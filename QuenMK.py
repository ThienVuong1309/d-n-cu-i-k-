import tkinter as tk
from tkinter import messagebox
import DangNhap
import taotk
import json
import os
import re

# Lấy file JSON
def user_json(email):
    with open("users.json", "r", encoding="utf-8") as f:
        events = json.load(f)
        for event in events:
            email1 = events[event]["email"]
            if email1 == email:
                return events[event]["username"]
    return None

def is_valid_email(gmail):
    return re.match(r"[^@]+@[^@]+\.[^@]+", gmail)

def email_exists(email):
    if not os.path.exists("users.json"):
        return False

    with open("users.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for key in data:
        user_info = data[key]
        if isinstance(user_info, dict) and user_info.get("email", "").lower() == email.lower():
            return True
    return False

def update_password(email, new_password):
    with open("users.json", "r+", encoding="utf-8") as f:
        data = json.load(f)
        for key in data:
            user_info = data[key]
            if isinstance(user_info, dict) and user_info.get("email", "").lower() == email.lower():
                user_info["password"] = new_password
                break
        f.seek(0)
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.truncate()

def verify_email():
    email = entry_email.get().strip().lower()  # 🆕 Chuẩn hóa email

    if not email:
        messagebox.showerror("Lỗi", "Vui lòng nhập địa chỉ email")
        return

    if not is_valid_email(email):
        messagebox.showerror("Lỗi", "Địa chỉ email không hợp lệ")
        return

    if not email_exists(email):
        messagebox.showerror("Lỗi", "Email không tồn tại trong hệ thống")
        return

    # 🆕 Lấy `username` sau khi email hợp lệ
    username = user_json(email)
    label_username.config(text=f"Tên Người Dùng: {username}" if username else "Tên Người Dùng: Không xác định")

    frame_email.pack_forget()
    frame_password.pack(pady=10)

def reset_password():
    new_password = entry_new_password.get()
    confirm_password = entry_confirm_password.get()
    email = entry_email.get()

    if len(new_password) < 6:
        messagebox.showerror("Lỗi", "Mật khẩu phải có ít nhất 6 ký tự")
    elif new_password != confirm_password:
        messagebox.showerror("Lỗi", "Mật khẩu nhập lại không khớp")
    else:
        update_password(email, new_password)
        
        # 🆕 Hiển thị thông báo đặt lại mật khẩu thành công
        messagebox.showinfo("Thông báo", f"Mật khẩu đã được đặt lại thành công!")

        root.destroy()
        DangNhap.create_login_window()

def back_login(root):
    root.destroy()
    DangNhap.create_login_window()

def main():
    global root, entry_email, entry_new_password, entry_confirm_password, frame_email, frame_password, label_username  

    root = tk.Tk()
    root.title("Quên Mật Khẩu")
    root.geometry("400x300+550+200")
    root.resizable(False, False)

    frame_email = tk.Frame(root)
    frame_email.pack(pady=20)

    tk.Label(frame_email, text="Nhập địa chỉ Email:", width=20, anchor="w").pack()
    entry_email = tk.Entry(frame_email, width=25)
    entry_email.pack(pady=5)
    btn_verify = tk.Button(frame_email, text="Xác nhận", command=verify_email)
    btn_verify.pack(pady=5)

    frame_password = tk.Frame(root)

    # 🆕 Định nghĩa `label_username` trước để cập nhật sau
    label_username = tk.Label(frame_password, text="Tên Người Dùng: Chưa xác định", font=("Arial", 10, "bold"))
    label_username.pack(pady=5)

    tk.Label(frame_password, text="Nhập mật khẩu mới:", width=20, anchor="w").pack()
    entry_new_password = tk.Entry(frame_password, show="*", width=25)
    entry_new_password.pack(pady=5)

    tk.Label(frame_password, text="Nhập lại mật khẩu:", width=20, anchor="w").pack()
    entry_confirm_password = tk.Entry(frame_password, show="*", width=25)
    entry_confirm_password.pack(pady=5)

    btn_reset = tk.Button(frame_password, text="Đặt lại mật khẩu", command=reset_password)
    btn_reset.pack(pady=5)

    btn_back = tk.Button(root, text="Quay lại Đăng nhập", command=lambda: back_login(root))
    btn_back.pack(side="bottom", pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
