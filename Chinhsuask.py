import tkinter as tk
from tkinter import messagebox
import json
import os
import sqlite3  # 🆕 Thêm SQLite để cập nhật database
from datetime import datetime  # 🆕 Import datetime để sử dụng trong convert_date_format
import requests
import Giaodienchinh  # Đảm bảo file này có và hàm open_main_window hoạt động

FILE_NAME = "events.json"
DB_FILE = "events.db"
FLASK_API_URL = "http://localhost:5000/events"  # URL để kiểm tra API Flask

def check_connection_to_localhost():
    try:
        response = requests.get(FLASK_API_URL)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False

def load_events():
    if not os.path.exists(FILE_NAME):
        return []
    with open(FILE_NAME, "r", encoding="utf-8") as file:
        return json.load(file)

def save_events(events):
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(events, file, ensure_ascii=False, indent=4)

def convert_date_format(date_str):
    """ Chuyển đổi ngày từ 'DD/MM/YYYY' sang 'YYYY-MM-DD' nếu cần """
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return date_str  # Nếu ngày đã đúng định dạng hoặc lỗi, giữ nguyên


def update_event_in_db(event_name, new_date, new_time, new_location, new_desc):
    """ Cập nhật sự kiện trong database SQLite, đảm bảo ngày đúng định dạng """
    
    # 🔄 Chuyển đổi định dạng ngày trước khi cập nhật
    converted_date = convert_date_format(new_date)
    if not converted_date:
        print(f"❌ Lỗi: Ngày không hợp lệ ({new_date}) trong sự kiện '{event_name}'")
        return
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE event SET date=?, time=?, location=?, description=? WHERE title=?",
            (converted_date, new_time, new_location, new_desc, event_name)
        )
        conn.commit()
        print(f"✅ Đã cập nhật sự kiện '{event_name}' trong database!")


# 🆕 Hàm cập nhật cả trong JSON và database
def update_event():
    if not check_connection_to_localhost():
        messagebox.showerror("Lỗi", "Không thể kết nối với localhost. Vui lòng kiểm tra kết nối mạng hoặc khởi động lại Flask server.")
        return
    
    selected_index = event_listbox.curselection()
    if not selected_index:
        messagebox.showerror("Lỗi", "Vui lòng chọn một sự kiện để chỉnh sửa!")
        return
    
    index = selected_index[0]
    events = load_events()
    
    # 🔄 **Lấy thông tin mới từ các ô nhập**
    event_name = entry_name.get()
    new_date = entry_date.get()
    new_time = entry_time.get()
    new_location = entry_location.get()
    new_desc = entry_desc.get("1.0", tk.END).strip()

    # 🔄 **Cập nhật sự kiện trong database**
    update_event_in_db(event_name, new_date, new_time, new_location, new_desc)

    # 🔄 **Cập nhật trong JSON**
    events[index]["Tên sự kiện"] = event_name
    events[index]["Ngày"] = new_date
    events[index]["Thời gian"] = new_time
    events[index]["Địa điểm"] = new_location
    events[index]["Mô tả"] = new_desc
    
    save_events(events)

    messagebox.showinfo("Thành công", "Sự kiện đã được cập nhật!")
    refresh_event_list()

def refresh_event_list():
    event_listbox.delete(0, tk.END)
    events = load_events()
    for event in events:
        event_listbox.insert(tk.END, f"{event['Tên sự kiện']} - {event['Ngày']} - {event['Thời gian']} - {event['Địa điểm']}")

def load_selected_event(event):
    selected_index = event_listbox.curselection()
    if not selected_index:
        return
    
    index = selected_index[0]
    event = load_events()[index]
    entry_name.delete(0, tk.END)
    entry_name.insert(0, event["Tên sự kiện"])
    entry_date.delete(0, tk.END)
    entry_date.insert(0, event["Ngày"])
    entry_time.delete(0, tk.END)
    entry_time.insert(0, event["Thời gian"])
    entry_location.delete(0, tk.END)
    entry_location.insert(0, event["Địa điểm"])
    entry_desc.delete("1.0", tk.END)
    entry_desc.insert("1.0", event["Mô tả"])

root = tk.Tk()
root.title("Chỉnh Sửa Sự Kiện")
root.geometry("700x500+400+100")

main_frame = tk.Frame(root, padx=20, pady=10)
main_frame.pack(fill="both", expand=True)

tk.Label(main_frame, text="Danh sách sự kiện:", font=("Arial", 15, "bold")).grid(row=0, column=1, columnspan=2)
event_listbox = tk.Listbox(main_frame, width=60, height=7)
event_listbox.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
event_listbox.bind("<<ListboxSelect>>", load_selected_event)
refresh_event_list()

fields = [("Tên Sự Kiện:", 2), ("Ngày (DD/MM/YYYY):", 3), ("Thời Gian (HH:MM):", 4), ("Địa điểm:", 5), ("Mô Tả Sự Kiện:", 6)]
entries = {}

for text, row in fields:
    tk.Label(main_frame, text=text, font=("Arial", 10)).grid(row=row, column=0, padx=10, pady=5, sticky="w")
    if text == "Mô Tả Sự Kiện:":
        entry = tk.Text(main_frame, width=50, height=5)
    else:
        entry = tk.Entry(main_frame, width=50)
    
    entry.grid(row=row, column=1, padx=10, pady=5)
    entries[text] = entry

entry_name = entries["Tên Sự Kiện:"]
entry_date = entries["Ngày (DD/MM/YYYY):"]
entry_time = entries["Thời Gian (HH:MM):"]
entry_location = entries["Địa điểm:"]
entry_desc = entries["Mô Tả Sự Kiện:"]

btn_update = tk.Button(main_frame, text="Cập Nhật Sự Kiện", command=update_event, width=15)
btn_update.grid(row=7, column=1, pady=10, sticky="e", padx=10)

btn_quaylai = tk.Button(main_frame, text="Quay lại", width=15, command=lambda: [root.destroy(), Giaodienchinh.open_main_window()])
btn_quaylai.grid(row=8, column=1, pady=10, sticky="e", padx=10)

root.mainloop()
