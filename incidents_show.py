import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime
import io

class IncidentsWindow:
    def __init__(self, parent, db_manager, class_button):
        self.parent = parent
        self.db_manager = db_manager
        self.window = tk.Toplevel(parent)
        
        self.window.geometry("900x600")
        self.window.configure(bg="#ffffff")

        self.window.transient(self.parent)
        self.window.grab_set()

        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"900x600+{x}+{y}")
        self.window.wm_iconphoto(False, tk.PhotoImage(file="icon.png"))
        self.class_button = class_button

        if self.class_button == 0:
            self.window.title("Новые инциденты")
        else:
            self.window.title("Архив инцидентов")

        top_frame = tk.Canvas(self.window, width=900, height=100, bg="#ffffff", highlightthickness=0)
        top_frame.pack(fill="x")

        top_frame.create_polygon(0, 0, 600, 0, 0, 100, fill="#7673BB", outline="#7673BB")
        top_frame.create_polygon(0, 0, 550, 0, 0, 70, fill="#5B57A4", outline="#5B57A4")
        top_frame.create_polygon(0, 0, 500, 0, 0, 40, fill="#39348A", outline="#39348A")

        image = Image.open("logo.png")
        image = image.resize((300, 60), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        logo_label = tk.Label(top_frame, image=photo, bg="#ffffff", borderwidth=0, highlightthickness=0)
        logo_label.place(x=600, y=10)
        logo_label.image = photo

        self.time_label = tk.Label(
            top_frame,
            text=datetime.now().strftime("%H:%M:%S %d.%m.%Y"),
            bg="#ffffff",
            fg="#39348A",
            font=("Inter", 16)
        )
        top_frame.create_window(640, 75, window=self.time_label, anchor="nw")
        self.update_time()

        main_frame = tk.Frame(self.window, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        if self.class_button == 0:
            columns = ("№", "Класс", "Время обнаружения", "Место", "Статус")
        else:
            columns = ("№", "Класс", "Время обнаружения", "Место", "Результат")

        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            match col:
                case "№":
                    width=50
                case _:
                    width=120
            self.tree.column(col, width=width)

        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self.on_double_click)
        self.load_incidents()

    #Функция обновления времени
    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S %d.%m.%Y")
        self.time_label.config(text=current_time)
        self.window.after(1000, self.update_time)

    def load_incidents(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)

            rows = self.db_manager.load_incidents(self.class_button) 

            for row in rows:
                self.tree.insert("", "end", values=row, tags=(row[0],))

            if hasattr(self.parent, 'update_incidents_indicator'):
                self.parent.update_incidents_indicator()

        except Exception as e:
            print(f"Ошибка загрузки инцидентов: {e}")

    #Обработка двойного нажатия
    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            incident_id = self.tree.item(item, "tags")[0]
            incident_data = self.db_manager.get_incident_details(incident_id)
            if incident_data:
                self.show_incident_details_window(incident_data)

    #Функция отображения окна инцидента
    def show_incident_details_window(self, incident_data):
        id, class_name, timestamp, camera_source, id_responsible, procedure, image_data  = incident_data
        details_window = tk.Toplevel(self.window)
        details_window.title(f"Инцидент №{id}")
        details_window.configure(bg="#ffffff")
        details_window.geometry("800x500")

        main_frame = tk.Frame(details_window, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        info_frame = tk.LabelFrame(main_frame, text="Информация об инциденте", bg="#ffffff", font=("Inter", 12))
        info_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)

        info_text = f"""
Время обнаружения: {timestamp}
Место: {camera_source}
        """
        info_label = tk.Label(
            info_frame,
            text=info_text,
            bg="#ffffff",
            justify="left",
            font=("Inter", 10)
        )
        info_label.pack(padx=10, pady=10, anchor="w")

        class_label = tk.Label(
            info_frame,
            text="Класс:",
            bg="#ffffff",
            font=("Inter", 10, "bold")
        )
        class_label.pack(padx=10, pady=(10, 5), anchor="w")

        if procedure == "Не обнаружено" or procedure == "Внесено в план":
            class_new = tk.StringVar(value=class_name)
            class_entry = tk.Entry(
                info_frame,
                textvariable=class_new,
                state="readonly",
                width=30,
                font=("Inter", 10)
            )
            class_entry.pack(padx=10, pady=(0, 10), anchor="w")

            proc_label = tk.Label(
                info_frame,
                text="Результат обработки:",
                bg="#ffffff",
                font=("Inter", 10, "bold")
            )
            proc_label.pack(padx=10, pady=(10, 5), anchor="w")

            proc = tk.StringVar(value=procedure)
            class_entry = tk.Entry(
                info_frame,
                textvariable=proc,
                state="readonly",
                width=30,
                font=("Inter", 10)
            )
            class_entry.pack(padx=10, pady=(0, 10), anchor="w")

        elif not id_responsible:
            class_new = tk.StringVar(value=class_name)
            class_entry = tk.Entry(
                info_frame,
                textvariable=class_new,
                width=30,
                font=("Inter", 10)
            )
            class_entry.pack(padx=10, pady=(0, 10), anchor="w")
            save_class_btn = tk.Button(
                info_frame,
                text="Сохранить",
                bg="#5B57A4",
                fg="white",
                font=("Inter", 9),
                command=lambda: self.db_manager.class_name_record(id, class_new.get())
            )
            save_class_btn.pack(padx=10, pady=5, anchor="w") 

            responsible_label = tk.Label(
                info_frame,
                text="Ответственный за устранение:",
                bg="#ffffff",
                font=("Inter", 10, "bold")
            )
            responsible_label.pack(padx=10, pady=(15, 5), anchor="w")

            employees = self.db_manager.get_employees()
            employees_id = [emp['id'] for emp in employees]
            employee_fio = [emp['fio'] for emp in employees]

            employee_var = tk.StringVar()
            responsible_combo = ttk.Combobox(
                info_frame,
                textvariable=employee_var,
                values=employee_fio,
                state="readonly",
                width=28,
                font=("Inter", 10)
            )
            responsible_combo.pack(padx=10, pady=(0, 10), anchor="w")
            save_responsible_btn = tk.Button(
                info_frame,
                text="Назначить ответственного",
                bg="#5B57A4",
                fg="white",
                font=("Inter", 9),
                command=lambda: self.responsible_record(id,  employee_var.get(), employees_id, employee_fio, details_window)
            )
            save_responsible_btn.pack(padx=10, pady=5, anchor="w")

            buttons_frame = tk.Frame(info_frame, bg="#ffffff")
            buttons_frame.pack(fill="x", padx=10, pady=5)

            btn_planned = tk.Button(
                buttons_frame,
                text="Внесено в план",
                bg="#7673BB",
                fg="white",
                font=("Inter", 10),
                command=lambda: self.status_record(id, details_window, "Внесено в план")
            )
            btn_planned.pack(side="left", padx=0)

            btn_not_detected = tk.Button(
                buttons_frame,
                text="Не обнаружено",
                bg="#39348A",
                fg="white",
                font=("Inter", 10),
                command=lambda: self.status_record(id, details_window, "Не обнаружено")
            )
            btn_not_detected.pack(side="left", padx=5)
        else:
            class_new = tk.StringVar(value=class_name)
            class_entry = tk.Entry(
                info_frame,
                textvariable=class_new,
                state="readonly",
                width=30,
                font=("Inter", 10)
            )
            class_entry.pack(padx=10, pady=(0, 10), anchor="w")

            responsible_label = tk.Label(
                info_frame,
                text="Ответственный за устранение:",
                bg="#ffffff",
                font=("Inter", 10, "bold")
            )
            responsible_label.pack(padx=10, pady=(15, 5), anchor="w")

            result = self.db_manager.user_get_information(id_responsible)
            Surname, Name, Patronymic, Position = result
            fio_resp = Surname +" " + Name + " " + Patronymic
            resp = tk.StringVar(value=fio_resp)
            resp_entry = tk.Entry(
                info_frame,
                state="readonly",
                textvariable=resp,
                width=30,
                font=("Inter", 10)
            )
            resp_entry.pack(padx=10, pady=(0, 10), anchor="w")

            btn_finish = tk.Button(
                info_frame,
                text="Устранён",
                bg="#39348A",
                fg="white",
                font=("Inter", 10),
                command=lambda: self.status_record(id, details_window, "Устранён")
            )
            btn_finish.pack(side="left", padx=0)
            

        photo_frame = tk.LabelFrame(main_frame, text="Фотография", bg="#ffffff", font=("Inter", 12))
        photo_frame.grid(row=0, column=1, sticky="nsew", pady=10)

        if image_data:
            try:
                image = Image.open(io.BytesIO(image_data))
                image.thumbnail((350, 350), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)

                photo_label = tk.Label(photo_frame, image=photo, bg="#ffffff")
                photo_label.image = photo  # Сохраняем ссылку
                photo_label.pack(padx=10, pady=10)
            except Exception as e:
                error_label = tk.Label(photo_frame, text="Ошибка загрузки фото", bg="#ffffff", fg="red")
                error_label.pack(padx=10, pady=10)
        else:
            no_photo_label = tk.Label(photo_frame, text="Фото отсутствует", bg="#ffffff")
            no_photo_label.pack(padx=10, pady=10)


        main_frame.columnconfigure(0, weight=1)

    def status_record(self, id, window, status):
        self.db_manager.result_record(id, status)
        self.load_incidents()
        window.destroy()

    def responsible_record(self, id, responsible, employees_id, employee_fio, window):
        i = 0
        for employee in employee_fio:
            if employee == responsible:
                id_employee = employees_id[i]
                break
            else:
                i+=1
        self.db_manager.responsible_record(id, id_employee)
        self.load_incidents()
        window.destroy()
