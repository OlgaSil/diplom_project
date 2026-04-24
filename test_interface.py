import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QTableWidget, QTableWidgetItem, QLabel, QPushButton,
                             QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
from datetime import datetime
import io
from PIL import Image
import sqlite3
import threading


class IncidentsWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.load_incidents()

    def init_ui(self):
        self.setWindowTitle("Новые инциденты")
        self.setGeometry(100, 100, 1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        top_frame = QFrame()
        top_frame.setStyleSheet("background-color: #ffffff;")
        top_layout = QHBoxLayout(top_frame)

        logo_label = QLabel()
        try:
            logo_pixmap = QPixmap("logo.png")
            logo_pixmap = logo_pixmap.scaled(300, 60, Qt.KeepAspectRatio)
            logo_label.setPixmap(logo_pixmap)
        except:
            logo_label.setText("LOGO")
        logo_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(logo_label)

        self.time_label = QLabel()
        self.time_label.setStyleSheet(
            "color: #39348A; font-family: Inter; font-size: 16px;"
        )
        self.update_time()
        top_layout.addWidget(self.time_label)
        top_layout.addStretch()

        main_layout.addWidget(top_frame, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["№", "Класс", "Время обнаружения", "Место", "Фото"])

        self.table.setColumnWidth(0, 50)   # №
        self.table.setColumnWidth(1, 120)  # Класс
        self.table.setColumnWidth(2, 150)  # Время обнаружения
        self.table.setColumnWidth(3, 180)  # Место
        self.table.setColumnWidth(4, 220)  # Фото

        self.table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.table, 1)

        refresh_btn = QPushButton("Обновить")
        refresh_btn.setStyleSheet(
            "background-color: #B3B1D4; color: #39348A; "
            "font-family: Inter; font-size: 12px; padding: 8px 16px;"
        )
        refresh_btn.clicked.connect(self.load_incidents)
        main_layout.addWidget(refresh_btn, 0, Qt.AlignCenter)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def update_time(self):
        current_time = datetime.now().strftime("%H:%M %d.%m.%Y")
        self.time_label.setText(current_time)

    def load_incidents(self):
        try:
            self.table.setRowCount(0)

            # Безопасное получение соединения и курсора
            result = self.db_manager._get_connection()
            if result is None:
                print("Ошибка: _get_connection() вернул None")
                return

            conn, cursor = result

            if conn is None or cursor is None:
                print("Ошибка: соединение или курсор не созданы")
                return

            cursor.execute('''
                SELECT
                  do.id,
                  do.class_name,
                  do.timestamp,
                  c.name AS camera_name,
                  do.image_data
                FROM detected_objects do
                LEFT JOIN cameras c ON do.camera_source = c.source
                ORDER BY do.timestamp DESC
                LIMIT 100
            ''')
            rows = cursor.fetchall()

            self.table.setRowCount(len(rows))

            for row_idx, row in enumerate(rows):
                incident_id, class_name, timestamp, camera_name, image_data = row

                self.table.setItem(row_idx, 0, QTableWidgetItem(str(incident_id)))
                self.table.setItem(row_idx, 1, QTableWidgetItem(class_name))
                self.table.setItem(row_idx, 2, QTableWidgetItem(timestamp))
                self.table.setItem(row_idx, 3, QTableWidgetItem(camera_name or "Неизвестно"))

                if image_data:
                    try:
                        image = Image.open(io.BytesIO(image_data))
                        image.thumbnail((200, 150), Image.Resampling.LANCZOS)

                        buffer = io.BytesIO()
                        image.save(buffer, format='PNG')
                        qimage = QImage.fromData(buffer.getvalue())
                        pixmap = QPixmap.fromImage(qimage)

                        image_label = QLabel()
                        image_label.setPixmap(pixmap)
                        image_label.setAlignment(Qt.AlignCenter)
                        image_label.setScaledContents(True)
                        image_label.setMaximumSize(200, 150)

                        cell_widget = QWidget()
                        cell_layout = QHBoxLayout(cell_widget)
                        cell_layout.addWidget(image_label)
                        cell_layout.setAlignment(Qt.AlignCenter)
                        cell_layout.setContentsMargins(5, 5, 5, 5)
                        self.table.setCellWidget(row_idx, 4, cell_widget)
                        self.table.setRowHeight(row_idx, 200)
                    except Exception as e:
                        print(f"Ошибка обработки изображения для ID {incident_id}: {e}")
                        self.table.setItem(row_idx, 4, QTableWidgetItem("Нет изображения"))
                else:
                    self.table.setItem(row_idx, 4, QTableWidgetItem("Нет изображения"))



        except Exception as e:
            print(f"Ошибка загрузки инцидентов: {e}")

# Исправленная заглушка для тестирования
if __name__ == "__main__":
    app = QApplication(sys.argv)

    class MockDBManager:
        def __init__(self):
            self.db_path = 'aerfild_data.db'

        def _get_connection(self):
            try:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                cursor = conn.cursor()
                return conn, cursor
            except Exception as e:
                print(f"Ошибка подключения к БД: {e}")
                return None

    db_manager = MockDBManager()
    window = IncidentsWindow(db_manager)
    window.show()
    sys.exit(app.exec_())