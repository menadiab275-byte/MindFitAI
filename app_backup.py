import sqlite3
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DATABASE = "mindfit.db"

def create_database():
    conn = sqlite3.connect(DATABASE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return "MindFit AI Backend is Running!"

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Please send JSON data"}), 400

    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")

    if not all(isinstance(val, str) and val.strip() for val in [full_name, email, password]):
        return jsonify({"error": "All fields are required"}), 400

    full_name = full_name.strip()
    email = email.strip().lower()
    password = password.strip()

    hashed_password = generate_password_hash(password)

    try:
        conn = sqlite3.connect(DATABASE)
        conn.execute(
            "INSERT INTO users (full_name, email, password) VALUES (?, ?, ?)",
            (full_name, email, hashed_password)
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "User registered successfully"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered"}), 400
    except sqlite3.Error:
        return jsonify({"error": "Database error"}), 500

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Please send JSON data"}), 400

    email = data.get("email")
    password = data.get("password")

    if not all(isinstance(val, str) and val.strip() for val in [email, password]):
        return jsonify({"error": "Email and password are required"}), 400

    email = email.strip().lower()

    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            return jsonify({
                "message": "Login successful",
                "user": {
                    "user_id": user["user_id"],
                    "full_name": user["full_name"],
                    "email": user["email"]
                }
            }), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401

    except sqlite3.Error:
        return jsonify({"error": "Database error"}), 500

@app.route("/user/<int:user_id>", methods=["GET"])
def get_user_info(user_id):
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        user = conn.execute(
            "SELECT user_id, full_name, email FROM users WHERE user_id = ?", 
            (user_id,)
        ).fetchone()
        conn.close()

        if user:
            return jsonify({
                "user_id": user["user_id"],
                "full_name": user["full_name"],
                "email": user["email"]
            }), 200
        else:
            return jsonify({"error": "User not found"}), 404

    except sqlite3.Error:
        return jsonify({"error": "Database error"}), 500

if __name__ == "__main__":
    create_database()
    app.run(debug=True)