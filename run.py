from daily_Message import daily_Message
import schedule
import time

schedule.every().day.at("17:40").do(daily_Message.send_email)

while True:
    print("Running")
    schedule.run_pending()
    time.sleep(1)
