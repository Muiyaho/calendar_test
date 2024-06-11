import tkinter as tk
from calendar_gui import CalendarGUI
from calendar_events import CalendarEvents

if __name__ == "__main__":
    root = tk.Tk()
    calendar_events = CalendarEvents()
    calendar_gui = CalendarGUI(root, calendar_events)
    root.mainloop()