import tkinter as tk
from tkinter import simpledialog, Menu, Toplevel, Label, Entry, Button, Text, filedialog, messagebox
import calendar
from datetime import datetime, date
import holidays
import json
import os

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.today = datetime.today()
        self.year = self.today.year
        self.month = self.today.month
        self.events = {}
        self.holidays = {}

        self.data_file = "calendar_events.json"
        self.load_events()

        self.root.title("캘린더 프로그램")
        self.root.geometry("800x600")
        self.create_menu()
        self.create_header()
        self.create_calendar()

    def create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="일정 불러오기", command=self.load_events_dialog)
        file_menu.add_command(label="일정 다른 이름으로 저장하기", command=self.save_events_as)
        file_menu.add_command(label="일정 초기화", command=self.reset_events)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.root.quit)

        menubar.add_cascade(label="파일", menu=file_menu)

    def create_header(self):
        header_frame = tk.Frame(self.root)
        header_frame.grid(row=0, column=0, columnspan=7)

        self.prev_button = tk.Button(header_frame, text="<", command=self.prev_month)
        self.prev_button.pack(side="left")

        self.next_button = tk.Button(header_frame, text=">", command=self.next_month)
        self.next_button.pack(side="right")

        self.today_button = tk.Button(header_frame, text="오늘", command=self.go_to_today)
        self.today_button.pack(side="left")

        self.month_label = tk.Label(header_frame, text="", font=("Helvetica", 16))
        self.month_label.pack(side="left", fill="x", expand=True)

        self.update_month_label()

    def create_calendar(self):
        self.clear_calendar()

        cal = calendar.Calendar(firstweekday=6)  # Sunday is considered as the first day of the week
        month_days = cal.monthdayscalendar(self.year, self.month)
        self.korean_holidays = holidays.KR(years=self.year)

        days_of_week = ["일", "월", "화", "수", "목", "금", "토"]
        for col, day in enumerate(days_of_week):
            day_label = tk.Label(self.root, text=day, font=("Helvetica", 12))
            day_label.grid(row=1, column=col)

        for row, week in enumerate(month_days):
            for col, day in enumerate(week):
                if day == 0:
                    continue

                current_date = date(self.year, self.month, day)
                if current_date not in self.events:
                    self.events[current_date] = []

                frame = tk.Frame(self.root, borderwidth=1, relief="solid")
                frame.grid(row=row + 2, column=col, sticky="nsew")

                if current_date == self.today.date():
                    bg_color = "#FFD700"  # 오늘 날짜 배경색
                else:
                    bg_color = "#FFFFFF"  # 기본 배경색

                fg_color = "black"  # 기본 글자색

                if col == 0:
                    bg_color = "#FFC0CB"  # 일요일 배경색
                    fg_color = "red"  # 일요일 글자색
                elif col == 6:
                    bg_color = "#ADD8E6"  # 토요일 배경색
                    fg_color = "red"  # 토요일 글자색

                if current_date in self.korean_holidays:
                    fg_color = "red"  # 공휴일 글자색
                    holiday_name = self.korean_holidays.get(current_date)
                    if current_date not in self.holidays:
                        self.holidays[current_date] = holiday_name
                    if holiday_name not in self.events[current_date]:
                        self.events[current_date].insert(0, holiday_name)

                frame.configure(bg=bg_color)
                day_label = tk.Label(frame, text=str(day), bg=bg_color, fg=fg_color)
                day_label.pack(anchor="nw")

                event_list = tk.Listbox(frame)
                event_list.pack(fill="both", expand=True)
                event_list.bind("<Button-3>", lambda e, date=current_date, el=event_list: self.show_context_menu(e, date, el))
                event_list.bind("<Double-Button-1>", lambda e, date=current_date, el=event_list: self.show_event_detail(e, date, el))

                self.update_events(current_date, event_list)

        for col in range(7):
            self.root.grid_columnconfigure(col, weight=1)
        for row in range(2, 8):  # Adjusted range to prevent the header row from being resized
            self.root.grid_rowconfigure(row, weight=1)

    def clear_calendar(self):
        for widget in self.root.grid_slaves():
            if int(widget.grid_info()["row"]) > 1:  # Ensure header row is not cleared
                widget.grid_forget()

    def update_month_label(self):
        self.month_label.config(text=f"{self.year}년 {self.month}월")

    def prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.update_month_label()
        self.create_calendar()

    def next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.update_month_label()
        self.create_calendar()

    def go_to_today(self):
        self.year = self.today.year
        self.month = self.today.month
        self.update_month_label()
        self.create_calendar()

    def show_context_menu(self, event, date, event_list):
        context_menu = Menu(self.root, tearoff=0)
        context_menu.add_command(label="일정 추가", command=lambda: self.open_add_event_popup(date))
        if event_list.curselection() and event_list.get(event_list.curselection()) not in self.holidays.values():
            context_menu.add_command(label="일정 삭제", command=lambda: self.delete_event(date, event_list))
        context_menu.post(event.x_root, event.y_root)

    def open_add_event_popup(self, event_date, event=None):
        popup = Toplevel(self.root)
        popup.title("일정 추가" if event is None else "일정 보기")
        popup.geometry("320x240")

        Label(popup, text="제목:").pack(pady=5)
        title_entry = Entry(popup, width=40)
        title_entry.pack(pady=5)
        title_entry.insert(0, event.split(": ")[0] if event else "")

        Label(popup, text="설명:").pack(pady=5)
        description_entry = Text(popup, width=40, height=5)
        description_entry.pack(pady=5)

        if event and len(event.split(": ")) > 1:
            description_entry.insert("1.0", event.split(": ")[1])
        else:
            description_entry.insert("1.0", "")

        if event:
            title_entry.config(state="disabled")
            description_entry.config(state="disabled")
        else:
            Button(popup, text="추가", command=lambda: self.add_event(event_date, title_entry.get(), description_entry.get("1.0", tk.END), popup)).pack(pady=20)

    def add_event(self, event_date, title, description, popup):
        if title:
            self.events[event_date].append(title)
            self.save_events()
            self.update_calendar()
            popup.destroy()

    def delete_event(self, event_date, event_list):
        selected_index = event_list.curselection()
        if selected_index:
            event_to_delete = event_list.get(selected_index)
            if event_to_delete not in self.holidays.values():
                self.events[event_date].remove(event_to_delete)
                self.save_events()
                self.update_calendar()

    def show_event_detail(self, event, event_date, event_list):
        selected_index = event_list.curselection()
        if selected_index:
            event_detail = event_list.get(selected_index)
            self.open_add_event_popup(event_date, event_detail)

    def update_events(self, event_date, event_list):
        event_list.delete(0, tk.END)
        for event in self.events.get(event_date, []):
            event_list.insert(tk.END, event)

    def update_calendar(self):
        cal = calendar.Calendar(firstweekday=6)
        month_days = cal.monthdayscalendar(self.year, self.month)

        for row, week in enumerate(month_days):
            for col, day in enumerate(week):
                if day == 0:
                    continue

                current_date = date(self.year, self.month, day)
                for widget in self.root.grid_slaves():
                    if int(widget.grid_info()["row"]) == row + 2 and int(widget.grid_info()["column"]) == col:
                        event_list = widget.winfo_children()[-1]
                        self.update_events(current_date, event_list)

    def save_events(self):
        events_to_save = {str(k): v for k, v in self.events.items()}
        holidays_to_save = {str(k): v for k, v in self.holidays.items()}
        data = {"events": events_to_save, "holidays": holidays_to_save}
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def save_events_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            events_to_save = {str(k): v for k, v in self.events.items()}
            holidays_to_save = {str(k): v for k, v in self.holidays.items()}
            data = {"events": events_to_save, "holidays": holidays_to_save}
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    def load_events(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                events_loaded = data.get("events", {})
                holidays_loaded = data.get("holidays", {})
                self.events = {datetime.strptime(k, "%Y-%m-%d").date(): v for k, v in events_loaded.items()}
                self.holidays = {datetime.strptime(k, "%Y-%m-%d").date(): v for k, v in holidays_loaded.items()}

    def load_events_dialog(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                events_loaded = data.get("events", {})
                holidays_loaded = data.get("holidays", {})
                self.events = {datetime.strptime(k, "%Y-%m-%d").date(): v for k, v in events_loaded.items()}
                self.holidays = {datetime.strptime(k, "%Y-%m-%d").date(): v for k, v in holidays_loaded.items()}
            self.update_calendar()

    def reset_events(self):
        if messagebox.askyesno("초기화 확인", "정말로 모든 일정을 초기화하시겠습니까?"):
            self.events = {k: [v] for k, v in self.holidays.items()}
            self.save_events()
            self.update_calendar()

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()