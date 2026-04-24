import sqlite3
from datetime import datetime
import threading
import cv2
import numpy as np
import hashlib
import os

class DBManager:
    def __init__(self):
        self.db_path = 'aerfild_data.db'
        self._local = threading.local()

    '''Общие функции'''
    #Функция подключения к базе данных
    def _get_connection(self):
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.cursor = self._local.conn.cursor()
        return self._local.conn, self._local.cursor

    """Функции, связанные с пользователями"""
    #Функция хэширования пароля
    def hash_password(self, password):
        salt = os.urandom(32)
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt, hashed_password
    
    #Функция проверки пароля
    def verify_password(self, salt, hash, password):
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return new_hash == hash
    
    #Функция смены пароля пользователя
    def change_user_password(self, user_id, new_password, login):
        try:
            conn, cursor = self._get_connection()
            new_salt, new_hashed_password = self.hash_password(new_password)
            if not login:
                cursor.execute(
                    '''UPDATE Users SET Password = ?, Salt = ? WHERE id = ?''',
                    (new_hashed_password, new_salt, user_id)
                )
            else:
                cursor.execute(
                    '''UPDATE Users SET Login = ?, Password = ?, Salt = ? WHERE id = ?''',
                    (login, new_hashed_password, new_salt, user_id)
                )
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при смене пароля: {e}")
            return False

    #Функция проверки логина и пароля пользователя    
    def user_verify(self, login, password):
        try:
            conn, cursor = self._get_connection()
            cursor.execute('''SELECT id, Access, Password, Salt FROM Users WHERE Login = ?''', (login,))
            result = cursor.fetchone()
            id, access, hash, salt = result
            if hash == "admin" and login == "admin":
                return [id, access]
            elif self.verify_password(salt, hash, password):
                return [id, access]
            else:
                return [0,1]
        except Exception as e:
            return [0,0]
        
    #Функция получения информации о пользователе
    def user_get_information(self, id):
        try:
            conn, cursor = self._get_connection()
            if id == 0:
                cursor.execute('''SELECT Surname, Name, Patronymic, Position, Login, Access FROM Users WHERE id != 1''')
                result = cursor.fetchall()
            else:
                cursor.execute('''SELECT Surname, Name, Patronymic, Position FROM Users WHERE id = ?''', (id,))
                result = cursor.fetchone()
            return result
        except Exception as e:
            return []
        
    #Функция сохранения нового пользователя
    def save_new_user(self, surname, name, patronymic, position, login, access, password):
        try:
            conn, cursor = self._get_connection()
            salt, hashed_password = self.hash_password(password)
            cursor.execute('''
                INSERT INTO Users (Surname, Name, Patronymic, Position, Login, Password, Salt, Access) VALUES (?, ?, ?, ?, ?, ?, ?, ?) ''',
                (
                    surname,
                    name,
                    patronymic,
                    position,
                    login,
                    hashed_password,
                    salt,
                    access
                ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка добавления пользователя: {e}")
            return False
        
    #Функция изменения данных пользователя
    def update_user(self, user_login, surname, name, patronymic, position, login, access):
        try:
            conn, cursor = self._get_connection()
            cursor.execute(
                '''UPDATE Users SET Surname = ?, Name = ?, Patronymic = ?, Position = ?, Login = ?, Access = ? WHERE Login = ?''',
                (surname, name, patronymic, position, login, access, user_login)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
            return False

    #Функция удаления пользователя    
    def delete_user(self, user_login):
        try:
            conn, cursor = self._get_connection()
            cursor.execute(
                '''DELETE FROM Users WHERE Login = ?''', (user_login,)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении пользователя: {e}")
            return False

    #Функция проверки существования пользователя
    def user_exist(self, user_login):
        try:
            conn, cursor = self._get_connection()
            cursor.execute(
                '''SELECT id, Name, Patronymic FROM Users WHERE Login = ?''', (user_login,)
            )
            result = cursor.fetchone()
            return result
        except Exception as e:
            print(f"Пользователь не найден: {e}")
            return []

    #Функция получения списка сотрудников
    def get_employees(self):
        conn, cursor = self._get_connection()
        cursor.execute(
            '''SELECT id, Surname, Name, Patronymic FROM Users WHERE Access = 4''')
        employees = []
        for row in cursor.fetchall():
            fio = row[1] + " " + row[2] + " " + row[3]
            employees.append({'id': row[0], 'fio': fio})
        return employees

    """Функции, связанные с камерами видеонаблюдения"""
    #Функция удаления камеры    
    def delete_camera(self, camera_id):
        try:
            conn, cursor = self._get_connection()
            cursor.execute(
                '''DELETE FROM cameras WHERE id = ?''', (camera_id,)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении камеры: {e}")
            return False

    #Функция получения информации о камерах
    def get_cameras(self):
        try:
            conn, cursor = self._get_connection()
            cursor.execute("SELECT id, name, source FROM cameras")
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            print("Ошибка запроса:", e)
            return []

    #Функция добавления новой камеры
    def add_camera(self, name, source):
        try:
            conn, cursor = self._get_connection()
            cursor.execute("INSERT INTO cameras (name, source) VALUES (?, ?)", (name, source))
            conn.commit()
        except Exception as e:
            print("Ошибка добавления камеры:", e)

    """Функции, связанные с инцидентами"""
    #Функция получения информации об инциденте
    def get_incident_details(self, incident_id):
        try:
            conn, cursor = self._get_connection()
            cursor.execute(f'''SELECT
                           i.id,
                           do.class_name,
                           do.timestamp,
                           c.name AS camera_name,
                           i.id_responsible,
                           i.procedure,
                           do.image_data
                        FROM detected_objects do
                        LEFT JOIN cameras c ON do.camera_source = c.source
                        LEFT JOIN incidents i ON i.id_object = do.id
                        WHERE i.id = ?''', (incident_id,))
            result = cursor.fetchone()
            if result:
                return result
        except Exception as e:
            print(f"Ошибка получения деталей инцидента: {e}")
            return None
        
    #Функция подсчёта кол-ва новых (необработанных) инцидентов
    def count_incidents(self):
        try:
            conn, cursor = self._get_connection()
            cursor.execute("SELECT COUNT(*) FROM incidents WHERE result <> 'Завершён'")
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"Ошибка подсчёта новых инцидентов: {e}")
            return 0
    
    #Функция проверки существования записи об объекте
    def object_exists(self, object_id, camera_source):
        try:
            conn, cursor = self._get_connection()
            cursor.execute(
                "SELECT 1 FROM detected_objects WHERE object_id = ? AND camera_source = ? LIMIT 1",
                (object_id, camera_source)
            )
            return cursor.fetchone() is not None
        except Exception as e:
            print("Ошибка проверки существования объекта:", e)
            return False
    
    #Функция записи категории объекта и перевода названия класса
    def category_detected(self, id, category, class_name):
        try:
            conn, cursor = self._get_connection()
            cursor.execute(
                '''UPDATE detected_objects SET category = ?, class_name = ? WHERE id = ?''',
                (category, class_name, id)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
            return False

    #Функция записи информации об объекте в базу данных
    def add_object_with_image(self, object_id, class_name, camera_source, image_array):
        try:
            conn, cursor = self._get_connection()

            is_success, buffer = cv2.imencode('.jpg', image_array)
            if not is_success:
                raise ValueError("Не удалось закодировать изображение")

            image_binary = buffer.tobytes()

            cursor.execute('''
                INSERT INTO detected_objects
                (object_id, class_name, timestamp, camera_source, image_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                object_id,
                class_name,
                datetime.now().strftime("%H:%M %d.%m.%Y"),
                camera_source,
                image_binary
            ))
            conn.commit()
            inserted_id = cursor.lastrowid
            return inserted_id
        except Exception as e:
            print("Ошибка добавления объекта с изображением в БД:", e)
            return 0
    
    #Функция создания инцидента
    def incident_create(self, object_id):
        try:
            conn, cursor = self._get_connection()
            result = " "
            cursor.execute('''
                INSERT INTO incidents
                (id_object, result)
                VALUES (?, ?)
            ''', (
                object_id, result
            ))
            conn.commit()
            return True
        except Exception as e:
            print("Ошибка создание инцидента:", e)
            return False

    #Функция выгрузки информации об инцидентах
    def load_incidents(self, class_button):
        print(class_button)
        try:
            condition = "= 'Завершён'"
            res = "i.procedure"
            if class_button == 0:
                condition = "<> 'Завершён'"
                res = "i.result"
            conn, cursor = self._get_connection()
            cursor.execute(f'''SELECT
                i.id,
                do.class_name,
                do.timestamp,
                c.name AS camera_name,
                {res}
            FROM incidents i
            LEFT JOIN detected_objects do ON i.id_object = do.id
            LEFT JOIN cameras c ON do.camera_source = c.source
            WHERE i.result {condition}
            ORDER BY i.id ASC
            LIMIT 100''')
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            print("Ошибка запроса:", e)
            return []
        
    #Запись результата обработки инцидента
    def result_record(self, id_incident, result):
        try:
            conn, cursor = self._get_connection()
            cursor.execute(
                '''UPDATE incidents SET procedure = ?, result = "Завершён" WHERE id = ?''',
                (result, id_incident)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при сохранении результата инцидента: {e}")
            return False
    
    #Функция записи класса
    def class_name_record(self, id, class_name):
        try:
            conn, cursor = self._get_connection()
            cursor.execute(
                '''SELECT id_object FROM incidents WHERE id = ?''',(id,)
            )
            id_object = cursor.fetchone()[0]
            cursor.execute(
                '''UPDATE detected_objects
                SET class_name = ? WHERE id = ?''',
                (class_name, id_object)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
            return False

    #Функция записи ответственного за устранение   
    def responsible_record(self, id, id_employee):
        try:
            conn, cursor = self._get_connection()
            cursor.execute(
                '''UPDATE incidents SET procedure = "Устранение", id_responsible = ?, result = "Ожидает устранения" WHERE id = ?''',
                (id_employee, id)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при сохранении результата инцидента: {e}")
            return False
