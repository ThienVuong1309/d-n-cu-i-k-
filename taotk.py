import tkinter as tk
from tkinter import messagebox
import json
import os
import re

USER_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        return {}

    try:
        with open(USER_FILE, "r", encoding="utf-8") as file:
            users = json.load(file)
            if isinstance(users, dict):
                return users
            else:
                return {} 
    except (json.JSONDecodeError, ValueError):
        return {}  

def is_valid_email(gmail):
    return re.match(r"[^@]+@[^@]+\.[^@]+", gmail)

def save_user(username, password, email):
    users = load_users() 
    if username in users:
        messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại!")
        return False

    users[username] = {"username": username, "password": password, "email": email}

    try:
        with open(USER_FILE, "w", encoding="utf-8") as file:
            json.dump(users, file, ensure_ascii=False, indent=4)
    except IOError:
        messagebox.showerror("Lỗi", "Không thể lưu dữ liệu!")
        return False

    return True



def register_account():
    username = entry_username.get()
    password = entry_password.get()
    confirm_password = entry_confirm_password.get()
    email = entry_email.get()

    if not username or not password or not confirm_password or not email:
        messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin")
    elif len(password) < 6:
        messagebox.showerror("Lỗi", "Mật khẩu phải có ít nhất 6 ký tự")
    elif password != confirm_password:
        messagebox.showerror("Lỗi", "Mật khẩu nhập lại không khớp")
    elif not is_valid_email(email):
        messagebox.showerror("Lỗi", "Email không hợp lệ!")
        return

    elif save_user(username, password, email):
        messagebox.showinfo("Thông báo", "Đăng ký thành công!")
        go_to_login()


def go_to_login(root):
    root.destroy()
    import DangNhap
    DangNhap.create_login_window()

def main():
    global entry_username, entry_password, entry_confirm_password, entry_email
    root = tk.Tk()
    root.title("Đăng ký tài khoản")
    root.geometry("400x300+500+200")
    root.resizable(False, False)

    frame = tk.Frame(root)
    frame.pack(pady=10)

    tk.Label(frame, text="Tên đăng nhập:", width=18, anchor="w").grid(row=0, column=0, padx=5, pady=7)
    entry_username = tk.Entry(frame, width=22)
    entry_username.grid(row=0, column=1, padx=5, pady=7)

    tk.Label(frame, text="Mật khẩu:", width=18, anchor="w").grid(row=1, column=0, padx=5, pady=7)
    entry_password = tk.Entry(frame, show="*", width=22)
    entry_password.grid(row=1, column=1, padx=5, pady=7)

    tk.Label(frame, text="Nhập lại mật khẩu:", width=18, anchor="w").grid(row=2, column=0, padx=5, pady=7)
    entry_confirm_password = tk.Entry(frame, show="*", width=22)
    entry_confirm_password.grid(row=2, column=1, padx=5, pady=7)

    tk.Label(frame, text="Địa chỉ Email:", width=18, anchor="w").grid(row=3, column=0, padx=5, pady=7)
    entry_email = tk.Entry(frame, width=22)
    entry_email.grid(row=3, column=1, padx=5, pady=7)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    btn_register = tk.Button(button_frame, text="Đăng ký", width=15, command=register_account)
    btn_register.grid(row=0, column=0, padx=5, pady=5)

    btn_login = tk.Button(button_frame, text="Quay lại Đăng nhập", width=15, command=lambda: go_to_login(root))
    btn_login.grid(row=0, column=1, padx=5, pady=5)

    root.mainloop()

    
if __name__ == "__main__":  
    main()