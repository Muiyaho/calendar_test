import time
from datetime import datetime
import threading
from win10toast import ToastNotifier

toaster = ToastNotifier()

def show_notification(title, message):
    toaster.show_toast(title, message, duration=10)

def check_alarms(calendar_events):
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_date = now.date()

        for event_date, events in calendar_events.events.items():
            for event in events:
                if event.get("alarm", False):
                    alarm_type = event.get("alarm_type", "once")
                    alarm_time = event.get("alarm_time", "")

                    if alarm_type == "daily" and alarm_time == current_time:
                        message = f"{event['title']} 작업을 할 시간입니다."
                        show_notification("알림", message)
                    elif alarm_type == "once" and alarm_time == current_time and event_date == current_date:
                        message = f"{event['title']} 작업을 할 시간입니다.\n - 작업 내용 : {event['description']}"
                        show_notification("알림", message)

        time.sleep(60)  # 1분마다 확인

def start_alarm_checker(calendar_events):
    alarm_thread = threading.Thread(target=check_alarms, args=(calendar_events,), daemon=True)
    alarm_thread.start()