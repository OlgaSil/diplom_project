import tkinter as tk
import cv2
from cameras_stream import VideoStreamWidget

class AddCameraDialog:
    def __init__(self, parent, db_manager, on_save_callback=None):
        self.parent = parent
        self.db_manager = db_manager
        self.on_save_callback = on_save_callback

        self.dialog = None
        self.name_entry = None
        self.source_entry = None
        self.preview_label = None
        self.status_label = None

        self.video_widget = None

        self.create_dialog()
    
    #Функция создания окна добавления камеры
    def create_dialog(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Добавление новой камеры")
        self.dialog.geometry("500x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.configure(bg="#ffffff")
        self.dialog.grab_set()

        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (350 // 2)
        self.dialog.geometry(f"400x350+{x}+{y}")
        self.dialog.wm_iconphoto(False, tk.PhotoImage(file="icon.png"))

        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        self.create_widgets()
        self.dialog.focus_set()

    #Функция создания полей ввода
    def create_widgets(self):
        input_frame = tk.Frame(self.dialog, bg="#B3B1D4", padx=10, pady=10)
        input_frame.pack(fill="x")

        tk.Label(input_frame, text="Название камеры:", bg="#B3B1D4", fg="#39348A", font=("Inter", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.name_entry = tk.Entry(input_frame, width=40, font=("Inter", 10))
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)


        tk.Label(input_frame, text="Источник (URL/ID):", bg="#B3B1D4", fg="#39348A", font=("Inter", 10, "bold")).grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.source_entry = tk.Entry(input_frame, width=40, font=("Inter", 10))
        self.source_entry.grid(row=1, column=1, padx=5, pady=5)

        self.status_label = tk.Label(self.dialog, text="", bg="#ffffff", fg="red", font=("Inter", 9))
        self.status_label.pack(pady=5)

        button_frame = tk.Frame(self.dialog, bg="#ffffff")
        button_frame.pack(padx=10, pady=(0, 10), fill="x")

        test_btn = tk.Button(
            button_frame,
            text="Проверить камеру",
            bg="#B3B1D4",
            activebackground="#9A98C2",
            activeforeground="#39348A",
            fg="white",
            font=("Inter", 10, "bold"),
            command=self.test_camera
        )
        test_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

        save_btn = tk.Button(
            button_frame,
            text="Сохранить",
            bg="#39348A",
            activebackground="#9A98C2",
            activeforeground="#39348A",
            fg="white",
            font=("Inter", 10, "bold"),
            command=self.save_camera
        )
        save_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))

        preview_frame = tk.LabelFrame(self.dialog, text="Превью камеры", bg="#ffffff", padx=5, pady=5)
        preview_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.video_widget = VideoStreamWidget(
        preview_frame,
        video_source="",
        width=300,
        height=200,
        bg_color="black"
        )
        self.video_widget.widget.pack(expand=True, fill="both")

    #Функция тестирования камеры
    def test_camera(self):
        name = self.name_entry.get().strip()
        source = self.source_entry.get().strip()

        if not name or not source:
            self.status_label.config(text="Заполните все поля!", fg="red")
            return

        cap = cv2.VideoCapture(int(source))
        if not cap.isOpened():
            self.status_label.config(text=f"Не удалось подключиться к источнику: {source}", fg="red")
            cap.release()
            return
        cap.release()

        self.video_widget.video_source = int(source)
        self.video_widget.start()

        self.status_label.config(text="Предпросмотр запущен!", fg="green")

    #Функция сохранения камеры
    def save_camera(self):
        name = self.name_entry.get().strip()
        source = self.source_entry.get().strip()

        if not name or not source:
            self.status_label.config(text="Заполните все поля!", fg="red")
            return

        cap = cv2.VideoCapture(int(source))
        if not cap.isOpened():
            self.status_label.config(text=f"Камера недоступна: {source}", fg="red")
            cap.release()
            return
        cap.release()

        result=self.db_manager.get_cameras()

        if int(source) in [camera[1] for camera in result]:
            self.status_label.config(text=f"Камера уже существует: {source}", fg="red")
        else:   
            self.db_manager.add_camera(name, int(source))
            self.on_save_callback()
            self.dialog.after(1000, self.on_close)

    #Функция закрытия окна
    def on_close(self):
        if self.video_widget and self.video_widget.running:
            self.video_widget.stop()
        if self.dialog:
            self.dialog.destroy()
