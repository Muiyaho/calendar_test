import tkinter as tk
from tkinter import Menu, Toplevel, Label, Entry, Button, Text, Checkbutton, BooleanVar, filedialog, messagebox, \
    Spinbox, StringVar, OptionMenu
import calendar
from datetime import date
import holidays
from calendar_events import CalendarEvents
from calendar_notifications import start_alarm_checker


class CalendarGUI:
    def __init__(self, root, calendar_events):
        self.root = root
        self.today = date.today()
        self.year = self.today.year
        self.month = self.today.month
        self.calendar_events = calendar_events
        self.korean_holidays = holidays.KR(years=self.year)

        self.root.title("캘린더 프로그램")
        self.root.geometry("800x600")
        self.create_menu()
        self.create_header()
        self.create_calendar()
        start_alarm_checker(self.calendar_events)

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

        cal = calendar.Calendar(firstweekday=6)
        month_days = cal.monthdayscalendar(self.year, self.month)

        days_of_week = ["일", "월", "화", "수", "목", "금", "토"]
        for col, day in enumerate(days_of_week):
            day_label = tk.Label(self.root, text=day, font=("Helvetica", 12))
            day_label.grid(row=1, column=col)

        for row, week in enumerate(month_days):
            for col, day in enumerate(week):
                if day == 0:
                    continue

                current_date = date(self.year, self.month, day)
                if current_date not in self.calendar_events.events:
                    self.calendar_events.events[current_date] = []

                frame = tk.Frame(self.root, borderwidth=1, relief="solid")
                frame.grid(row=row + 2, column=col, sticky="nsew")

                if current_date == self.today:
                    bg_color = "#FFD700"
                else:
                    bg_color = "#FFFFFF"

                fg_color = "black"

                if col == 0:
                    bg_color = "#FFC0CB"
                    fg_color = "red"
                elif col == 6:
                    bg_color = "#ADD8E6"
                    fg_color = "red"

                if current_date in self.korean_holidays:
                    fg_color = "red"
                    holiday_name = self.korean_holidays.get(current_date)
                    if current_date not in self.calendar_events.holidays:
                        self.calendar_events.holidays[current_date] = holiday_name
                    if not any(
                            event.get("title") == holiday_name for event in self.calendar_events.events[current_date]):
                        self.calendar_events.events[current_date].insert(0, {"title": holiday_name, "description": "",
                                                                             "alarm": False, "alarm_time": None,
                                                                             "alarm_type": None, "debug": False})

                frame.configure(bg=bg_color)
                day_label = tk.Label(frame, text=str(day), bg=bg_color, fg=fg_color)
                day_label.pack(anchor="nw")

                event_list = tk.Listbox(frame)
                event_list.pack(fill="both", expand=True)
                event_list.bind("<Button-3>",
                                lambda e, date=current_date, el=event_list: self.show_context_menu(e, date, el))
                event_list.bind("<Double-Button-1>",
                                lambda e, date=current_date, el=event_list: self.show_event_detail(e, date, el))

                self.update_events(current_date, event_list)

        for col in range(7):
            self.root.grid_columnconfigure(col, weight=1)
        for row in range(2, 8):
            self.root.grid_rowconfigure(row, weight=1)

    def clear_calendar(self):
        for widget in self.root.grid_slaves():
            if int(widget.grid_info()["row"]) > 1:
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
        if event_list.curselection() and event_list.get(event_list.curselection()) not in [
            self.calendar_events.holidays.get(date)]:
            context_menu.add_command(label="일정 삭제", command=lambda: self.delete_event(date, event_list))
        context_menu.post(event.x_root, event.y_root)

    def open_add_event_popup(self, event_date, event=None):
        if event and event["title"] in self.calendar_events.holidays.values():
            messagebox.showinfo("알림", "공휴일은 수정할 수 없습니다.")
            return

        popup = Toplevel(self.root)
        popup.title("일정 추가" if event is None else "일정 보기")
        popup.geometry("400x350")

        Label(popup, text="제목:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        title_entry = Entry(popup, width=40)
        title_entry.grid(row=0, column=1, pady=5, padx=5)
        title_entry.insert(0, event["title"] if event else "")

        Label(popup, text="설명:").grid(row=1, column=0, pady=5, padx=5, sticky="nw")
        description_entry = Text(popup, width=40, height=5)
        description_entry.grid(row=1, column=1, pady=5, padx=5)
        description_entry.insert("1.0", event["description"] if event else "")

        alarm_var = BooleanVar()
        debug_var = BooleanVar()

        if event:
            alarm_var.set(event["alarm"])
            debug_var.set(event["debug"])

        alarm_check = Checkbutton(popup, text="알림 설정", variable=alarm_var,
                                  command=lambda: self.toggle_alarm_frame(alarm_var, alarm_frame, alarm_option_menu))
        alarm_check.grid(row=2, column=0, pady=5, padx=5, sticky="w")

        alarm_frame = tk.Frame(popup)
        alarm_frame.grid(row=3, column=0, columnspan=2, pady=5, padx=5)

        alarm_options = ["정기 알람", "시간대 선택"]
        alarm_type_var = StringVar(
            value=alarm_options[0] if not event else ("정기 알람" if event.get("alarm_type") == "daily" else "시간대 선택"))

        alarm_option_menu = OptionMenu(popup, alarm_type_var, *alarm_options)
        alarm_option_menu.grid(row=2, column=1, pady=5, padx=5, sticky="w")

        time_frame = tk.Frame(alarm_frame)
        time_frame.grid(row=1, column=0, columnspan=2, pady=5, padx=5)

        Label(time_frame, text="시간 설정:").grid(row=0, column=0, pady=5, padx=5, sticky="w")

        hour_spinbox = Spinbox(time_frame, from_=0, to=23, width=3)
        hour_spinbox.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        hour_spinbox.delete(0, "end")
        hour_spinbox.insert(0, "09" if not event else event.get("alarm_time", "").split(":")[0])

        Label(time_frame, text="시").grid(row=0, column=2, pady=5, padx=5, sticky="w")

        minute_spinbox = Spinbox(time_frame, from_=0, to=59, width=3)
        minute_spinbox.grid(row=0, column=3, pady=5, padx=5, sticky="w")
        minute_spinbox.delete(0, "end")
        minute_spinbox.insert(0, "00" if not event else event.get("alarm_time", "").split(":")[1])

        Label(time_frame, text="분").grid(row=0, column=4, pady=5, padx=5, sticky="w")

        if not alarm_var.get():
            alarm_frame.grid_remove()

        Button(popup, text="추가" if event is None else "수정",
               command=lambda: self.add_or_update_event(event_date, title_entry.get(),
                                                        description_entry.get("1.0", tk.END), alarm_var.get(),
                                                        alarm_type_var.get(), hour_spinbox.get(), minute_spinbox.get(),
                                                        debug_var.get(), event, popup)).grid(row=4, column=0,
                                                                                             columnspan=2, pady=20)

        #debug_check = Checkbutton(popup, text="디버그", variable=debug_var)
        #debug_check.grid(row=5, column=1, pady=5, padx=5, sticky="w")

    def toggle_alarm_frame(self, alarm_var, alarm_frame, alarm_option_menu):
        if alarm_var.get():
            alarm_option_menu.grid()
            alarm_frame.grid()
        else:
            alarm_option_menu.grid_remove()
            alarm_frame.grid_remove()

    def add_or_update_event(self, event_date, title, description, alarm, alarm_type, alarm_hour, alarm_minute, debug,
                            old_event, popup):
        alarm_time = f"{alarm_hour.zfill(2)}:{alarm_minute.zfill(2)}" if alarm else None
        alarm_type_str = "daily" if alarm_type == "정기 알람" else "once"
        if old_event:
            self.calendar_events.update_event(event_date, old_event, title, description, alarm, alarm_time,
                                              alarm_type_str, debug)
        else:
            self.calendar_events.add_event(event_date, title, description, alarm, alarm_time, alarm_type_str, debug)
        self.create_calendar()
        popup.destroy()

    def delete_event(self, event_date, event_list):
        selected_index = event_list.curselection()
        if selected_index:
            event_to_delete_title = event_list.get(selected_index)
            full_event = next(
                (event for event in self.calendar_events.events[event_date] if event["title"] == event_to_delete_title),
                None)
            if full_event and full_event["title"] not in self.calendar_events.holidays.values():
                self.calendar_events.delete_event(event_date, full_event)
                self.create_calendar()

    def show_event_detail(self, event, event_date, event_list):
        selected_index = event_list.curselection()
        if selected_index:
            event_detail = event_list.get(selected_index)
            full_event = next((ev for ev in self.calendar_events.events[event_date] if ev["title"] == event_detail), {})
            self.open_add_event_popup(event_date, full_event)

    def update_events(self, event_date, event_list):
        event_list.delete(0, tk.END)
        for event in self.calendar_events.events.get(event_date, []):
            if event["title"] in self.calendar_events.holidays.values():
                event_list.insert(tk.END, event["title"])
                event_list.itemconfig(tk.END, {'fg': 'red'})
            else:
                event_list.insert(tk.END, event["title"])

    def load_events_dialog(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            self.calendar_events.load_events(file_path)
            self.create_calendar()

    def save_events_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            self.calendar_events.save_events(file_path)

    def reset_events(self):
        if messagebox.askyesno("초기화 확인", "정말로 모든 일정을 초기화하시겠습니까?"):
            self.calendar_events.reset_events()
            self.create_calendar()