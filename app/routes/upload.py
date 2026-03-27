from flask import Blueprint, jsonify, render_template, request, session, url_for
from sqlalchemy import text

from app import db

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload")
def upload_page():
    return render_template("upload/form.html")


@upload_bp.route("/api/upload", methods=["POST"])
def upload_listing():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json() or {}

    required_fields = [
        "title",
        "author",
        "isbn",
        "publisher",
        "edition",
        "course",
        "condition",
    ]
    missing_fields = [field for field in required_fields if not str(data.get(field, "")).strip()]
    if missing_fields:
        return jsonify(
            {"error": f"Missing required fields: {', '.join(missing_fields)}"}
        ), 400

    payload = {field: str(data[field]).strip() for field in required_fields}
    creator_id = session.get("user_id", 1)

    try:
        existing_book = db.session.execute(
            text("SELECT id FROM books WHERE isbn = :isbn LIMIT 1"),
            {"isbn": payload["isbn"]},
        ).mappings().first()

        if existing_book:
            book_id = existing_book["id"]
        else:
            book_id = db.session.execute(
                text(
                    """
                    INSERT INTO books (isbn, title, author, publisher, edition)
                    VALUES (:isbn, :title, :author, :publisher, :edition)
                    RETURNING id
                    """
                ),
                {
                    "isbn": payload["isbn"],
                    "title": payload["title"],
                    "author": payload["author"],
                    "publisher": payload["publisher"],
                    "edition": payload["edition"],
                },
            ).scalar_one()

        listing_id = db.session.execute(
            text(
                """
                INSERT INTO listings (book_id, creator_id, course, condition)
                VALUES (:book_id, :creator_id, :course, :condition)
                RETURNING id
                """
            ),
            {
                "book_id": book_id,
                "creator_id": creator_id,
                "course": payload["course"],
                "condition": payload["condition"],
            },
        ).scalar_one()

        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 500

    return jsonify(
        {
            "message": "Textbook uploaded successfully",
            "listing_id": listing_id,
            "redirect_url": url_for("search.listing_detail", listing_id=listing_id),
        }
    ), 201
