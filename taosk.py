import tkinter as tk
from tkinter import messagebox
import json
import sqlite3
from datetime import datetime
import requests
import Giaodienchinh  

EVENTS_FILE = 'events.json'
DB_FILE = 'events.db'
FLASK_API_URL = "http://localhost:5000/events"  

# 🆕 Hàm chuyển đổi ngày từ DD/MM/YYYY sang YYYY-MM-DD
def convert_date_format(date_str):
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None  # Trả về None nếu ngày không hợp lệ

def check_connection_to_localhost():
    try:
        response = requests.get(FLASK_API_URL)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def save_event():
    if not check_connection_to_localhost():
        messagebox.showerror("Lỗi", "Không thể kết nối với localhost. Vui lòng kiểm tra kết nối mạng hoặc khởi động lại Flask server.")
        return

    event_name = entry_name.get()
    event_date = entry_date.get()
    event_time = entry_time.get()
    event_location = entry_location.get()
    event_description = text_description.get("1.0", tk.END).strip()

    if not event_name or not event_date or not event_time:
        messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin sự kiện!")
        return

    # 🔄 **Chuyển đổi định dạng ngày trước khi lưu**
    converted_date = convert_date_format(event_date)
    if not converted_date:
        messagebox.showerror("Lỗi", "Ngày không hợp lệ! Vui lòng nhập đúng định dạng dd/mm/yyyy.")
        return

    if event_time == "24:00":
        event_time = "00:00"  
    else:
        try:
            datetime.strptime(event_time, "%H:%M")
        except ValueError:
            messagebox.showerror("Lỗi", "Giờ không hợp lệ! Vui lòng nhập đúng định dạng hh:mm.")
            return

    if event_location == "":
        event_location = "Địa điểm trống"

    event_data = {
        "Tên sự kiện": event_name,
        "Ngày": converted_date,  # 🆕 Dùng ngày đã chuyển đổi
        "Thời gian": event_time,
        "Mô tả": event_description,
        "Địa điểm": event_location
    }

    save_event_to_db(event_name, converted_date, event_time, event_location, event_description)

    try:
        with open(EVENTS_FILE, "r", encoding="utf-8") as f:
            events = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        events = []

    events.append(event_data)

    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=4)

    messagebox.showinfo("Thành công", "Sự kiện đã được lưu vào hệ thống!")
    root.destroy()
    Giaodienchinh.open_main_window()

def save_event_to_db(event_name, event_date, event_time, event_location, event_description):
    """ Lưu sự kiện mới vào database SQLite """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO event (title, date, time, location, description) VALUES (?, ?, ?, ?, ?)",
            (event_name, event_date, event_time, event_location, event_description)
        )
        conn.commit()
        print(f"✅ Sự kiện '{event_name}' đã được lưu vào database!")

def open_create_event_window():
    if not check_connection_to_localhost():
        messagebox.showerror("Lỗi kết nối", "Không thể kết nối đến localhost. Hãy chắc chắn rằng Flask server đang chạy.")
        return

    global root, entry_name, entry_date, entry_time, text_description, entry_location

    root = tk.Tk()
    root.title("Tạo Sự Kiện")
    root.geometry("700x500+400+100")
    root.resizable(False, False)

    tk.Label(root, text="Tạo Sự Kiện", font=("Arial", 16, "bold")).pack(pady=10)

    frame = tk.Frame(root)
    frame.pack(pady=5)

    tk.Label(frame, text="Tên sự kiện:", anchor="w").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    entry_name = tk.Entry(frame, width=30)
    entry_name.grid(row=0, column=1, padx=5, pady=7)

    tk.Label(frame, text="Ngày (dd/mm/yyyy):", anchor="w").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    entry_date = tk.Entry(frame, width=30)
    entry_date.grid(row=1, column=1, padx=5, pady=7)

    tk.Label(frame, text="Thời gian (hh:mm):", anchor="w").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    entry_time = tk.Entry(frame, width=30)
    entry_time.grid(row=2, column=1, padx=5, pady=7)

    tk.Label(frame, text="Địa điểm:", anchor="w").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    entry_location = tk.Entry(frame, width=30)
    entry_location.grid(row=3, column=1, padx=5, pady=7)

    tk.Label(root, text="Mô tả sự kiện:", anchor="w").pack(pady=5)
    text_description = tk.Text(root, width=40, height=5)
    text_description.pack(padx=10, pady=7)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    btn_save = tk.Button(button_frame, text="Lưu", width=12, command=save_event)
    btn_save.grid(row=0, column=0, padx=5, pady=5)

    btn_back = tk.Button(button_frame, text="Quay lại", width=12,
                         command=lambda: [root.destroy(), Giaodienchinh.open_main_window()])
    btn_back.grid(row=0, column=1, padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    open_create_event_window()
