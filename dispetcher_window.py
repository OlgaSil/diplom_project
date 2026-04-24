import tkinter as tk
from tkinter import ttk
import math
from PIL import Image, ImageTk
from datetime import datetime
from camera_add import AddCameraDialog
from cameras_stream import VideoStreamWidget
from incidents_show import IncidentsWindow

class DispencherWindow:
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
        
        self.is_fullscreen_active = False

        self.camera_widgets = []
        self.camera_name_labels = []
        self.fullscreen_widgets = []
        
        self.user_get_information()
        self.setup_ui()
    
    #Функция получения информации о пользователе
    def user_get_information(self):
        result = self.db_manager.user_get_information(self.id_user)
        self.surname, self.name, self.patronymic, self.position = result

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

        text_surname = tk.Label(left_frame, text=self.surname, bg="#B3B1D4", fg="#39348A", font=("Inter", 12))
        text_surname.place(x=10, y=550)
        text_name = tk.Label(left_frame, text=self.name, bg="#B3B1D4", fg="#39348A", font=("Inter", 12))
        text_name.place(x=10, y=570)
        text_patronymic = tk.Label(left_frame, text=self.patronymic, bg="#B3B1D4", fg="#39348A", font=("Inter", 12))
        text_patronymic.place(x=10, y=590)
        text_position = tk.Label(left_frame, text=self.position, bg="#B3B1D4", fg="#39348A", font=("Inter", 6))
        text_position.place(x=10, y=610)

        btn3 = tk.Button(left_frame, text="Выйти", bg="#B3B1D4", fg="#39348A", font=("Inter", 16), command=self.on_closing)
        btn3.place(x=0, y=630, width=250, height=50)

        main_content_frame = tk.Frame(self.window, bg="#ffffff")
        main_content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        new_incidents_frame = tk.LabelFrame(main_content_frame, text="Новые инциденты", bg="#ffffff", font=("Inter", 14, "bold"))
        new_incidents_frame.pack(fill="both", expand=True, pady=(0, 20))

        columns_new = ("№", "Класс", "Время обнаружения", "Место", "Статус")
        self.tree = ttk.Treeview(new_incidents_frame, columns=columns_new, show="headings", height=8)

        for col in columns_new:
            self.tree.heading(col, text=col)
            match col:
                case "№":
                    width = 50
                case _:
                    width = 120
            self.tree.column(col, width=width)

        scrollbar_new = ttk.Scrollbar(new_incidents_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_new.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar_new.pack(side="right", fill="y")
        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = self.db_manager.load_incidents(0)

        for row in rows:
            self.tree.insert("", "end", values=row, tags=(row[0],))

        finished_incidents_frame = tk.LabelFrame(main_content_frame, text="Завершённые инциденты", bg="#ffffff", font=("Inter", 14, "bold"))
        finished_incidents_frame.pack(fill="both", expand=True)

        columns_finished = ("№", "Класс", "Время обнаружения", "Место", "Результат")
        self.treef = ttk.Treeview(finished_incidents_frame, columns=columns_finished, show="headings", height=8)

        for col in columns_finished:
            self.treef.heading(col, text=col)
            match col:
                case "№":
                    width = 50
                case _:
                    width = 120
            self.treef.column(col, width=width)

        scrollbar_finished = ttk.Scrollbar(finished_incidents_frame, orient="vertical", command=self.treef.yview)
        self.treef.configure(yscrollcommand=scrollbar_finished.set)

        self.treef.pack(side="left", fill="both", expand=True)
        scrollbar_finished.pack(side="right", fill="y")
        
        rows = self.db_manager.load_incidents(1)

        for row in rows:
            self.treef.insert("", "end", values=row, tags=(row[0],))

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

