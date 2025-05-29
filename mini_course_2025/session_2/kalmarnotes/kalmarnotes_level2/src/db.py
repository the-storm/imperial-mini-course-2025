import sqlite3
from contextlib import closing
import os
import random

from markupsafe import escape
import hashlib

class Database:
    def __init__(self, db_path='notes.db'):
        self.db_path = db_path
        self.remove_db()
        self._initialize_db()

    def remove_db(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def _initialize_db(self):
            with closing(self.connect_db()) as db:
                with db as conn:
                    conn.execute('''
                        CREATE TABLE IF NOT EXISTS notes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            title TEXT NOT NULL,
                            content TEXT NOT NULL
                        )
                    ''')
                    conn.execute('''
                        CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL
                            )
                    ''')
                    
                    admin_pass = hashlib.sha256(os.getenv('ADMIN_PASSWORD', 'kalmar').encode()).hexdigest()
                    flag = os.getenv('FLAG', 'default_flag')
                    conn.execute('''
                        INSERT OR IGNORE INTO users (username, password)
                        VALUES (?, ?)
                    ''', ('admin', admin_pass))
                    
                    random_large_id = random.randint(1, 100000000000)
                    conn.execute('''
                        INSERT OR IGNORE INTO notes (id, user_id, title, content)
                        VALUES (?, 1, 'Flag', ?)
                    ''', (random_large_id, flag))

                    random_large_id = random.randint(100000000000, 200000000000)
                    conn.execute('''
                        INSERT OR IGNORE INTO notes (id, user_id, title, content)
                        VALUES (?, 1, 'Note', ?)
                    ''', (random_large_id, "This is not the flag you are looking for"))

                    conn.execute('''
                        UPDATE sqlite_sequence SET seq = 0 WHERE name = 'notes'
                    ''')

    def connect_db(self):
        return sqlite3.connect(self.db_path)
    
    def sanitize_dict(self,data):
        try:

            if isinstance(data, dict):
                return {key: self.sanitize_dict(value) for key, value in data.items()}
            elif isinstance(data, list):
                return [self.sanitize_dict(item) for item in data]
            elif isinstance(data, str):
                return escape(data)
            else:
                return data
        except Exception as e:
            print(f"exception {e}", flush=True, file=sys.stderr)
            return data



    def create_new_note(self, title, content, user_id):
        with closing(self.connect_db()) as db:
            with db as conn:
                cursor = conn.execute('''
                    INSERT INTO notes (title, content, user_id)
                    VALUES (?, ?, ?)
                ''', (title, content, user_id))
                return cursor.lastrowid

    def delete_note_by_id(self, note_id, user_id):
        with closing(self.connect_db()) as db:
            with db as conn:
                cursor = conn.execute('''
                    DELETE FROM notes WHERE id = ?
                ''', (note_id,))
                return cursor.rowcount > 0

    def get_note_by_id(self, note_id, user_id):
        with closing(self.connect_db()) as db:
            cursor = db.execute('''
                SELECT id, title, content, user_id FROM notes WHERE id = ?
            ''', (note_id,))
            row = cursor.fetchone()
            # admins are allowed to read any notes!
            if row and (row[3] == user_id or user_id == 1):
                note = {'id': row[0], 'title': row[1], 'content': row[2], 'user_id': row[3]}
                return self.sanitize_dict(note)
            return None

    def get_all_notes_for_user(self, user_id):
        with closing(self.connect_db()) as db:
            cursor = db.execute('''
                SELECT id, title, content FROM notes WHERE user_id = ?
            ''', (user_id,))
            notes = [{'id': row[0], 'title': row[1], 'content': row[2]} for row in cursor.fetchall()]
            return self.sanitize_dict(notes)

    def authenticate_user(self, username, password):
        with closing(self.connect_db()) as db:
            cursor = db.execute('''
                SELECT id, username FROM users 
                WHERE username = ? AND password = ?
            ''', (username, password))
            row = cursor.fetchone()
            if row:
                return {'id': row[0], 'username': row[1]}
            return None

    def create_new_user(self, username, password):
        try:
            with closing(self.connect_db()) as db:
                with db as conn:
                    cursor = conn.execute('''
                        INSERT INTO users (username, password)
                        VALUES (?, ?)
                    ''', (username, password))
                    return {'id': cursor.lastrowid, 'username': username}
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
        
    def get_username_from_id(self, user_id):
        with closing(self.connect_db()) as db:
            cursor = db.execute('''
                SELECT username FROM users WHERE id = ?
            ''', (user_id,))
            row = cursor.fetchone()
            if row:
                return row[0]
            return None