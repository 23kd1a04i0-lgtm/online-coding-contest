import sqlite3

conn = sqlite3.connect('users.db')

# users table
conn.execute('''
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT,
    password TEXT
)
''')

# submissions table
conn.execute('''
CREATE TABLE IF NOT EXISTS submissions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    score INTEGER
)
''')

conn.commit()
conn.close()

print("Database Created Successfully")