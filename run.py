from daily_Message import daily_Message
import schedule
import time

schedule.every().day.at("06:00").do(daily_Message.send_email)

while True:
    print("Running!")
    schedule.run_pending()
    time.sleep(1)
