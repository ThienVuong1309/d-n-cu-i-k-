import json
import os
from DangNhap import create_login_window, login_success
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import time
import threading
class CustomProgressBar(tk.Frame):
    def __init__(self, master=None, width=200, height=20, **kwargs):
        super().__init__(master, **kwargs)
        
        # Thiết lập kích thước và màu sắc cho thanh tiến trình
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg="white", highlightthickness=0)
        self.canvas.pack()
        
        # Tạo một hình chữ nhật đại diện cho thanh tiến trình
        self.progress = self.canvas.create_rectangle(0, 0, 0, self.height, fill="blue")


        # Biến để theo dõi tiến trình hiện tại
        self.current_progress = 0


    def set_progress(self, value):
        # Xác định độ dài của thanh tiến trình dựa trên giá trị đầu vào
        width = self.width * (value / 100)
        self.canvas.coords(self.progress, 0, 0, width, self.height)


    def start_progress(self, duration):
        # Đặt lại tiến trình hiện tại về 0
        self.current_progress = 0
        # Tính toán bước tiến trình
        self.step = 100 / (duration * 340 / 100)  # mỗi 100ms sẽ tăng bao nhiêu %
        self.update_progress()


    def update_progress(self):
        if self.current_progress < 100:
            # Tăng tiến trình hiện tại và cập nhật giao diện
            self.current_progress += self.step
            self.set_progress(self.current_progress)
            # Gọi lại hàm này sau 100ms
            self.after(100, self.update_progress)
        else:
            self.set_progress(100)  # Đảm bảo thanh tiến trình đầy đủ 100%
            self.close_and_open_main_window()  # Đóng cửa sổ loading và mở giao diện chính

    def close_and_open_main_window(self):
        # Đóng cửa sổ hiện tại
        self.master.destroy()  # Hoặc self.destroy() nếu cần
        # Mở giao diện chính
        import Giaodienchinh
        Giaodienchinh.open_main_window()



def sync_json_to_db(json_path='events.json', db_path='events.db'):
    """ Cập nhật sự kiện từ JSON vào database nhưng không xóa sự kiện cũ """
    if not os.path.exists(json_path):
        print(f"❌ File '{json_path}' không tồn tại! Không có dữ liệu để đồng bộ.")
        return

    with open(json_path, "r", encoding="utf-8") as file:
        json_events = json.load(file)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Lấy danh sách tất cả sự kiện từ database
        cursor.execute("SELECT id, title, date FROM event")
        db_events = cursor.fetchall()

        json_event_list = [(event["Tên sự kiện"], event["Ngày"]) for event in json_events]
        db_event_titles = {event_title for _, event_title, _ in db_events}

        # 🔄 **Chỉ thêm sự kiện mới từ JSON vào database**
        for event in json_events:
            event_title = event["Tên sự kiện"]
            event_date = event["Ngày"]

            if event_title not in db_event_titles:  # Nếu sự kiện chưa có trong database
                cursor.execute(
                    "INSERT INTO event (title, date) VALUES (?, ?)",
                    (event_title, event_date)
                )
                print(f"✅ Thêm sự kiện mới vào database: {event_title}")

        conn.commit()
        print("✅ Đồng bộ hóa từ JSON vào database hoàn tất! Không xóa sự kiện cũ.")

def xoa_su_kien(title, db_path='events.db', json_path='events.json'):
    """ Xóa sự kiện khỏi database và `events.json` """

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # 🔴 **Xóa sự kiện khỏi database**
        cursor.execute("DELETE FROM event WHERE title=?", (title,))
        conn.commit()
        print(f"🗑️ Đã xóa sự kiện: {title} khỏi database!")

    # 🔄 **Xóa sự kiện khỏi `events.json`**
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as file:
            events = json.load(file)

        # Chỉ giữ lại những sự kiện KHÔNG phải sự kiện cần xóa
        events = [event for event in events if event["Tên sự kiện"] != title]

        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(events, file, ensure_ascii=False, indent=4)

        print(f"🗑️ Đã xóa sự kiện: {title} khỏi `events.json`!")

def convert_db_to_json(db_path='events.db', json_path='events.json'):
    column_mapping = {
        "id": "id",
        "title": "Tên sự kiện",
        "date": "Ngày",
        "description": "Mô tả",
        "location": "Địa điểm",
        "time": "Thời gian"
    }

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM event")

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        events = []
        for row in rows:
            event = {}
            for col, val in zip(columns, row):
                new_key = column_mapping.get(col, col)
                if new_key == "Ngày" and val:
                    try:
                        date_obj = datetime.fromisoformat(val)
                        val = date_obj.strftime("%Y-%m-%d")
                    except Exception:
                        pass
                event[new_key] = val
            events.append(event)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(events, f, ensure_ascii=False, indent=4)

        print(f"✅ Chuyển thành công {len(events)} sự kiện!")
    except Exception as e:
        print(f"⚠️ Lỗi: {e}")
    finally:
        conn.close()

# 🏗 Kiểm tra đăng nhập
def is_logged_in():
    if os.path.exists("session.json"):
        with open("session.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("logged_in", False)
    return False

def show_loading_screen():
        # Tạo cửa sổ chính
    root = tk.Tk()
    root.title("QLSK")


    # Tạo và hiển thị custom progress bar
    progress_bar = CustomProgressBar(root)
    progress_bar.pack(pady=20)
    progress_bar.start_progress(10)


    # Chạy vòng lặp chính của ứng dụng
    root.mainloop()

if __name__ == "__main__":
    convert_db_to_json()
    sync_json_to_db()

    if is_logged_in():
        show_loading_screen()
    else:
        create_login_window()
        if login_success:
            print("Đăng nhập thành công, chuyển sang giao diện chính / chờ 10s")
            show_loading_screen()
        else:
            print("Chưa đăng nhập hoặc bị sai tài khoản")
