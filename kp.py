import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("BookStore.db")
        self.cursor = self.conn.cursor()
        self.create_user_table()
        self.create_property_table()
        self.create_message_table()
        self.initialize_worker()
        self.update_messages_table()

    def create_user_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                password TEXT
            )
        """)
        self.conn.commit()

    def create_property_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT,
                property_type TEXT,
                area TEXT,
                number_of_floors TEXT,
                number_of_rooms INTEGER,
                cost REAL
            )
        """)
        self.conn.commit()

    def create_message_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_name TEXT,
                sender_surname TEXT,
                mobile TEXT,
                subject TEXT,
                message TEXT
            )
        """)
        self.conn.commit()

    def add_message(self, sender_name, sender_surname, mobile, subject, message):
        self.cursor.execute("""
            INSERT INTO messages (
                sender_name, sender_surname, mobile, subject, message
            ) VALUES (?, ?, ?, ?, ?)
        """, (sender_name, sender_surname, mobile, subject, message))  # added 'mobile' argument
        self.conn.commit()

    def get_messages(self):
        self.cursor.execute("""
            SELECT * FROM messages
        """)
        return self.cursor.fetchall()

    def register_user(self, username, password):
        self.cursor.execute("""
            INSERT INTO users (username, password) VALUES (?, ?)
        """, (username, password))
        self.conn.commit()

    def verify_user(self, username, password):
        self.cursor.execute("""
            SELECT * FROM users WHERE username = ? AND password = ?
        """, (username, password))
        return self.cursor.fetchone()

    def initialize_worker(self):
        # check for the existence of the user 'worker'
        user = self.verify_user("admin", "admin")
        # if not user, register it
        if not user:
            self.register_user("admin", "admin")

    def get_book(self, id=None):
        if id is not None:
            self.cursor.execute("""
                SELECT * FROM properties WHERE id = ?
            """, (id,))
            return self.cursor.fetchone()
        else:
            self.cursor.execute("""
                SELECT * FROM properties
            """)
            return self.cursor.fetchall()

    def add_book(self, address, property_type, area, number_of_floors, number_of_rooms, cost):
        self.cursor.execute("""
            INSERT INTO properties (
                address, property_type, area, number_of_floors, number_of_rooms, cost
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (address, property_type, area, number_of_floors, number_of_rooms, cost))
        self.conn.commit()

    def update_book(self, id, address, property_type, area, number_of_floors, number_of_rooms, cost):
        self.cursor.execute("""
            UPDATE properties SET 
                address = ?, property_type = ?, area = ?, number_of_floors = ?, number_of_rooms = ?, cost = ?
            WHERE id = ?
        """, (address, property_type, area, number_of_floors, number_of_rooms, cost, id))
        self.conn.commit()

    def delete_book(self, id):
        self.cursor.execute("""
            DELETE FROM properties WHERE id = ?
        """, (id,))
        self.conn.commit()

    def update_messages_table(self):
        # Check if 'mobile' field exists in the messages table
        self.cursor.execute("PRAGMA table_info(messages)")
        fields = self.cursor.fetchall()
        field_names = [field[1] for field in fields]

        if 'mobile' not in field_names:
            self.cursor.execute("ALTER TABLE messages ADD mobile TEXT")
            self.conn.commit()
