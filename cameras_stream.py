import tkinter as tk
import cv2
import threading
import queue
from PIL import Image, ImageTk
import time
from ultralytics import YOLO
import sqlite3
from datetime import datetime
from db import DBManager
from agent import Agent
import multiprocessing as mp

def _process_object_async(id, label, video_source):
        db_manager = DBManager()
        agent = Agent()
        category = agent.category_detect(label)
        cls_translated = agent.class_name_translated(label)
        db_manager.category_detected(id, category, cls_translated)
        if category=='посторонний':
            db_manager.incident_create(id)
        

class VideoStreamWidget:
    def __init__(self, parent, video_source, width, height, bg_color="#B3B1D4"):
        self.parent = parent
        self.video_source = video_source
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.cap = None
        self.thread = None
        self.running = False
        self.frame_queue = queue.Queue(maxsize=1)
        self._after_id = None
        self.is_connected = False
        

        self.model = YOLO("yolo26x.pt")
        self.db_manager = DBManager()

        self.container = tk.Frame(parent, bg=bg_color, width=width, height=height)
        self.container.pack_propagate(False)

        self.video_label = tk.Label(self.container, bg=bg_color)
        self.video_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.retry_button = tk.Button(
            self.container,
            text="Обновить",
            bg="#B3B1D4",
            fg="#39348A",
            activebackground="#9A98C2",
            activeforeground="#39348A",
            font=("Inter", 10, "bold"),
            command=self._retry_connection
        )
    
    @property
    def is_running(self):
        return self.running    

    def start(self):
        if self.running:
            return
        self.running = True

        self.cap = cv2.VideoCapture(self.video_source)
        if not self.cap.isOpened():
            self._show_error_state()
            self.running = False
            return

        self.is_connected = True
        self._hide_error_state()
        self.thread = threading.Thread(target=self._video_worker, daemon=True)
        self.thread.start()
        self._check_queue()

    def _retry_connection(self):
        self.stop()
        self.start()

    def _show_error_state(self):
        self.is_connected = False
        self.video_label.pack_forget()
        self.retry_button.pack(expand=True, fill="both", padx=5, pady=5)

    def _hide_error_state(self):
        self.is_connected = True
        self.retry_button.pack_forget()
        self.video_label.pack(expand=True, fill="both")
    
    def _process_frame_with_ai(self, frame):
        if self.model is None:
            return frame

        try:
            results = self.model.track(frame, persist=True, verbose=False)

            if results[0].boxes is not None and results[0].boxes.id is not None:
                boxes = results[0].boxes.xywh.cpu()
                track_ids = results[0].boxes.id.int().cpu().tolist()
                classes = results[0].boxes.cls.cpu().numpy()
                confidences = results[0].boxes.conf.cpu().numpy()

                annotated_frame = results[0].plot()

                for i, (box, cls, conf, track_id) in enumerate(zip(boxes, classes, confidences, track_ids)):
                    if not self.db_manager.object_exists(track_id, self.video_source):
                        x_center, y_center, width, height = box
                        label = self.model.names[int(cls)]   
                                
                        x1 = int(x_center - width / 2)
                        y1 = int(y_center - height / 2)
                        x2 = int(x_center + width / 2)
                        y2 = int(y_center + height / 2)

                        object_roi = frame[y1:y2, x1:x2]
                        inserted_id = self.db_manager.add_object_with_image(
                            object_id=track_id,
                            class_name=label,
                            camera_source=self.video_source,
                            image_array=object_roi
                        )

                        process = mp.Process(
                            target=_process_object_async,
                            args=(inserted_id, label, self.video_source)
                        )
                        process.start()

                return annotated_frame

        except Exception as e:
            print(f"Ошибка обработки кадра моделью: {e}")

        return frame

    def _video_worker(self):
        target_fps = 30
        frame_time = 1.0 / target_fps
        prev_time = time.time()

        while self.running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    self.cap.release()
                    self.cap = None
                    self._show_error_state()
                    break

                processed_frame = self._process_frame_with_ai(frame)

                processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                processed_frame = cv2.resize(processed_frame, (self.width, self.height))

                if self.frame_queue.empty():
                    self.frame_queue.put(processed_frame)

                current_time = time.time()
                sleep_time = frame_time - (current_time - prev_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                prev_time = current_time

            except Exception as e:
                time.sleep(0.1)

    def _check_queue(self):
        try:
            frame = self.frame_queue.get_nowait()
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

            if not self.is_connected:
                self._hide_error_state()

        except queue.Empty:
            pass

        if self.running:
            self._after_id = self.container.after(30, self._check_queue)

    def stop(self):
        self.running = False

        if self._after_id:
            self.container.after_cancel(self._after_id)
            self._after_id = None

        if self.cap is not None and self.cap.isOpened():
            self.cap.release()

        if self.thread is not None:
            self.thread.join(timeout=1.0)

    def destroy(self):
        self.stop()
        self.container.destroy()

    def show_detection_dialog(self, camera_source, class_name, object_roi):
        dialog = tk.Toplevel(self.container)
        dialog.title("Обнаружен посторонний объект")
        dialog.geometry("400x400")
        dialog.resizable(False, False)
        dialog.transient(self.container)
        dialog.grab_set()
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"+{x}+{y}")

        conn, cursor = self.db_manager._get_connection()
        cursor.execute(
            "SELECT name FROM cameras WHERE source = ?",
            (camera_source,)
        )
        result = cursor.fetchone()
        
        title_label = tk.Label(
            dialog,
            text="Обнаружен посторонний объект!",
            font=("Inter", 16, "bold"),
            fg="#39348A"
        )
        title_label.pack(pady=10)

        info_text = f"Место: {result[0]}\nКласс: {class_name}"
        info_label = tk.Label(
            dialog,
            text=info_text,
            font=("Inter", 12),
            justify="left"
        )
        info_label.pack(pady=5)

        try:
            roi_rgb = cv2.cvtColor(object_roi, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(roi_rgb)
            max_size = (150, 150)
            pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(pil_image)
            image_label = tk.Label(dialog, image=photo)
            image_label.image = photo
            image_label.pack(pady=10)
        except Exception as img_error:
            error_label = tk.Label(
                dialog,
                text="Не удалось отобразить изображение",
                fg="red"
            )
            error_label.pack(pady=10)

        ok_button = tk.Button(
            dialog,
            text="OK",
            bg="#B3B1D4",
            fg="#39348A",
            font=("Inter", 12, "bold"),
            width=10,
            command=dialog.destroy
        )
        ok_button.pack(pady=20)

        dialog.focus_set()
    
    