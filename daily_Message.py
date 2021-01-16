#!/usr/bin/env python
# coding: utf-8

import os
import requests
import html
import datetime
import smtplib
from email.mime.text import MIMEText

class daily_Message():

    def cut_data(line):
        if "\t" in line:
            line = line.replace("\t","")
        line_list  = line.split("<")
        return line_list[0]

    def clear_data(line):
        no_letter = True
        if "</nobr" in line:
            line = line.replace("</nobr","")
        if "&nbsp;&nbsp;&nbsp" in line:
            line = line.replace("&nbsp;&nbsp;&nbsp;", "")
        if "&nbsp;&nbsp" in line:
            line = line.replace("&nbsp;&nbsp;", "")
        line = html.unescape(line)
        if "..." in line:
            line = line.replace("...","")
        if ".." in line:
            line = line.replace("..","")
        return line

    def change_umlaute(text):
        if "ä" in text:
            text = text.replace("ä","ae")
        if "Ä" in text:
            text = text.replace("Ä", "AE")
        if "ü" in text:
            text = text.replace("ü", "ue")
        if "Ü" in text:
            text = text.replace("Ü", "Ue")
        if "ö" in text:
            text = text.replace("ö","oe")
        if "Ö" in text:
            text = text.replace("Ö", "Oe")
        if "ß" in text:
            text = text.replace("ß", "ss")
        text = text.replace(u'\xa0'," ")
        return text

    def send_email():
        # login data
        user = os.environ["GMAIL_USER"]
        pwd = os.environ["GMAIL_PWD"]

        # getting email data
        subject = "Daily Message"
        mail_from = os.environ["GMAIL_USER"]
        rcpt_to = os.environ["GMAIL_RCPT"]
        mail_text = daily_Message.create_message()
        mail_text = daily_Message.change_umlaute(mail_text)
        data = f'From:{mail_from}\nTo:{rcpt_to}\nSubject:{subject}\n\n{mail_text}'

        # creating smtp connection
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(user,pwd)
        server.sendmail(mail_from, rcpt_to, data)
        server.quit()
        print("e-mail send")

    def get_weather():
        # Getting Weather Information using OpenWeatherMap

        # Setting up the Request
        api_key = os.environ["OWM_API_KEY"]
        lat = 51.348
        lon = 7.5563
        url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=de'

        # Request
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json"
            }
        )

        # Process Response
        if response.ok is True:
            response_json = response.json()

            # Processing Data
            temperatur = str(response_json["current"]["temp"])
            temperatur_fells_like = str(response_json["current"]["feels_like"])
            temperatur_daily_day = str(response_json["daily"][0]["temp"]["day"])
            temperatur_daily_night = str(response_json["daily"][0]["temp"]["night"])
            temperatur_daily_eve = str(response_json["daily"][0]["temp"]["eve"])
            temperatur_daily_morn = str(response_json["daily"][0]["temp"]["morn"])
            temperatur_daily_day_fells_like = str(response_json["daily"][0]["feels_like"]["day"])
            temperatur_daily_night_fells_like  = str(response_json["daily"][0]["feels_like"]["night"])
            temperatur_daily_eve_fells_like  = str(response_json["daily"][0]["feels_like"]["eve"])
            temperatur_daily_morn_fells_like  = str(response_json["daily"][0]["feels_like"]["morn"])
            weather_main_description = str(response_json["daily"][0]["weather"][0]["description"])
            alerts = ""
            try:
                alerts = str(response_json["alerts"][0]["description"])
            except KeyError:
                alerts = "Keine Informationen"

            # Creating Weather String
            weather_string = f'***Wetter:***\n' \
                             f'Aktuell:  {temperatur} Gefühlt: {temperatur_fells_like}\n' \
                             f'Morgens:  {temperatur_daily_morn} Gefühlt: {temperatur_daily_morn_fells_like}\n' \
                             f'Tagsüber: {temperatur_daily_day} Gefühlt: {temperatur_daily_day_fells_like}\n' \
                             f'Abends:   {temperatur_daily_eve} Gefühlt: {temperatur_daily_eve_fells_like}\n' \
                             f'Nachts:   {temperatur_daily_night} Gefühlt: {temperatur_daily_night_fells_like}\n' \
                             f'Wetter: {weather_main_description}\n' \
                             f'Information: {alerts}'
            return weather_string
        else:
            return "Error"

    def get_special_day():
        # Getting day information using https://welcher-tag-ist-heute.org/
        response = requests.get("https://welcher-tag-ist-heute.org/")
        if response.ok:
            # Setting up Variables
            html_doc = response.text.splitlines()
            holiday = []
            special_day = []
            week_number = "0"
            sunrise = ""
            sunset = ""
            counter = 0

            # Processing Response
            for line in html_doc:
                if '<a href="feiertage/' in line:
                    day = daily_Message.cut_data(html_doc[counter + 1])
                    holiday.append(day)
                if '<a href="aktionstage/' in line:
                    day = daily_Message.cut_data(html_doc[counter + 1])
                    special_day.append(day)
                counter += 1

            day_string = "Heute ist der " + datetime.datetime.now().strftime("%d.%m.%Y") + ".\n"
            for day in holiday:
                day_string += day + "\n"
            for day in special_day:
                day_string += day + "\n"
            return day_string
        else:
            return "Error"

    def get_news():
        # Getting news using https://www.ard-text.de/
        news = "***News:***\n"
        # Getting multiple Pages
        pages = [101,102,103]
        for page in pages:
            response = requests.get(f'https://www.ard-text.de/{page}')
            if response.ok:
                # Setting up variables
                html_doc = response.text.splitlines()
                counter = 0
                text_lines = False
                first_encounter = True
                # Processing Response
                for line in html_doc:
                    if text_lines and counter > 2:
                        # end of news lines
                        if line == "<div><span class='fgw bgb' style='width:0px;'><nobr></nobr></span><span class='fgbl bgb' style='width:390px;'><nobr><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'><img src='./img/g1b2c.gif'></nobr></span></div>":
                            text_lines = False
                        else:
                            text_html = line.split(">")
                            # Getting news
                            if len(text_html) == 11:
                                news += "\n"
                                result = daily_Message.clear_data(text_html[7])
                                news += result + "\n"
                            if len(text_html) == 7:
                                result = daily_Message.clear_data(text_html[3])
                                news += result
                            if len(text_html) == 13:
                                result = daily_Message.clear_data(text_html[3])
                                news += result + "\n"
                                number_string = text_html[7]
                                a = number_string[len(number_string)-4]
                                b = number_string[len(number_string)-3]
                                c = number_string[len(number_string)-2]
                                url = "https://www.ard-text.de/mobil/" + a + b + c
                                news += url + "\n"
                            if len(text_html) == 21:
                                result = daily_Message.clear_data(text_html[7])
                                news += result + "\n"
                                number_string = text_html[16]
                                a = number_string[0]
                                b = number_string[1]
                                c = number_string[2]
                                url = "https://www.ard-text.de/mobil/" + a + b + c
                                news += url + "\n"
                    # Start of news lines
                    if 'ardtext_classic' in line and first_encounter:
                        text_lines = True
                        first_encounter = False
                    counter += 1
            else:
                return "Error"
        return news

    def create_message():
        weather = daily_Message.get_weather()
        day = daily_Message.get_special_day()
        news = daily_Message.get_news()

        message = "Guten Morgen " + os.environ["USER_NAME"] + "\n\n"
        message += day + "\n"
        message += news + "\n"
        message += weather + "\n"

        return message
