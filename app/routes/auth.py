from flask import Blueprint, jsonify, request, session, url_for
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

auth_bp = Blueprint("auth", __name__)


def _password_matches(stored_password, submitted_password):
    try:
        return check_password_hash(stored_password, submitted_password)
    except ValueError:
        return stored_password == submitted_password


def _build_username(first_name, last_name, email):
    base = f"{first_name}.{last_name}".strip(".").lower()
    if not base:
        base = email.split("@", 1)[0].lower()
    return "".join(char for char in base if char.isalnum() or char in {".", "_"})


def _next_available_username(base_username):
    root = base_username or "student"
    username = root
    suffix = 1

    while True:
        existing = db.session.execute(
            text("SELECT 1 FROM users WHERE username = :username LIMIT 1"),
            {"username": username},
        ).first()
        if not existing:
            return username

        suffix += 1
        username = f"{root}{suffix}"


@auth_bp.route("/api/me")
def current_user():
    if not session.get("user_id"):
        return jsonify({"authenticated": False, "user": None})

    return jsonify(
        {
            "authenticated": True,
            "user": {
                "id": session.get("user_id"),
                "email": session.get("user_email"),
                "username": session.get("username"),
            },
        }
    )


@auth_bp.route("/api/signup", methods=["POST"])
def signup():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json() or {}
    first_name = str(data.get("first_name", "")).strip()
    last_name = str(data.get("last_name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", "")).strip()

    if not first_name or not last_name or not email or not password:
        return jsonify({"error": "All fields are required."}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400

    existing_user = db.session.execute(
        text("SELECT id FROM users WHERE email = :email LIMIT 1"),
        {"email": email},
    ).mappings().first()
    if existing_user:
        return jsonify({"error": "An account with that email already exists."}), 409

    base_username = _build_username(first_name, last_name, email)
    username = _next_available_username(base_username)

    try:
        user_id = db.session.execute(
            text(
                """
                INSERT INTO users (username, password, email)
                VALUES (:username, :password, :email)
                RETURNING id
                """
            ),
            {
                "username": username,
                "password": generate_password_hash(password),
                "email": email,
            },
        ).scalar_one()
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 500

    session["user_id"] = user_id
    session["user_email"] = email
    session["username"] = username

    return jsonify(
        {
            "message": "Account created successfully.",
            "redirect_url": url_for("search.search_page"),
            "user": {"id": user_id, "email": email, "username": username},
        }
    ), 201


@auth_bp.route("/api/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json() or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", "")).strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = db.session.execute(
        text(
            """
            SELECT id, username, email, password
            FROM users
            WHERE email = :email
            LIMIT 1
            """
        ),
        {"email": email},
    ).mappings().first()

    if not user or not _password_matches(user["password"], password):
        return jsonify({"error": "Invalid email or password."}), 401

    session["user_id"] = user["id"]
    session["user_email"] = user["email"]
    session["username"] = user["username"]

    return jsonify(
        {
            "message": "Signed in successfully.",
            "redirect_url": url_for("search.search_page"),
            "user": {
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
            },
        }
    )


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Signed out successfully.", "redirect_url": url_for("index")})
