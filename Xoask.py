import tkinter as tk
from tkinter import messagebox
import json
import sqlite3  # 🆕 Import SQLite để xóa sự kiện khỏi database

EVENTS_FILE = "events.json"
DB_FILE = "events.db"  # 🆕 Đường dẫn database

def load_events():
    try:
        with open(EVENTS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_events(events):
    with open(EVENTS_FILE, "w", encoding="utf-8") as file:
        json.dump(events, file, indent=4, ensure_ascii=False)

# 🆕 Hàm xóa sự kiện khỏi database
def delete_event_from_db(event_name):
    """ Xóa sự kiện khỏi database SQLite """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM event WHERE title=?", (event_name,))
        conn.commit()
        print(f"🗑️ Đã xóa sự kiện: {event_name} khỏi database!")

# 🆕 Hàm xóa sự kiện cả trong JSON và database
def delete_event():
    selected_index = listbox.curselection()
    if not selected_index:
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn một sự kiện để xóa")
        return
    
    index = selected_index[0]
    event_name = events[index]["Tên sự kiện"]  # 🆕 Lấy tên sự kiện để xóa trong database

    # 🆕 Gọi hàm xóa sự kiện khỏi database
    delete_event_from_db(event_name)

    # 🔄 Xóa khỏi danh sách JSON
    del events[index]
    save_events(events)
    
    # 🔄 Cập nhật lại danh sách sự kiện
    refresh_listbox()
    
    messagebox.showinfo("Thông báo", "Sự kiện đã được xóa thành công")

def on_select(event):
    selected_index = listbox.curselection()
    if not selected_index:
        return
    
    index = selected_index[0]
    selected_event = events[index]
    entry_name.delete(0, tk.END)
    entry_name.insert(0, selected_event["Tên sự kiện"])
    entry_date.delete(0, tk.END)
    entry_date.insert(0, selected_event["Ngày"])
    entry_time.delete(0, tk.END)
    entry_time.insert(0, selected_event["Thời gian"])
    entry_description.delete(0, tk.END)
    entry_description.insert(0, selected_event["Mô tả"])

def login():
    import Giaodienchinh
    root.destroy()
    Giaodienchinh.open_main_window()

def refresh_listbox():
    listbox.delete(0, tk.END)
    for event in events:
        listbox.insert(tk.END, event["Tên sự kiện"])

events = load_events()

root = tk.Tk()
root.title("Chỉnh sửa Sự kiện")
root.geometry("700x500+400+100")

listbox = tk.Listbox(root, height=10)
listbox.pack(pady=10, fill=tk.BOTH, expand=True)
listbox.bind("<<ListboxSelect>>", on_select)
refresh_listbox()

tk.Label(root, text="Tên Sự Kiện:").pack()
entry_name = tk.Entry(root)
entry_name.pack()

tk.Label(root, text="Ngày (dd/mm/yyyy):").pack()
entry_date = tk.Entry(root)
entry_date.pack()

tk.Label(root, text="Thời Gian:").pack()
entry_time = tk.Entry(root)
entry_time.pack()

tk.Label(root, text="Mô Tả:").pack()
entry_description = tk.Entry(root)
entry_description.pack()

btn_delete = tk.Button(root, text="Xóa Sự Kiện", command=delete_event)
btn_delete.pack(pady=5)

btn_dangxuat = tk.Button(root, text="Quay lại", command=lambda: login())
btn_dangxuat.pack(pady=8)

root.mainloop()
