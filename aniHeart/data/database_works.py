import sqlite3

class UserDatabase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def user_exists(self, user_id):
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE user_id=?", (user_id,))
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


    def insert_anme(self, genre, name, id):
        self.cursor.execute("INSERT INTO anime (genre_name, anime_name, id) VALUES (?, ?, ?)", (genre, name, id,))
        self.conn.commit()

    def catch_anime_name(self, name):
        self.cursor.execute("SELECT id FROM anime WHERE anime_name = ?", (name,))
        anime_id = self.cursor.fetchall()
        return [row[0] for row in anime_id]

    def catch_anime_count(self, name):
        self.cursor.execute("SELECT COUNT(*) AS count FROM anime WHERE anime_name = ?", (name,))
        result = self.cursor.fetchone()
        return result[0] 

    def anime_name(self, idx):
        self.cursor.execute("SELECT anime_name FROM anime WHERE id = ?", (idx,))
        result = self.cursor.fetchone()
        return result[0]

    def anime_id(self, name):
        self.cursor.execute("SELECT id FROM anime WHERE anime_name = ?", (name,))
        result = self.cursor.fetchall()
        return [row[0] for row in result]
    
    def add_anime_to_favorites(self, user_id, anime_name):
        self.cursor.execute("INSERT INTO favorite (user_id, anime_name) VALUES (?, ?)", (user_id, anime_name,))
        self.conn.commit()

    def catch_animename_by_genre(self, genre):
        self.cursor.execute("SELECT anime_name FROM anime WHERE genre_name = ?", (genre,))
        result = self.cursor.fetchall()
        return [row[0] for row in result]

    def search_by_name(self, name):
        self.cursor.execute("SELECT anime_name FROM anime WHERE anime_name = ?", (name,))
        result = self.cursor.fetchall()
        return [row[0] for row in result]

    def saved(self, user_id):
        self.cursor.execute("SELECT anime_name FROM favorite WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchall()
        return [row[0] for row in result]
    
    # Fetch the result
        