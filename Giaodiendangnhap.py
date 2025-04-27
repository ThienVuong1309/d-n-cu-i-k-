import tkinter as tk
from tkinter import messagebox
from tkinter import font
from PIL import Image, ImageTk
import threading
from DangNhap import create_login_window, login_success
import time

def create_login_window1():
    def open_google_login():
        if not terms_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chấp nhận điều khoản và chính sách của chúng tôi!")
            return
        messagebox.showinfo("Google Login", "Đăng nhập bằng Google (demo).")

    def open_github_login():
        if not terms_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chấp nhận điều khoản và chính sách của chúng tôi!")
            return
        messagebox.showinfo("GitHub Login", "Đăng nhập bằng GitHub (demo).")

    def show_normal_login():
        if not terms_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chấp nhận điều khoản và chính sách của chúng tôi!")
            return
        # Đóng cửa sổ login hiện tại
        root.destroy()
        # Nhập và gọi hàm mở giao diện chính từ file main.py
        create_login_window()

    def back_to_options():
        # Nếu bạn có thêm form đăng nhập, thì chỗ này sẽ hiện lại widget đăng nhập ban đầu.
        username_label.place_forget()
        username_entry.place_forget()
        password_label.place_forget()
        password_entry.place_forget()
        login_button.place_forget()
        back_button.place_forget()

        google_button.place(x=50, y=150, width=300, height=40)
        github_button.place(x=50, y=200, width=300, height=40)
        normal_login_button.place(x=50, y=250, width=300, height=40)
        terms_checkbox.place(x=50, y=300)

    def login_with_account():
        # Nếu cần xử lý đăng nhập tài khoản, bạn có thể thêm logic ở đây.
        pass

    root = tk.Tk()
    root.title("Esmart QLSK")
    root.geometry("400x600")
    root.configure(bg="white")
    root.resizable(False, False)

    # Logo đặt ở giữa phía trên
    logo_font = font.Font(family="Arial", size=24, weight="bold")
    logo_label = tk.Label(root, text="Esmart QLSK", font=logo_font, bg="white")
    logo_label.place(x=200, y=50, anchor="center")

    # Load icon cho Google và GitHub
    try:
        google_img = Image.open("google_icon.png").resize((20, 20))
        google_icon = ImageTk.PhotoImage(google_img)
    except Exception as e:
        google_icon = None

    try:
        github_img = Image.open("github_icon.png").resize((20, 20))
        github_icon = ImageTk.PhotoImage(github_img)
    except Exception as e:
        github_icon = None

    # Nút đăng nhập bằng Google
    google_button = tk.Button(root, text="  Đăng nhập bằng Google", image=google_icon,
                              compound="left", bg="white", fg="black",
                              relief="solid", command=open_google_login, anchor="center")
    google_button.image = google_icon
    google_button.place(x=50, y=150, width=300, height=40)

    # Nút đăng nhập bằng GitHub
    github_button = tk.Button(root, text="  Đăng nhập bằng GitHub", image=github_icon,
                              compound="left", bg="white", fg="black",
                              relief="solid", command=open_github_login, anchor="center")
    github_button.image = github_icon
    github_button.place(x=50, y=200, width=300, height=40)

    # Nút đăng nhập bằng tài khoản Esmart QLSK - sẽ mở main.py
    normal_login_button = tk.Button(root, text="Đăng nhập bằng tài khoản Esmart QLSK",
                                    bg="#007bff", fg="white", font=("Arial", 10, "bold"),
                                    command=show_normal_login)
    normal_login_button.place(x=50, y=250, width=300, height=40)

    # Checkbox "Chấp nhận điều khoản và chính sách"
    terms_var = tk.BooleanVar()
    terms_checkbox = tk.Checkbutton(root, text="Chấp nhận điều khoản và chính sách của chúng tôi",
                                    bg="white", variable=terms_var)
    terms_checkbox.place(x=50, y=300)

    # Các widget cho form đăng nhập (không sử dụng nếu mở main.py)
    username_label = tk.Label(root, text="Tên đăng nhập:", bg="white")
    username_entry = tk.Entry(root)
    password_label = tk.Label(root, text="Mật khẩu:", bg="white")
    password_entry = tk.Entry(root, show="*")
    login_button = tk.Button(root, text="Đăng nhập", bg="#28a745", fg="white",
                             font=("Arial", 10, "bold"), command=login_with_account)
    back_button = tk.Button(root, text="Quay lại", bg="white", fg="black",
                            font=("Arial", 10), command=back_to_options)

    root.mainloop()

if __name__ == "__main__":
    create_login_window1()
