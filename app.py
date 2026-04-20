from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"


# ===== DATABASE PATH FIX =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "songs.db")


# ===== DB CONNECT =====
def get_db():
    return sqlite3.connect(DB_PATH)


# ===== INIT DB =====
def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ===== HOME =====
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return "<h1>✅ Login Successful - Home Page</h1>"


# ===== LOGIN =====
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            username = request.form.get("username")
            password = request.form.get("password")

            conn = get_db()
            c = conn.cursor()

            c.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password)
            )
            user = c.fetchone()

            conn.close()

            if user:
                session["user"] = username
                return redirect("/")
            else:
                return "❌ Wrong username or password"

        except Exception as e:
            print("LOGIN ERROR:", e)
            return f"Error: {str(e)}"

    return render_template("login.html")


# ===== SIGNUP =====
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        try:
            username = request.form.get("username")
            password = request.form.get("password")

            conn = get_db()
            c = conn.cursor()

            c.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except Exception as e:
            print("SIGNUP ERROR:", e)
            return f"Error: {str(e)}"

    return render_template("signup.html")


# ===== LOGOUT =====
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# ===== RUN =====
if __name__ == "__main__":
    app.run(debug=True)
