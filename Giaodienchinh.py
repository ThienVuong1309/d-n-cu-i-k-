import tkinter as tk
import json
import requests
from tkinter import messagebox, StringVar
import os
import importlib
import unidecode  # 🔥 Thêm thư viện để xử lý văn bản không dấu


# 🆕 Hàm gọi API Flask để lấy dữ liệu sự kiện và cập nhật JSON mà không xóa sự kiện cũ
# kiểm tra một là có có file events.json và events.db không, hai là có kết nối internet không, ba là có dữ liệu không?
def fetch_events_from_api():
    if os.path.exists("events.json") and os.path.exists("events.db"):
        try:
            response = requests.get("http://localhost:5000/events", timeout=20)
        
            if response.status_code == 200:
                events_api = response.json()

                events_json = []
                if os.path.exists("events.json"):
                     with open("events.json", "r", encoding="utf-8") as file:
                        try:
                            events_json = json.load(file)
                            if not events_json:
                                return "EmptyFile"
                        except json.JSONDecodeError:
                            return "EmptyFile"

                existing_events_names = {event.get("Tên sự kiện") for event in events_json}

                for event in events_api:
                    if event.get("Tên sự kiện") not in existing_events_names:
                        events_json.append(event)

                with open("events.json", "w", encoding="utf-8") as file:
                    json.dump(events_json, file, ensure_ascii=False, indent=4)

                return events_json
        except requests.exceptions.RequestException:
            return "InternetBad"
    
    return "NoFile"

# 📂 Hàm đọc & tìm kiếm sự kiện từ tệp JSON
# này là của json có cái nút chuyển đổi từ api về json áá
def load_events_from_json(filename, event_listbox, search_keyword=""):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            events = json.load(file)
            event_listbox.delete(0, tk.END)
            
            for index, event in enumerate(events, start=1):
                event_name = event.get("Tên sự kiện", "Không tên")
                event_date = event.get("Ngày", "")
                event_time = event.get("Thời gian", "")
                event_location = event.get("Địa điểm", "")

                # 🔄 **Chỉ hiển thị sự kiện nếu khớp từ khóa tìm kiếm**
                if search_keyword.lower() in event_name.lower():
                    event_listbox.insert(tk.END, f"{index}. {event_name} - {event_date} {event_time} {event_location}")

    except FileNotFoundError:
        messagebox.showerror("Lỗi", "Tệp events.json không tồn tại.")
    except json.JSONDecodeError:
        messagebox.showerror("Lỗi", "Tệp events.json không phải định dạng JSON hợp lệ.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")

# 🔄 Hàm làm mới lại Listbox (đọc từ API hoặc JSON)
# đây là cái hàm chuyển nè
# này là api
def refresh_event_listbox(event_listbox, event_source="json", search_keyword=""):
    event_listbox.delete(0, tk.END)

    if event_source == "json":
        load_events_from_json("events.json", event_listbox, search_keyword)
    elif event_source == "api":
        events = fetch_events_from_api()

        if isinstance(events, list):
            for index, event in enumerate(events, start=1):
                event_name = event.get("Tên sự kiện", "Không có tên")
                event_date = event.get("Ngày", "Không rõ ngày")
                event_time = event.get("Thời gian", "Không rõ thời gian")
                event_location = event.get("Địa điểm", "Không có địa điểm")

                # 🔄 **Chỉ hiển thị sự kiện nếu khớp từ khóa tìm kiếm**
                if search_keyword.lower() in event_name.lower():
                    event_listbox.insert(tk.END, f"{index}. {event_name} - {event_date} {event_time} {event_location}")
        
        elif events == "InternetBad":
            event_listbox.insert(tk.END, "Không có kết nối Internet!")
        elif events == "EmptyFile":
            event_listbox.insert(tk.END, "Không có dữ liệu.")
        else:
            event_listbox.insert(tk.END, "Không có dữ liệu từ API!") 

# 🔍 **Hàm tìm kiếm sự kiện**
# Cái này khi viết dấu nó vẫn tìm được như mình chat ai nó không dấu nó vẫn hiểu áá
def remove_accents(text):
    """ Chuyển văn bản có dấu thành không dấu """
    return unidecode.unidecode(text).lower()

# 🔍 Hàm tìm kiếm sự kiện
def search_events(event_listbox, entry_search, source_var):
    search_keywords = remove_accents(entry_search.get().strip()).split()  # 🔍 Xóa dấu và chia từ khóa
    event_listbox.delete(0, tk.END)

    events = fetch_events_from_api() if source_var.get() == "api" else load_events_from_json("events.json", event_listbox)
    ranked_events = []

    if isinstance(events, list):  
        for index, event in enumerate(events, start=1):
            event_name = remove_accents(event.get("Tên sự kiện", ""))
            event_date = remove_accents(event.get("Ngày", ""))
            event_time = remove_accents(event.get("Thời gian", ""))
            event_location = remove_accents(event.get("Địa điểm", ""))

            match_score = sum(keyword in event_name + event_date + event_time + event_location for keyword in search_keywords)

            if match_score > 0:
                ranked_events.append((match_score, index, event_name, event_date, event_time, event_location))

        ranked_events.sort(reverse=True, key=lambda x: x[0])

        for match_score, index, event_name, event_date, event_time, event_location in ranked_events:
            event_listbox.insert(tk.END, f"{index}. {event_name.title()} - {event_date} {event_time} {event_location} (🔍 Khớp: {match_score} từ khóa)")
    
    elif events == "InternetBad":
        event_listbox.insert(tk.END, "Không có kết nối Internet!")
    elif events == "EmptyFile":
        event_listbox.insert(tk.END, "Không có dữ liệu.")
    else:
        event_listbox.insert(tk.END, "Không có dữ liệu từ API!")  



# 🏗 **Các hàm chính giữ nguyên**
# tui có viết cho nó gọn lại á

# Thêm sự kiện mớimới
def open_create_event(main_window):
    main_window.destroy()
    taosk = importlib.import_module("taosk")
    taosk.open_create_event_window()

# Chỉnh sửa sự kiện 
def open_chinhsua(main_window, event_listbox):
    main_window.destroy()
    Chinhsuask = importlib.import_module("Chinhsuask")

# Xóa sự kiện
def xoa_sk(main_window, event_listbox):    
    main_window.destroy()
    Xoask = importlib.import_module("Xoask")

# Nơi hiển thị sự kiệnkiện
def Hien_thi_sk(main_window):
    HienthiSK = importlib.import_module("HienthiSK")
    HienthiSK.display_events(main_window)

# Hàm đăng xuất tk 
def logout(root):
    removess()
    root.destroy()
    import DangNhap
    DangNhap.create_login_window()

# nó sẽ xóa cái session.json khi đăng xuất á
def removess():
    if os.path.exists("session.json"):
        os.remove("session.json")

# Giao diện UI chính

def open_main_window():
    main_window = tk.Tk()
    main_window.title("Quản lý sự kiện và lịch trình")
    main_window.geometry("700x500+400+100")
    main_window.resizable(True, True)

    main_window.grid_rowconfigure(1, weight=1)
    main_window.grid_columnconfigure(0, weight=1)

    button_frame = tk.Frame(main_window)
    button_frame.pack(fill="x", padx=10, pady=10)

    # 📜 Tạo khung chứa danh sách sự kiện
    event_frame = tk.Frame(main_window)
    event_frame.pack(fill="both", expand=True, padx=5, pady=5)

    # 🖱️ Scrollbar dọc
    scroll_y = tk.Scrollbar(event_frame, orient=tk.VERTICAL)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    # 🔄 Scrollbar ngang
    scroll_x = tk.Scrollbar(event_frame, orient=tk.HORIZONTAL)
    scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    # 📜 Listbox có liên kết scrollbar, mở rộng hết khung
    # có thể chỉnh màu nơi hiện thị event list nè
    event_listbox = tk.Listbox(event_frame, font=("Times New Roman", 13), yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    event_listbox.pack(fill="both", expand=True, padx=5, pady=5)

    # 🔗 Kết nối scrollbar với Listbox để cuộn mượt
    scroll_y.config(command=event_listbox.yview)
    scroll_x.config(command=event_listbox.xview)

    # 🏗 **Các nút chức năng**
    for i in range(6):  
        button_frame.grid_columnconfigure(i, weight=1) # Đảm bảo kích thước các nút sẽ tự điều chỉnh khi thay đổi kích thước cửa sổ

    btn_create = tk.Button(button_frame, text="Tạo Sự Kiện", width=15, command=lambda: open_create_event(main_window))
    btn_create.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    btn_edit = tk.Button(button_frame, text="Chỉnh Sửa Sự Kiện", width=15, command=lambda: open_chinhsua(main_window, event_listbox))
    btn_edit.grid(row=0, column=1, padx=5, pady=5)

    btn_delete = tk.Button(button_frame, text="Xóa Sự Kiện", width=15, command=lambda: xoa_sk(main_window, event_listbox))
    btn_delete.grid(row=0, column=2, padx=5, pady=5)

    btn_xem = tk.Button(button_frame, text="Xem chi tiết các sự kiện", width=20, command=lambda: Hien_thi_sk(main_window))
    btn_xem.grid(row=0, column=3, padx=5, pady=5)

    btn_reload = tk.Button(button_frame, text="🔄 Làm Mới", width=12, command=lambda: refresh_event_listbox(event_listbox, source_var.get()))
    btn_reload.grid(row=0, column=4, padx=5, pady=5)

    btn_logout = tk.Button(button_frame, text="Đăng Xuất", width=15, command=lambda: logout(main_window))
    btn_logout.grid(row=0, column=5, padx=5, pady=5, sticky="e")

    source_frame = tk.Frame(main_window)
    source_frame.pack(pady=5)

    tk.Label(source_frame, text="Nguồn dữ liệu: ").pack(side=tk.LEFT)
    source_var = StringVar(value="api")
    source_var.trace("w", lambda *args: refresh_event_listbox(event_listbox, source_var.get()))

    source_menu = tk.OptionMenu(source_frame, source_var, "api", "json")
    source_menu.pack(side=tk.LEFT)

    # 🔍 **Thêm ô tìm kiếm**
    search_frame = tk.Frame(main_window)
    search_frame.pack(pady=5)
    entry_search = tk.Entry(search_frame, width=25)
    entry_search.pack(side=tk.LEFT, padx=5)
    btn_search = tk.Button(search_frame, text="🔍 Tìm Kiếm", command=lambda: search_events(event_listbox, entry_search, source_var))
    btn_search.pack(side=tk.LEFT)

    refresh_event_listbox(event_listbox, source_var.get())

    main_window.mainloop()


if __name__ == "__main__":
    open_main_window()
