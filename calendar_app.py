import tkinter as tk
import calendar
from datetime import datetime, date
import holidays

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.today = datetime.today()
        self.year = self.today.year
        self.month = self.today.month

        self.root.title("캘린더 프로그램")
        self.create_header()
        self.create_calendar()

    def create_header(self):
        header_frame = tk.Frame(self.root)
        header_frame.grid(row=0, column=0, columnspan=7)

        self.prev_button = tk.Button(header_frame, text="<", command=self.prev_month)
        self.prev_button.pack(side="left")

        self.next_button = tk.Button(header_frame, text=">", command=self.next_month)
        self.next_button.pack(side="right")

        self.month_label = tk.Label(header_frame, text="", font=("Helvetica", 16))
        self.month_label.pack(side="left", fill="x", expand=True)

        self.update_month_label()

    def create_calendar(self):
        self.clear_calendar()

        cal = calendar.Calendar()
        month_days = cal.monthdayscalendar(self.year, self.month)
        korean_holidays = holidays.KR(years=self.year)

        days_of_week = ["일", "월", "화", "수", "목", "금", "토"]
        for col, day in enumerate(days_of_week):
            day_label = tk.Label(self.root, text=day, font=("Helvetica", 12))
            day_label.grid(row=1, column=col)

        for row, week in enumerate(month_days):
            for col, day in enumerate(week):
                if day == 0:
                    continue

                frame = tk.Frame(self.root, borderwidth=1, relief="solid")
                frame.grid(row=row+2, column=col, sticky="nsew")

                bg_color = "#FFFFFF"  # 기본 배경색
                fg_color = "black"  # 기본 글자색

                if col == 0:
                    bg_color = "#FFC0CB"  # 일요일 배경색
                    fg_color = "red"  # 일요일 글자색
                elif col == 6:
                    bg_color = "#ADD8E6"  # 토요일 배경색
                    fg_color = "red"  # 토요일 글자색

                current_date = date(self.year, self.month, day)
                if current_date in korean_holidays:
                    fg_color = "red"  # 공휴일 글자색

                frame.configure(bg=bg_color)
                day_label = tk.Label(frame, text=str(day), bg=bg_color, fg=fg_color)
                day_label.pack(anchor="nw")

                text_var = tk.StringVar()
                entry = tk.Entry(frame, textvariable=text_var)
                entry.pack(fill="both", expand=True)

        for col in range(7):
            self.root.grid_columnconfigure(col, weight=1)
        for row in range(8):
            self.root.grid_rowconfigure(row, weight=1)

    def clear_calendar(self):
        for widget in self.root.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
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

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()