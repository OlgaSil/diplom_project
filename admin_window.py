import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
import math
from PIL import Image, ImageTk
from datetime import datetime
import re
import string
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AdminWindow:
    def __init__(self, parent, db_manager, id_user):
        self.parent = parent
        self.db_manager = db_manager
        self.id_user = id_user

        self.window = tk.Toplevel(parent)
        self.window.title("Мониторинг аэродрома")
        self.window.geometry("1200x800")
        self.window.configure(bg="#ffffff")
        self.window.resizable(width=False, height=False)

        self.window.wm_iconphoto(False, tk.PhotoImage(file="icon.png"))

        self.camera_widgets = []
        self.camera_name_labels = []

        self.position = "Администратор"
        
        self.setup_ui()
        self.get_users_information()

    #Функция настройки интерфейса
    def setup_ui(self):
        top_frame = tk.Canvas(self.window, width=1200, height=110, bg="#ffffff", highlightthickness=0)
        top_frame.pack(fill="x")

        top_frame.create_polygon(0, 110, 249, 110, 249, 0, fill="#B3B1D4", outline="#B3B1D4")
        top_frame.create_polygon(0, 0, 900, 0, 0, 110, fill="#7673BB", outline="#7673BB")
        top_frame.create_polygon(0, 0, 850, 0, 0, 90, fill="#5B57A4", outline="#5B57A4")
        top_frame.create_polygon(0, 0, 800, 0, 0, 60, fill="#39348A", outline="#39348A")

        image = Image.open("logo.png")
        image = image.resize((300, 60), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        logo_label = tk.Label(top_frame, image=photo, bg="#ffffff", borderwidth=0, highlightthickness=0)
        logo_label.place(x=900, y=10)
        logo_label.image = photo

        self.time_label = tk.Label(top_frame, text=datetime.now().strftime("%H:%M:%S %d.%m.%Y"), bg="#ffffff", fg="#39348A", font=("Inter", 16))
        self.time_label.place(x=940, y=75)
        self.update_time()

        left_frame = tk.Frame(self.window, bg="#B3B1D4", width=250)
        left_frame.pack(side="left", fill="y")

        text_label = tk.Label(left_frame, text="Мониторинг", bg="#B3B1D4", fg="#39348A", font=("Inter", 20))
        text_label.place(x=50, y=10)
        text_label = tk.Label(left_frame, text="аэродрома", bg="#B3B1D4", fg="#39348A", font=("Inter", 20))
        text_label.place(x=55, y=45)

        btn1 = tk.Button(left_frame, text="Добавить пользователя", bg="#B3B1D4", fg="#39348A", font=("Inter", 16), command=self.add_user_window)
        btn1.place(x=0, y=100, width=250, height=100)

        text_position = tk.Label(left_frame, text=self.position, bg="#B3B1D4", fg="#39348A", font=("Inter", 16))
        text_position.place(x=10, y=580)

        btn3 = tk.Button(left_frame, text="Выйти", bg="#B3B1D4", fg="#39348A", font=("Inter", 16), command=self.on_closing)
        btn3.place(x=0, y=630, width=250, height=50)

        self.users_frame = tk.Frame(self.window, bg="#ffffff")
        self.users_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        columns = ("№", "Фамилия", "Имя", "Отчество", "Должность", "Логин", "Уровень доступа")
        self.tree = ttk.Treeview(self.users_frame, columns=columns, show="headings", height=15)
        scrollbar = ttk.Scrollbar(self.users_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        for col in columns:
            self.tree.heading(col, text=col)
            width = 150
            match col:
                case "№":
                    width=30
            self.tree.column(col, width=width)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        
        self.tree.bind("<Double-1>", self.on_user_double_click)

    #Функция получения информации о пользователе
    def get_users_information(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)

            rows = self.db_manager.user_get_information(0) 
            
            row_number = 1
            for row in rows:
                if row[-1] == 1:
                    ac = "Администратор"
                elif row[-1] == 2:
                    ac =  "Специалист"
                elif row[-1] == 3:
                    ac = "Диспетчер"
                else:
                    ac = "Рабочий"
                display_row = (row_number,) + row[:-1] + (ac,)
                self.tree.insert("", "end", values=display_row, tags=(row[0],))
                row_number += 1

        except Exception as e:
            print(f"Ошибка загрузки инцидентов: {e}")
    
    #Функция добавления пользователя
    def add_user_window(self):
        window = tk.Toplevel(self.window)
        window.title("Мониторинг аэродрома")
        window.geometry("800x600")
        window.configure(bg="#ffffff")
        window.resizable(False, False)
        
        window.transient(self.window)
        window.grab_set()

        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (800 // 2)
        y = (window.winfo_screenheight() // 2) - (600 // 2)
        window.geometry(f"800x600+{x}+{y}")
        window.wm_iconphoto(False, tk.PhotoImage(file="icon.png"))

        title_label = tk.Label(window, text="Введите данные нового пользователя", bg="#ffffff", fg="#39348A", font=("Inter", 16, "bold"))
        title_label.pack(pady=10)

        surname_label = tk.Label(window, text="Фамилия:", bg="#ffffff", fg="#39348A", font=("Inter", 12))
        surname_label.pack(anchor="w", padx=50)
        surname_entry = tk.Entry(window, bg="#f0f0f0", fg="#39348A", font=("Inter", 12), width=30)
        surname_entry.pack(padx=50, pady=(0, 10), fill="x")

        name_label = tk.Label(window, text="Имя:", bg="#ffffff", fg="#39348A", font=("Inter", 12))
        name_label.pack(anchor="w", padx=50)
        name_entry = tk.Entry(window, bg="#f0f0f0", fg="#39348A", font=("Inter", 12), width=30)
        name_entry.pack(padx=50, pady=(0, 10), fill="x")

        patronymic_label = tk.Label(window, text="Отчество:", bg="#ffffff", fg="#39348A", font=("Inter", 12))
        patronymic_label.pack(anchor="w", padx=50)
        patronymic_entry = tk.Entry(window, bg="#f0f0f0", fg="#39348A", font=("Inter", 12), width=30)
        patronymic_entry.pack(padx=50, pady=(0, 10), fill="x")

        position_label = tk.Label(window, text="Должность:", bg="#ffffff", fg="#39348A", font=("Inter", 12))
        position_label.pack(anchor="w", padx=50)
        position_entry = tk.Entry(window, bg="#f0f0f0", fg="#39348A", font=("Inter", 12), width=30)
        position_entry.pack(padx=50, pady=(0, 10), fill="x")

        email_label = tk.Label(window, text="E-mail:", bg="#ffffff", fg="#39348A", font=("Inter", 12))
        email_label.pack(anchor="w", padx=50)
        email_entry = tk.Entry(window, bg="#f0f0f0", fg="#39348A", font=("Inter", 12), width=30)
        email_entry.pack(padx=50, pady=(0, 10), fill="x")

        access_label = tk.Label(window, text="Уровень доступа:", bg="#ffffff", fg="#39348A", font=("Inter", 12))
        access_label.pack(anchor="w", padx=50)
        access_combobox = ttk.Combobox(window, values=["Администратор", "Специалист", "Диспетчер", "Рабочий"], state="readonly", font=("Inter", 12),  width=28)
        access_combobox.pack(padx=50, pady=(0, 10), fill="x")

        error_label = tk.Label(window, text="", bg="#ffffff", fg="#dc3545", font=("Inter", 10))
        error_label.pack()

        #Функция сохранения нового пользователя
        def save_data_user():
            surname = surname_entry.get()
            name = name_entry.get()
            patronymic = patronymic_entry.get()
            position = position_entry.get()
            login = email_entry.get()
            access_txt = access_combobox.get()
            if access_txt == "Администратор":
                access = 1
            elif access_txt == "Специалист":
                access = 2
            elif access_txt == "Диспетчер":
                access = 3
            else:
                access = 4

            error_label.config(text="")

            def validate_email(email: str) -> bool:
                pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                return re.match(pattern, email) is not None
            
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
            if not surname or not name or not patronymic or not position or not login or not access:
                error_label.config(text="Заполните все поля")
                return
            elif not validate_email(login) and access != 4:
                error_label.config(text="Некорректный формат email")
                return
            characters = string.ascii_letters + string.digits + "!@#$%^&*"
            password = ''.join(random.choice(characters) for _ in range(8))
            result = self.db_manager.save_new_user(surname, name, patronymic, position, login, access, password)
            if result and password_send_email(login, password, name, patronymic) and access != 4:
                error_label.config(text="Пользователь создан, пароль отправлен на email", fg="#28a745")
                self.get_users_information()
                window.after(3000, window.destroy)
            elif result and access == 4:
                error_label.config(text="Пользователь сохранён", fg="#28a745")
                self.get_users_information()
                window.after(3000, window.destroy)
            else:
                error_label.config(text="Ошибка при создании нового пользователя")


        change_btn = tk.Button(window, text="Сохранить данные пользователя", bg="#B3B1D4", fg="#39348A", font=("Inter", 14), command=save_data_user)
        change_btn.pack(pady=10)

        window.bind("<Return>", lambda event: save_data_user())

    #Функция получения информации о выделенном пользователе
    def on_user_double_click(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        item = selected_item[0]
        user_data = self.tree.item(item, "values")
        user_login = user_data[5]

        self.edit_user_window(user_login, user_data)

    #Функция редактирования пользователя
    def edit_user_window(self, user_login, user_data):
        window = tk.Toplevel(self.window)
        window.title("Редактирование пользователя")
        window.geometry("800x600")
        window.configure(bg="#ffffff")
        window.resizable(False, False)

        window.transient(self.window)
        window.grab_set()

        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (800 // 2)
        y = (window.winfo_screenheight() // 2) - (600 // 2)
        window.geometry(f"800x600+{x}+{y}")
        window.wm_iconphoto(False, tk.PhotoImage(file="icon.png"))

        title_label = tk.Label(window, text="Редактирование данных пользователя", bg="#ffffff", fg="#39348A", font=("Inter", 16, "bold"))
        title_label.pack(pady=10)
        
        if user_data[6] == 1:
            ac = "Администратор"
        elif user_data[6] == 2:
            ac =  "Специалист"
        elif user_data[6] == 3:
            ac = "Диспетчер"
        else:
            ac = "Рабочий"

        fields = [
            ("Фамилия", user_data[1]),
            ("Имя", user_data[2]),
            ("Отчество", user_data[3]),
            ("Должность", user_data[4]),
            ("E-mail (Логин)", user_data[5]),
            ("Уровень доступа", user_data[6])
        ]

        entries = {}
        for i, (label_text, current_value) in enumerate(fields):
            label = tk.Label(window, text=label_text + ":", bg="#ffffff", fg="#39348A", font=("Inter", 12))
            label.pack(anchor="w", padx=50)

            if label_text == "Уровень доступа":
                entry = ttk.Combobox(window, values=["Администратор", "Специалист", "Диспетчер", "Рабочий"], state="readonly", font=("Inter", 12), width=28)
                entry.set(current_value)
            else:
                entry = tk.Entry(window, bg="#f0f0f0", fg="#39348A", font=("Inter", 12), width=30)
                entry.insert(0, current_value)

            entry.pack(padx=50, pady=(0, 10), fill="x")
            entries[label_text] = entry

        error_label = tk.Label(window, text="", bg="#ffffff", fg="#dc3545", font=("Inter", 10))
        error_label.pack()

        button_frame = tk.Frame(window, bg="#ffffff")
        button_frame.pack(pady=20)

        save_btn = tk.Button(button_frame, text="Сохранить изменения", bg="#B3B1D4", fg="#39348A", font=("Inter", 14), command=lambda: self.save_user_changes(user_login, entries, error_label, window))
        save_btn.pack(side="left", padx=10)

        delete_btn = tk.Button(button_frame, text="Удалить пользователя", bg="#dc3545", fg="white", font=("Inter", 14), command=lambda: self.delete_user(user_login, window))
        delete_btn.pack(side="left", padx=10)

        window.bind("<Return>", lambda event: self.save_user_changes(user_login, entries, error_label, window))

    #Функция сохранения изменений данных пользователя
    def save_user_changes(self, user_login, entries, error_label, window):
        surname = entries["Фамилия"].get()
        name = entries["Имя"].get()
        patronymic = entries["Отчество"].get()
        position = entries["Должность"].get()
        login = entries["E-mail (Логин)"].get()
        access_txt = entries["Уровень доступа"].get()

        if access_txt == "Администратор":
            access = 1
        elif access_txt == "Специалист":
            access = 2
        elif access_txt == "Диспетчер":
            access = 3
        else:
            access = 4

        error_label.config(text="")

        def validate_email(email: str) -> bool:
            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            return re.match(pattern, email) is not None

        if not surname or not name or not patronymic or not position or not login or not access:
            error_label.config(text="Заполните все поля")
            return
        elif not validate_email(login) and position != "Рабочий":
            error_label.config(text="Некорректный формат email")
            return

        result = self.db_manager.update_user(user_login, surname, name, patronymic, position, login, access)

        if result:
            error_label.config(text="Данные успешно обновлены", fg="#28a745")
            self.get_users_information()
            window.after(2000, window.destroy)
        else:
            error_label.config(text="Ошибка при сохранении изменений")

    #Функция удаления пользователя
    def delete_user(self, user_login, window):
        confirm = tkinter.messagebox.askyesno(
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить этого пользователя?\n"
            "Действие нельзя отменить."
        )

        if confirm:
            result = self.db_manager.delete_user(user_login)
            if result:
                tkinter.messagebox.showinfo("Успех", "Пользователь удалён")
                self.get_users_information()
                window.destroy()
            else:
                tkinter.messagebox.showerror("Ошибка", "Не удалось удалить пользователя")

    #Функция закрытия программы
    def on_closing(self):
        for widget in self.camera_widgets:
            widget.stop()
        self.window.destroy()

    #Функция запуска программы
    def run(self):
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    #Функция обновления времени
    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S %d.%m.%Y")
        self.time_label.config(text=current_time)
        self.window.after(1000, self.update_time)