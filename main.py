import tkinter as tk
from PIL import Image, ImageTk
from db import DBManager
from monitoring_window import MonitoringWindow
from admin_window import AdminWindow
from dispetcher_window import DispencherWindow
import re
import string
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.width = 600
        self.height = 400
        self.create_entry_window()
        self.db_manager = DBManager() 
        self.setup_ui()

    #Функция создания окна входа
    def create_entry_window(self):
        self.root.title("Мониторинг аэродрома")
        self.root.configure(bg="#ffffff")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = (screen_width // 2) - (self.width // 2)
        y_coordinate = (screen_height // 2) - (self.height // 2)
        self.root.geometry(f"{self.width}x{self.height}+{x_coordinate}+{y_coordinate}")
        self.root.resizable(width=False, height=False)
        self.root.wm_iconphoto(False, tk.PhotoImage(file="icon.png"))

    #Функция настройки интерфейса
    def setup_ui(self):
        top_frame = tk.Canvas(self.root, width=self.width, height=self.height/8, bg="#ffffff", highlightthickness=0)
        top_frame.pack(fill="x")

        image = Image.open("logo.png")
        image = image.resize((150, 30), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        logo_label = tk.Label(top_frame, image=photo, bg="#ffffff", borderwidth=0, highlightthickness=0)
        logo_label.place(x=10, y=20)
        logo_label.image = photo

        entry_text_label = tk.Label(top_frame, text="ВХОД", bg="#ffffff", fg="#39348A", font=("Inter", 18))
        entry_text_label.place(x=300, y=20)

        left_frame = tk.Frame(self.root, bg="#B3B1D4", width=self.width/4, height=self.height/5)
        left_frame.pack(side="left")

        text_label = tk.Label(left_frame, text="Мониторинг", bg="#B3B1D4", fg="#39348A", font=("Inter", 16))
        text_label.place(x=10, y=10)
        text_label = tk.Label(left_frame, text="аэродрома", bg="#B3B1D4", fg="#39348A", font=("Inter", 16))
        text_label.place(x=15, y=45)

        login_frame = tk.Frame(self.root, bg="#ffffff", width=self.width/4*3, height=self.height/8*7)
        login_frame.pack(fill="both", expand=True)

        self.entry_error_label = tk.Label(login_frame, text="", bg="#ffffff", fg="#dc3545", font=("Inter", 12))
        self.entry_error_label.grid(row=0, column=0, padx=(60, 0), pady=(5, 5), sticky="ew")

        login_label = tk.Label(login_frame, text="Логин:", bg="#ffffff", fg="#39348A", font=("Inter", 12))
        login_label.grid(row=1, column=0, padx=(60, 0), pady=(50, 5), sticky="w")

        self.login_entry = tk.Entry(login_frame, bg="#f0f0f0", fg="#39348A", font=("Inter", 12), width=30)
        self.login_entry.grid(row=2, column=0, padx=(60, 0), pady=(0, 15), sticky="ew")

        password_label = tk.Label(login_frame, text="Пароль:", bg="#ffffff", fg="#39348A", font=("Inter", 12))
        password_label.grid(row=3, column=0, padx=(60, 0), pady=(5, 5), sticky="w")

        self.password_entry = tk.Entry(login_frame, bg="#f0f0f0", fg="#39348A", font=("Inter", 12), width=30, show="*")
        self.password_entry.grid(row=4, column=0, padx=(60, 0), pady=(0, 15), sticky="ew")

        entry_btn = tk.Button(login_frame, text="Войти", bg="#B3B1D4", fg="#39348A", font=("Inter", 16), command=self.user_verify)
        entry_btn.grid(row=5, column=0, padx=(60, 0), pady=20, sticky="ew")
        self.root.bind("<Return>", lambda event: self.user_verify())

        recovery_btn = tk.Button(login_frame, text="Восстановить пароль", bg="#6c757d", fg="white", font=("Inter", 12), command=self.open_password_recovery)
        recovery_btn.grid(row=6, column=0, padx=(60, 0), pady=0, sticky="ew")

    #Функция обработки входа
    def user_verify(self):  
        login = self.login_entry.get()
        password = self.password_entry.get()

        self.entry_error_label.config(text="")

        if not login or not password:
            self.entry_error_label.config(text="Введите логин и пароль для входа")
        else:
            result = self.db_manager.user_verify(login, password)
            id_user, access = result
            if password == "admin" and id_user != 0:
                self.window_change_password(1)
            elif id_user == 0 and access == 0:
                self.entry_error_label.config(text="Пользователь не найден")
            elif id_user == 0 and access == 1:
                self.entry_error_label.config(text="Неверный пароль")
            elif access==1:
                self.root.withdraw()
                admin_window=AdminWindow(self.root, self.db_manager, id_user)
                admin_window.window.wait_window()
                self.root.destroy()
            elif access==2:
                self.root.withdraw()
                monitoring_window=MonitoringWindow(self.root, self.db_manager, id_user)
                monitoring_window.window.wait_window()
                self.root.destroy()
            elif access==3:
                self.root.withdraw()
                dispetcher_window=DispencherWindow(self.root, self.db_manager, id_user)
                dispetcher_window.window.wait_window()
                self.root.destroy()

    #Функция смены временного пароля администратора
    def window_change_password(self, user_id):
        window = tk.Toplevel(self.root)
        window.title("Мониторинг аэродрома")
        window.geometry("400x350")
        window.configure(bg="#ffffff")
        window.resizable(False, False)
        
        window.transient(self.root)
        window.grab_set()

        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (400 // 2)
        y = (window.winfo_screenheight() // 2) - (350 // 2)
        window.geometry(f"400x350+{x}+{y}")
        window.wm_iconphoto(False, tk.PhotoImage(file="icon.png"))

        title_label = tk.Label(window, text="Настройка", bg="#ffffff", fg="#39348A", font=("Inter", 16, "bold"))
        title_label.pack(pady=10)

        instruction_label = tk.Label(window,  text="Это первый запуск системы.\nПожалуйста, настройте учётную запись администратора:", bg="#ffffff", fg="#5B57A4", font=("Inter", 10), justify="center")
        instruction_label.pack(pady=(0, 20))
        email_label = tk.Label(window, text="E-mail администратора:", bg="#ffffff", fg="#39348A", font=("Inter", 12))
        email_label.pack(anchor="w", padx=50)
        email_entry = tk.Entry(window, bg="#f0f0f0", fg="#39348A", font=("Inter", 12), width=30)
        email_entry.pack(padx=50, pady=(0, 10), fill="x")

        new_password_label = tk.Label(window, text="Новый пароль:", bg="#ffffff", fg="#39348A", font=("Inter", 12))
        new_password_label.pack(anchor="w", padx=50)
        new_password_entry = tk.Entry(window, bg="#f0f0f0", fg="#39348A", font=("Inter", 12), width=30, show="*")
        new_password_entry.pack(padx=50, pady=(0, 10), fill="x")

        confirm_password_label = tk.Label(window, text="Подтвердите пароль:", bg="#ffffff", fg="#39348A", font=("Inter", 12))
        confirm_password_label.pack(anchor="w", padx=50)
        confirm_password_entry = tk.Entry(window, bg="#f0f0f0", fg="#39348A", font=("Inter", 12), width=30, show="*")
        confirm_password_entry.pack(padx=50, pady=(0, 10), fill="x")

        error_label = tk.Label(window, text="", bg="#ffffff", fg="#dc3545", font=("Inter", 10))
        error_label.pack()

        #Функция сохранения нового пароля администратора
        def change_password():
            email = email_entry.get()
            new_password = new_password_entry.get()
            confirm_password = confirm_password_entry.get()

            def is_valid_email(email):
                pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                return re.match(pattern, email) is not None

            error_label.config(text="")

            if not email or not new_password or not confirm_password:
                error_label.config(text="Заполните все поля")
                return
            elif new_password != confirm_password:
                error_label.config(text="Введённые пароли не совпадают")
                return
            elif len(new_password) < 6:
                error_label.config(text="Пароль должен содержать минимум 6 символов")
                return
            elif not is_valid_email(email):
                error_label.config(text="Введите корректный email адрес")
                return

            result = self.db_manager.change_user_password(user_id, new_password, email)
            if result:
                window.destroy()
                self.root.withdraw()
                admin_window = AdminWindow(self.root, self.db_manager, user_id)
                admin_window.window.wait_window()
                self.root.destroy()
            else:
                error_label.config(text="Ошибка при установке пароля") 

        change_btn = tk.Button(window, text="Сохранить пароль", bg="#B3B1D4", fg="#39348A", font=("Inter", 14), command=change_password)
        change_btn.pack(pady=10)

        window.bind("<Return>", lambda event: change_password())

    #Функция восстановления пароля
    def open_password_recovery(self):
        window = tk.Toplevel(self.root)
        window.title("Восстановление пароля")
        window.geometry("400x250")
        window.configure(bg="#ffffff")
        window.resizable(False, False)

        window.transient(self.root)
        window.grab_set()

        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (400 // 2)
        y = (window.winfo_screenheight() // 2) - (250 // 2)
        window.geometry(f"400x250+{x}+{y}")
        window.wm_iconphoto(False, tk.PhotoImage(file="icon.png"))

        title_label = tk.Label(window, text="Восстановление пароля", bg="#ffffff", fg="#39348A", font=("Inter", 16, "bold"))
        title_label.pack(pady=10)

        instruction_label = tk.Label(window, text="Введите email (логин),\nна неё будет выслан новый пароль:", bg="#ffffff", fg="#5B57A4", font=("Inter", 10), justify="center")
        instruction_label.pack(pady=(0, 20))

        email_label = tk.Label(window, text="Email (Логин):", bg="#ffffff", fg="#39348A", font=("Inter", 12))
        email_label.pack(anchor="w", padx=50)
        email_entry = tk.Entry(window, bg="#f0f0f0", fg="#39348A", font=("Inter", 12), width=30)
        email_entry.pack(padx=50, pady=(0, 10), fill="x")

        error_label = tk.Label(window, text="", bg="#ffffff", fg="#dc3545", font=("Inter", 10))
        error_label.pack()

        def send_recovery_email():
            email = email_entry.get()
            error_label.config(text="")

            def password_send_email(login, password, name, patronymic):
                try:
                    smtp_server = "smtp.yandex.ru"
                    smtp_port = 587
                    sender_email = "s-olga2002@yandex.ru"
                    sender_password = "adsyudarbsrnxvuq"
                    recipient_email = login

                    message = MIMEMultipart()
                    message["From"] = sender_email
                    message["To"] = recipient_email
                    message["Subject"] = "Доступ к системе мониторинга аэродрома"

                    body = f"""
Здравствуйте, {name} {patronymic}!

Высылаем Ваши учётные данные для доступа к системе мониторинга аэродрома:

    Логин: {login}
    Пароль: {password}

--    
С уважением,
Служба связи и АСУ
"""
                    message.attach(MIMEText(body, "plain", "utf-8"))

                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(sender_email, sender_password)
                    text = message.as_string()
                    server.sendmail(sender_email, recipient_email, text)
                    server.quit()
                    return True
                except Exception as e:
                    print(f"Ошибка отправки email: {e}")
                    return False

            if not email:
                error_label.config(text="Введите email для восстановления")
                return

            result = self.db_manager.user_exist(email)
            user_id, name, patronymic = result
            if result:
                characters = string.ascii_letters + string.digits + "!@#$%^&*"
                password = ''.join(random.choice(characters) for _ in range(8))
                result = self.db_manager.change_user_password(user_id, password, email)
                if result and password_send_email(email, password, name, patronymic):
                    error_label.config(text="Новый пароль отправлен на email", fg="#28a745")
                    window.after(3000, window.destroy)
                else:
                    error_label.config(text="Ошибка отправки пароля")
            else:
                error_label.config(text="Пользователь с таким email не найден")

        send_btn = tk.Button(window, text="Отправить новый пароль", bg="#B3B1D4", fg="#39348A", font=("Inter", 14), command=send_recovery_email)
        send_btn.pack(pady=10)

        cancel_btn = tk.Button(window, text="Отмена", bg="#6c757d", fg="white", font=("Inter", 14), command=window.destroy)
        cancel_btn.pack(pady=5)

        window.bind("<Return>", lambda event: send_recovery_email())

    #Функция закрытия программы
    def on_closing(self):
        self.root.destroy()

    #Функция запуска программы
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()