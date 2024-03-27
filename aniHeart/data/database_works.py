import sqlite3

class UserDatabase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def user_exists(self, user_id):
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE id=?", (user_id,))
        count = self.cursor.fetchone()[0]
        return count > 0



    def insert_user(self, user_id, name, phone_number):
        self.cursor.execute("INSERT INTO users (user_id, username, phone_number) VALUES (?, ?, ?)", (user_id, name, phone_number,))
        self.conn.commit()


    def admin_check(self, admin_id):
        self.cursor.execute("SELECT admin_id FROM admins")
        admin_ids = self.cursor.fetchall()
        for row in admin_ids:
            return row[0]

    def insert_genere_name(self, genre_name):
        self.cursor.execute("INSERT INTO genres (genre_name) VALUES (?)", (genre_name,))
        self.conn.commit()


    def select_genres(self):
        self.cursor.execute("SELECT genre_name FROM genres")
        genres = self.cursor.fetchall()
        return [row[0] for row in genres]


    def insert_anme(self, genre, id):
        self.cursor.execute("INSERT INTO anime (genre_name, id) VALUES (?, ?)", (genre, id,))
        self.conn.commit()