from daily_Message import daily_Message
import schedule
import time

from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

schedule.every().day.at("18:30").do(daily_Message.send_email)

while True:
    print("Running")
    schedule.run_pending()
    time.sleep(1)
