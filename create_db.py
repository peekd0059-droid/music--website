import sqlite3

conn = sqlite3.connect("song.db")
c = conn.cursor()

# users table
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

# songs table
c.execute("""
CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    file TEXT,
    image TEXT
)
""")

# reset songs
c.execute("DELETE FROM songs")

# insert songs
c.execute("INSERT INTO songs (name, file, image) VALUES ('DR MOB Fearless Funk', 'songs/drmob.mp3', 'images/drmob.jpg')")
c.execute("INSERT INTO songs (name, file, image) VALUES ('MXZI Deno Favela', 'songs/mxzi.mp3', 'images/mxzi.jpg')")

conn.commit()
conn.close()

print("DB READY")