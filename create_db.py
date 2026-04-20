import sqlite3

conn = sqlite3.connect("song.db")
c = conn.cursor()

# likes table
c.execute("""
CREATE TABLE IF NOT EXISTS likes (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
song_id INTEGER
)
""")

# playlists table
c.execute("""
CREATE TABLE IF NOT EXISTS playlists (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
name TEXT
)
""")

conn.commit()
conn.close()

print("DB READY")