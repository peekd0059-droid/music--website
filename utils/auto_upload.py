import os
import sqlite3

def auto_upload():
    conn = sqlite3.connect("song.db")
    c = conn.cursor()

    songs_folder = "static/songs"
    image_folder = "static/images"

    default_image = None

    # pick first image
    for img in os.listdir(image_folder):
        default_image = "images/" + img
        break

    for file in os.listdir(songs_folder):

        if not file.endswith(".mp3"):
            continue

        song_path = "songs/" + file
        name = file.replace(".mp3", "")

        # check already exists
        c.execute("SELECT * FROM songs WHERE file=?", (song_path,))
        exists = c.fetchone()

        if not exists:
            c.execute(
                "INSERT INTO songs(name,file,image) VALUES (?,?,?)",
                (name, song_path, default_image)
            )
            print("Added:", name)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    auto_upload()