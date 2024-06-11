import json
from datetime import datetime, date

class CalendarEvents:
    def __init__(self, data_file="calendar_events.json"):
        self.data_file = data_file
        self.events = {}
        self.holidays = {}
        self.load_events()

    def load_events(self):
        if not self.data_file or not isinstance(self.data_file, str):
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                events_loaded = data.get("events", {})
                holidays_loaded = data.get("holidays", {})
                self.events = {datetime.strptime(k, "%Y-%m-%d").date(): v for k, v in events_loaded.items()}
                self.holidays = {datetime.strptime(k, "%Y-%m-%d").date(): v for k, v in holidays_loaded.items()}
        except FileNotFoundError:
            self.events = {}
            self.holidays = {}

    def save_events(self):
        events_to_save = {str(k): v for k, v in self.events.items()}
        holidays_to_save = {str(k): v for k, v in self.holidays.items()}
        data = {"events": events_to_save, "holidays": holidays_to_save}
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_event(self, event_date, title, description, alarm, alarm_time, alarm_type, debug):
        if title:
            event_data = {"title": title, "description": description.strip(), "alarm": alarm, "alarm_time": alarm_time, "alarm_type": alarm_type, "debug": debug}
            if event_date not in self.events:
                self.events[event_date] = []
            self.events[event_date].append(event_data)
            self.save_events()

    def update_event(self, event_date, old_event, title, description, alarm, alarm_time, alarm_type, debug):
        if title and event_date in self.events and old_event in self.events[event_date]:
            self.events[event_date].remove(old_event)
            self.add_event(event_date, title, description, alarm, alarm_time, alarm_type, debug)

    def delete_event(self, event_date, event_to_delete):
        if event_date in self.events and event_to_delete in self.events[event_date]:
            self.events[event_date].remove(event_to_delete)
            self.save_events()

    def reset_events(self):
        self.events = {k: [{"title": v, "description": "", "alarm": False, "alarm_time": None, "alarm_type": None, "debug": False}] for k, v in self.holidays.items()}
        self.save_events()