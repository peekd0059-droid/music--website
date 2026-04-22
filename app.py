from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import cloudinary
import cloudinary.uploader
import hashlib

app = Flask(__name__)
app.secret_key = "supersecretkey"

# CLOUDINARY
cloudinary.config(
    cloud_name="YOUR_CLOUD_NAME",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET"
)

# DB
def get_db():
    conn = sqlite3.connect("song.db")
    conn.row_factory = sqlite3.Row
    return conn

# HASH
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# INIT DB
def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY,
        name TEXT,
        file TEXT,
        image TEXT,
        plays INTEGER DEFAULT 0
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY,
        username TEXT,
        song_id INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= AUTH =================

@app.route('/signup', methods=["GET","POST"])
def signup():
    if request.method=="POST":
        u=request.form["username"]
        p=hash_password(request.form["password"])

        conn=get_db()
        c=conn.cursor()
        try:
            c.execute("INSERT INTO users(username,password) VALUES (?,?)",(u,p))
            conn.commit()
        except:
            return "User exists"

        conn.close()
        return redirect('/login')

    return render_template("signup.html")

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["username"]
        p=hash_password(request.form["password"])

        conn=get_db()
        c=conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p))

        if c.fetchone():
            session["user"]=u
            return redirect('/')

        return "Wrong login"

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ================= HOME =================

@app.route('/')
def home():
    conn=get_db()
    c=conn.cursor()

    songs=c.execute("SELECT * FROM songs").fetchall()

    user=session.get("user","guest")
    liked=[i["song_id"] for i in c.execute("SELECT song_id FROM likes WHERE username=?",(user,))]

    conn.close()

    return render_template("index.html",songs=songs,liked_ids=liked)

# ================= API =================

@app.route('/api/songs')
def api_songs():
    conn=get_db()
    songs=[dict(row) for row in conn.execute("SELECT * FROM songs")]
    conn.close()
    return jsonify(songs)

@app.route('/api/trending')
def api_trending():
    conn=get_db()
    songs=[dict(row) for row in conn.execute("SELECT * FROM songs ORDER BY plays DESC LIMIT 10")]
    conn.close()
    return jsonify(songs)

@app.route('/api/like/<int:id>', methods=["POST"])
def api_like(id):
    user=session.get("user","guest")

    conn=get_db()
    c=conn.cursor()

    existing=c.execute("SELECT * FROM likes WHERE username=? AND song_id=?",(user,id)).fetchone()

    if existing:
        c.execute("DELETE FROM likes WHERE username=? AND song_id=?",(user,id))
        status="removed"
    else:
        c.execute("INSERT INTO likes(username,song_id) VALUES (?,?)",(user,id))
        status="liked"

    conn.commit()
    conn.close()

    return jsonify({"status":status})

# ================= FEATURES =================

@app.route('/play/<int:id>')
def play(id):
    conn=get_db()
    conn.execute("UPDATE songs SET plays=plays+1 WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return "ok"

@app.route('/trending')
def trending():
    conn=get_db()
    songs=conn.execute("SELECT * FROM songs ORDER BY plays DESC LIMIT 10").fetchall()
    conn.close()
    return render_template("index.html",songs=songs,liked_ids=[])

@app.route('/liked')
def liked():
    user=session.get("user","guest")
    conn=get_db()

    songs=conn.execute("""
    SELECT songs.* FROM songs
    JOIN likes ON songs.id=likes.song_id
    WHERE likes.username=?
    """,(user,)).fetchall()

    conn.close()
    return render_template("index.html",songs=songs,liked_ids=[])

# ================= UPLOAD =================

@app.route('/upload',methods=["GET","POST"])
def upload():
    if request.method=="POST":
        name=request.form["name"]
        song=request.files["song"]
        image=request.files["image"]

        s=cloudinary.uploader.upload(song,resource_type="video")
        i=cloudinary.uploader.upload(image)

        conn=get_db()
        conn.execute("INSERT INTO songs(name,file,image) VALUES (?,?,?)",
                     (name,s["secure_url"],i["secure_url"]))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("upload.html")

# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)