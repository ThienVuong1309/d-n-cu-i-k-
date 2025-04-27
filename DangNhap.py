import tkinter as tk
from tkinter import messagebox
import taotk
import QuenMK
import Giaodienchinh
import json
import os

USER_FILE = "users.json"
login_success = False  # Biến kiểm tra đăng nhập thành công

def load_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w", encoding="utf-8") as file:
            json.dump({}, file, ensure_ascii=False, indent=4)

    try:
        with open(USER_FILE, "r", encoding="utf-8") as file:
            users = json.load(file)
            if not isinstance(users, dict): 
                return {}
            return users
    except json.JSONDecodeError:
        return {}

def check_credentials(username, password):
    users = load_users()
    return username in users and users[username]["password"] == password

def save_session():
    with open("session.json", "w", encoding="utf-8") as f:
        json.dump({"logged_in": True}, f)

def login():
    global login_success
    username = entry_username.get()
    password = entry_password.get()

    if check_credentials(username, password):
        messagebox.showinfo("Thành công", "Đăng nhập thành công!")
        login_success = True
        save_session()
        root.destroy()
        Giaodienchinh.open_main_window()
    else:
        messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu không chính xác!")

def open_register():
    root.withdraw() 
    taotk.main()

def forgot_password():
    root.withdraw()
    QuenMK.main()

def create_login_window():
    global root, entry_username, entry_password
    root = tk.Tk()
    root.title("Quản lí sự kiện và lịch trình")
    root.geometry("400x300+550+200")
    root.resizable(True, True)

    lbl_title = tk.Label(root, text="ĐĂNG NHẬP", font=("Arial", 20, "bold"), fg="black")
    lbl_title.pack(side="top", fill="x", pady=5)

    frame = tk.Frame(root)
    frame.pack(pady=10)

    tk.Label(frame, text="Tên đăng nhập:", width=15, anchor="w").grid(row=0, column=0, padx=5, pady=5)
    entry_username = tk.Entry(frame, width=20)
    entry_username.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame, text="Mật khẩu:", width=15, anchor="w").grid(row=1, column=0, padx=5, pady=5)
    entry_password = tk.Entry(frame, show="*", width=20)
    entry_password.grid(row=1, column=1, padx=5, pady=5)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    btn_login = tk.Button(button_frame, text="Đăng nhập", width=12, command=login)
    btn_login.grid(row=0, column=0, padx=5, pady=5)

    btn_register = tk.Button(button_frame, text="Đăng ký tài khoản", width=15, command=open_register)
    btn_register.grid(row=0, column=1, padx=5, pady=5)

    btn_forgot = tk.Button(root, text="Quên mật khẩu?", font=("Arial", 8), fg="blue", borderwidth=0, command=forgot_password)
    btn_forgot.pack(pady=5, side="bottom")

    root.mainloop()
