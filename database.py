import sqlite3

import logging

from typing import List, Optional

class BotDatabase:

    def __init__(self):

        self.db_path = "bot_database.db"

        self.init_database()

    

    def init_database(self):

        try:

            conn = sqlite3.connect(self.db_path)

            cursor = conn.cursor()

            

            cursor.execute('''

                CREATE TABLE IF NOT EXISTS users (

                    user_id INTEGER PRIMARY KEY,

                    username TEXT,

                    first_name TEXT,

                    last_name TEXT,

                    is_verified INTEGER DEFAULT 0,

                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

                )

            ''')

            

            cursor.execute('''

                CREATE TABLE IF NOT EXISTS conversations (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    user_id INTEGER,

                    role TEXT,

                    content TEXT,

                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP

                )

            ''')

            

            conn.commit()

            conn.close()

            logging.info("Database initialized")

        except Exception as e:

            logging.error(f"Database error: {e}")

    

    def add_user(self, user_id: int, username: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None):

        try:

            conn = sqlite3.connect(self.db_path)

            cursor = conn.cursor()

            cursor.execute('''

                INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)

                VALUES (?, ?, ?, ?)

            ''', (user_id, username, first_name, last_name))

            conn.commit()

            conn.close()

            return True

        except Exception as e:

            logging.error(f"Error adding user: {e}")

            return False

    

    def verify_user(self, user_id: int):

        try:

            conn = sqlite3.connect(self.db_path)

            cursor = conn.cursor()

            cursor.execute('UPDATE users SET is_verified = 1 WHERE user_id = ?', (user_id,))

            conn.commit()

            conn.close()

            return True

        except Exception as e:

            logging.error(f"Error verifying user: {e}")

            return False

    

    def is_user_verified(self, user_id: int) -> bool:

        try:

            conn = sqlite3.connect(self.db_path)

            cursor = conn.cursor()

            cursor.execute('SELECT is_verified FROM users WHERE user_id = ?', (user_id,))

            result = cursor.fetchone()

            conn.close()

            return bool(result and result[0] == 1)

        except Exception as e:

            logging.error(f"Error checking verification: {e}")

            return False

    

    def get_all_users(self) -> List[int]:

        try:

            conn = sqlite3.connect(self.db_path)

            cursor = conn.cursor()

            cursor.execute('SELECT user_id FROM users WHERE is_verified = 1')

            users = [row[0] for row in cursor.fetchall()]

            conn.close()

            return users

        except Exception as e:

            logging.error(f"Error getting users: {e}")

            return []

    

    def add_conversation(self, user_id: int, role: str, content: str):

        try:

            conn = sqlite3.connect(self.db_path)

            cursor = conn.cursor()

            cursor.execute('''

                INSERT INTO conversations (user_id, role, content)

                VALUES (?, ?, ?)

            ''', (user_id, role, content))

            conn.commit()

            conn.close()

            return True

        except Exception as e:

            logging.error(f"Error adding conversation: {e}")

            return False

    

    def get_conversation_history(self, user_id: int, limit: int = 10) -> List[dict]:

        try:

            conn = sqlite3.connect(self.db_path)

            cursor = conn.cursor()

            cursor.execute('''

                SELECT role, content FROM conversations 

                WHERE user_id = ? 

                ORDER BY timestamp DESC 

                LIMIT ?

            ''', (user_id, limit))

            results = cursor.fetchall()

            conn.close()

            return [{"role": row[0], "content": row[1]} for row in reversed(results)]

        except Exception as e:

            logging.error(f"Error getting history: {e}")

            return []

    

    def clear_conversation(self, user_id: int):

        try:

            conn = sqlite3.connect(self.db_path)

            cursor = conn.cursor()

            cursor.execute('DELETE FROM conversations WHERE user_id = ?', (user_id,))

            conn.commit()

            conn.close()

            return True

        except Exception as e:

            logging.error(f"Error clearing conversation: {e}")

            return False