import sqlite3

conn = sqlite3.connect("song.db")
c = conn.cursor()

# songs (अगर पहले से है तो ignore)
c.execute("""
CREATE TABLE IF NOT EXISTS songs (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
file TEXT,
image TEXT
)
""")

# likes
c.execute("""
CREATE TABLE IF NOT EXISTS likes (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
song_id INTEGER
)
""")

# playlists
c.execute("""
CREATE TABLE IF NOT EXISTS playlists (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
name TEXT
)
""")

# playlist songs
c.execute("""
CREATE TABLE IF NOT EXISTS playlist_songs (
id INTEGER PRIMARY KEY AUTOINCREMENT,
playlist_id INTEGER,
song_id INTEGER
)
""")

conn.commit()
conn.close()

print("DB READY")