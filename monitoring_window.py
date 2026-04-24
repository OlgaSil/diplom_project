import tkinter as tk
import math
from PIL import Image, ImageTk
from datetime import datetime
from camera_add import AddCameraDialog
from cameras_stream import VideoStreamWidget
from incidents_show import IncidentsWindow

class MonitoringWindow:
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
        self.refresh_camera_streams()
        self.update_incidents_indicator()

        self.window.after(30000, self.schedule_indicator_update) 
    
    #Функция получения информации о пользователе
    def user_get_information(self):
        result = self.db_manager.user_get_information(self.id_user)
        self.surname, self.name, self.patronymic, self.position = result

    #Функция запуска окна отображения новых инцидентов
    def show_incidents_window_new(self):
        IncidentsWindow(self.window, self.db_manager, 0)
        self.window.after(1000, self.update_incidents_indicator) 

    #Функция запуска окна отображения архивных инцидентов
    def show_incidents_window_history(self):
        IncidentsWindow(self.window, self.db_manager, 1) 

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

        btn1_frame = tk.Frame(left_frame, bg="#B3B1D4")
        btn1_frame.place(x=0, y=100, width=250, height=100)

        self.btn_new_incidents = tk.Button(btn1_frame, text="Новые инциденты", bg="#B3B1D4", fg="#39348A", font=("Inter", 16), command=self.show_incidents_window_new)
        self.btn_new_incidents.pack(fill="both", expand=True)

        self.indicator_canvas = tk.Canvas(btn1_frame, width=15, height=15, bg="#B3B1D4", highlightthickness=0)
        self.indicator_canvas.place(relx=0.9, rely=0.1)
        self.indicator = None

        btn2 = tk.Button(left_frame, text="Архив инцидентов", bg="#B3B1D4", fg="#39348A", font=("Inter", 16), command=self.show_incidents_window_history)
        btn2.place(x=0, y=200, width=250, height=100)

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

        self.video_frame = tk.Frame(self.window, bg="#ffffff")
        self.video_frame.pack(side="right", fill="both", expand=True)

    #Функция обновления видеопотоков
    def refresh_camera_streams(self):
        cameras_data = self.db_manager.get_cameras()
        for widget in self.camera_widgets:
            widget.stop()

        for widget in self.fullscreen_widgets:
            if hasattr(widget, 'is_running') and widget.is_running:
                widget.stop()
        self.fullscreen_widgets.clear()

        for child in self.video_frame.winfo_children():
            child.destroy()
        self.camera_widgets.clear()
        self.camera_name_labels.clear()

        if not cameras_data:
            self.show_add_button_only()
            return

        id, camera_names, video_sources = zip(*cameras_data)
        camera_kol = len(cameras_data) + 1

        l = math.sqrt(camera_kol)
        kol_str, kol_stl = 0, 0
        if l % 1 != 0:
            l = round(l)
            kol_str = l
            kol_stl = math.ceil(camera_kol / kol_str)
        else:
            kol_str = l
            kol_stl = math.ceil(camera_kol / l)
        if kol_stl < 3:
            kol_stl = 3

        max_rows = int(kol_str)
        max_cols = int(kol_stl)

        cw = int(950 / max_cols) - 10

        if cw < 300:
            global CAMERA_WIDTH, CAMERA_HEIGHT
            CAMERA_WIDTH = cw
            CAMERA_HEIGHT = int(math.ceil(cw / 1.5))

        iterator = 0
        camera_kol -= 1

        for i in range(max_rows):
            for j in range(max_cols):
                if iterator < camera_kol:
                    cell_frame = tk.Frame(self.video_frame, bg="#ffffff")
                    cell_frame.grid(row=i, column=j, padx=0, pady=5)
                    cell_frame.grid_rowconfigure(0, weight=1)
                    cell_frame.grid_rowconfigure(1, weight=0)
                    cell_frame.grid_columnconfigure(0, weight=1)

                    video_container = tk.Frame(cell_frame, bg="#000000")
                    video_container.grid(row=0, column=0, padx=1, pady=5, sticky="nsew")

                    video_widget = VideoStreamWidget(
                        video_container,
                        video_sources[iterator],
                        CAMERA_WIDTH,
                        CAMERA_HEIGHT
                    )
                    video_widget.container.pack(fill="both", expand=True)
                    self.camera_widgets.append(video_widget)

                    bottom_container = tk.Frame(cell_frame, bg="#ffffff")
                    bottom_container.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))

                    name_label = tk.Label(
                        bottom_container,
                        text=camera_names[iterator],
                        bg="#ffffff",
                        fg="#39348A",
                        font=("Inter", 12, "bold")
                    )
                    name_label.pack(side="left", padx=(0, 10))

                    menu_button = tk.Button(
                        bottom_container,
                        text="⋯",
                        bg="#B3B1D4",
                        fg="#39348A",
                        font=("Arial", 12),
                        width=2,
                        height=1
                    )
                    menu_button.pack(side="right")

                    menu_button.bind(
                        "<Button-1>",
                        lambda e, idx=iterator: self.show_camera_menu(e, idx)
                    )

                    self.camera_name_labels.append(name_label)
                    video_widget.start()
                elif iterator == camera_kol:
                    self.create_add_camera_button(i, j)
                else:
                    cell_frame = tk.Frame(self.video_frame, bg="#ffffff")
                    cell_frame.grid(row=i, column=j, padx=0, pady=5)
                    empty_label = tk.Label(cell_frame, bg="#ffffff", width=CAMERA_WIDTH, height=CAMERA_HEIGHT)
                    empty_label.grid(row=0, column=0, padx=1, pady=5, sticky="nsew")
                iterator += 1

            for j in range(max_cols):
                self.video_frame.grid_columnconfigure(j, weight=1, minsize=CAMERA_WIDTH)
            for i in range(max_rows):
                self.video_frame.grid_rowconfigure(i, weight=1, minsize=CAMERA_HEIGHT + 10)

    #Функция отображения меню камеры
    def show_camera_menu(self, event, camera_index):
        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(
            label="Открыть в полноэкранном режиме",
            command=lambda: self.open_fullscreen_camera(camera_index)
        )
        menu.add_separator()
        menu.add_command(
            label="Удалить камеру",
            command=lambda: self.confirm_delete_camera(camera_index)
        )
        menu.post(event.x_root, event.y_root)

    #Функция запроса подтвеждения удаления камеры
    def confirm_delete_camera(self, camera_index):
        result = tk.messagebox.askyesno(
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить эту камеру?",
            parent=self.window
        )
        if result:
            self.delete_camera(camera_index)

    #Функция удаления камеры
    def delete_camera(self, camera_index):
        cameras_data = self.db_manager.get_cameras()
        if 0 <= camera_index < len(cameras_data):
            camera_id = cameras_data[camera_index][0]
            self.db_manager.delete_camera(camera_id)
            self.refresh_camera_streams()

    #Функция открытия видеопотока в отдельном окне
    def open_fullscreen_camera(self, camera_index):
        cameras_data = self.db_manager.get_cameras()
        if 0 <= camera_index < len(cameras_data):
            camera_name = cameras_data[camera_index][1]
            video_source = cameras_data[camera_index][2]

            fullscreen_window = tk.Toplevel(self.window)
            fullscreen_window.title(camera_name)
            fullscreen_window.geometry("800x600")
            fullscreen_window.configure(bg="#ffffff")
            fullscreen_window.resizable(False, False)

            fullscreen_window.transient(self.window)
            fullscreen_window.grab_set()

            x = (fullscreen_window.winfo_screenwidth() // 2) - (800 // 2)
            y = (fullscreen_window.winfo_screenheight() // 2) - (600 // 2)
            fullscreen_window.geometry(f"800x550+{x}+{y}")
            fullscreen_window.wm_iconphoto(False, tk.PhotoImage(file="icon.png"))

            video_frame = tk.Frame(fullscreen_window, bg="#000000")
            video_frame.pack(fill="both", expand=True)

            fullscreen_widget = VideoStreamWidget(video_frame, video_source, 750, 500)
            fullscreen_widget.container.pack(padx=10, pady=10)
            fullscreen_widget.start()

            self.current_fullscreen_widget = fullscreen_widget
            self.is_fullscreen_active = True

            fullscreen_window.protocol("WM_DELETE_WINDOW",
                            lambda: self.on_fullscreen_close(camera_index, fullscreen_window))

    #Функция закрытия отдельного окна видеопотока
    def on_fullscreen_close(self, camera_index, fullscreen_window):
        if hasattr(self, 'current_fullscreen_widget'):
            self.current_fullscreen_widget.stop()
            del self.current_fullscreen_widget
        self.is_fullscreen_active = False
        self.refresh_camera_streams()
        fullscreen_window.destroy()
        
    #Функция отображения основного окна без видеопотоков
    def show_add_button_only(self):
        cell_frame = tk.Frame(self.video_frame, bg="#ffffff")
        cell_frame.grid(row=0, column=0, padx=0, pady=5)
        cell_frame.grid_columnconfigure(0, weight=1)
        cell_frame.grid_rowconfigure(0, weight=1)

        self.add_button = tk.Button(cell_frame, text="+", bg="#B3B1D4", fg="#39348A", activebackground="#9A98C2", activeforeground="#39348A", font=("Inter", 36, "bold"), width=4, height=1, command=self.open_add_camera_dialog)
        self.add_button.grid(row=0, column=0, padx=1, pady=5, sticky="nsew")

        self.video_frame.grid_columnconfigure(0, weight=1)
        self.video_frame.grid_rowconfigure(0, weight=1)

    #Функция отображения основного окна с видеопотоками
    def create_add_camera_button(self, row, col):
        cell_frame = tk.Frame(self.video_frame, bg="#ffffff")
        cell_frame.grid(row=row, column=col, padx=0, pady=5)
        self.add_button = tk.Button(cell_frame, text="+", bg="#B3B1D4", fg="#39348A", activebackground="#9A98C2", activeforeground="#39348A", font=("Inter", 36, "bold"), width=4, height=1, command=self.open_add_camera_dialog)
        self.add_button.grid(row=0, column=0, padx=1, pady=5)

    #Функция отображения кол-ва новых (непросмотренных) инцидентов
    def update_incidents_indicator(self):
        count = self.db_manager.count_incidents()
        if count != 0:
            if self.indicator:
                self.indicator_canvas.delete(self.indicator)
                self.indicator = None

            if count > 0:
                self.indicator = self.indicator_canvas.create_oval(
                    2, 2, 13, 13,
                    fill="red",
                    outline="red"
                )
                if count < 100:
                    self.indicator_canvas.create_text(
                        7.5, 7.5,
                        text=str(count),
                        fill="white",
                        font=("Arial", 8, "bold")
                    )

    #Функция обновления кол-ва новых (непросмотренных) инцидентов
    def schedule_indicator_update(self):
        self.update_incidents_indicator()
        self.window.after(30000, self.schedule_indicator_update)

    #Функция запуска окна добавления камеры
    def open_add_camera_dialog(self):
        AddCameraDialog(
            parent=self.window,
            db_manager=self.db_manager,
            on_save_callback=self.refresh_camera_streams
        )

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

CAMERA_WIDTH, CAMERA_HEIGHT = 300, 200
