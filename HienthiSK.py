import tkinter as tk
from tkinter import messagebox
import json
import os

EVENTS_FILE = "events.json"

def load_events():
    if not os.path.exists(EVENTS_FILE):
        return []
    
    try:
        with open(EVENTS_FILE, "r", encoding="utf-8") as file:
            events = json.load(file)
            return events if isinstance(events, list) else []
    except json.JSONDecodeError:
        return []
    
def go_back(event_window, main_window):
    event_window.destroy()
    main_window.destroy()
    import Giaodienchinh
    Giaodienchinh.open_main_window()

def display_events(main_window):
    events = load_events()

    if not events:
        messagebox.showinfo("Thông báo", "Chưa có sự kiện nào được lưu!")
        return

    event_window = tk.Tk()
    event_window.title("Danh sách sự kiện")
    event_window.geometry("700x500+400+100")

    tk.Label(event_window, text="Danh sách Sự Kiện", font=("Arial", 14, "bold")).pack(pady=5)

    listbox = tk.Listbox(event_window, width=80, height=15)
    listbox.pack(pady=10)

    for event in events:
        # Kiểm tra xem sự kiện có key "id" không
        if 'id' in event:
            listbox.insert(tk.END, f"{event['id']}.{event['Tên sự kiện']} - {event['Ngày']} {event['Thời gian']} - {event['Địa điểm']}")
        else:
            listbox.insert(tk.END, f"{event['Tên sự kiện']} - {event['Ngày']} {event['Thời gian']} - {event['Địa điểm']}")


    btn_back = tk.Button(event_window, text="Quay lại",font=("Times New Roman", 13), command=lambda:go_back(event_window, main_window))
    btn_back.pack(pady=15)


    event_window.mainloop()

if __name__ == "__main__":
    display_events()



