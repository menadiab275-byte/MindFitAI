from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash

app = Flask(__name__)

DATABASE = "mindfit.db"


def create_database():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        return jsonify({
            "error": "Please send JSON data"
        }), 400

    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")

    if not all(isinstance(value, str) and value.strip()
               for value in [full_name, email, password]):
        return jsonify({
            "error": "All fields are required"
        }), 400

    full_name = full_name.strip()
    email = email.strip().lower()

    if len(password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters"
        }), 400

    hashed_password = generate_password_hash(password)

    try:
        conn = sqlite3.connect(DATABASE)

        conn.execute("""
            INSERT INTO users (full_name, email, password)
            VALUES (?, ?, ?)
        """, (full_name, email, hashed_password))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Account created successfully",
            "full_name": full_name,
            "email": email
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Email already exists"
        }), 409

    except sqlite3.Error:
        return jsonify({
            "error": "Database error"
        }), 500


if __name__ == "__main__":
    create_database()
    app.run(debug=True)