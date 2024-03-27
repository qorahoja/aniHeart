import sqlite3

def create_database(db_name):
    # Connect to SQLite database (will create it if not exists)
    conn = sqlite3.connect(db_name)
    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()
    
    # Create a table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                      user_id INTEGER PRIMARY KEY,
                      username,
                      phone_number TEXT)''')


    cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
                      admin_id INTEGER PRIMARY KEY,
                      admin_name TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS genres (
                      genre_name TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS anime (
                      genre_name TEXT,
                      id, INTEGER)''')


    # Commit changes and close connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Name of the database file
    database_name = "database.db"
    # Create the database
    create_database(database_name)
    print(f"Database '{database_name}' created successfully.")
