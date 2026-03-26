import sqlite3
import datetime

class Database:
    def __init__(self, db_path="anime_bot.db"):
        self.db_path = db_path
        self.create_tables()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def create_tables(self):
        """Создание таблиц в базе данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    username TEXT,
                    created_at TIMESTAMP
                )
            ''')
            
            # Таблица лайков
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_likes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    anime_id INTEGER,
                    created_at TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def add_user(self, user_id, username):
        """Добавление пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, created_at)
                VALUES (?, ?, ?)
            ''', (user_id, username, datetime.datetime.now()))
            conn.commit()
    
    def add_like(self, user_id, anime_id):
        """Добавление лайка"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_likes (user_id, anime_id, created_at)
                VALUES (?, ?, ?)
            ''', (user_id, anime_id, datetime.datetime.now()))
            conn.commit()
    
    def add_dislike(self, user_id, anime_id):
        """Добавление дизлайка"""
        # Можно создать отдельную таблицу для дизлайков
        pass