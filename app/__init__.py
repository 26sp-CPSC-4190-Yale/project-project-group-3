from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.config import Config

db = SQLAlchemy()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    socketio.init_app(app)

    @app.context_processor
    def inject_auth_state():
        return {
            "current_user": {
                "id": session.get("user_id"),
                "email": session.get("user_email"),
                "username": session.get("username"),
            }
        }

    from app.routes.search import search_bp
    from app.routes.upload import upload_bp
    from app.routes.auth import auth_bp
    from app.routes.listings import listings_bp
    from app.routes.chat import chat_bp, register_socket_events

    @app.route("/")
    def index():
        stats = {"listed": 0, "saved": 0}
        active_listings = []
        hot_listings = []

        try:
            if session.get("user_id"):
                user_id = session["user_id"]
                stats["listed"] = db.session.execute(
                    text("SELECT COUNT(*) FROM listings WHERE creator_id = :user_id"),
                    {"user_id": user_id},
                ).scalar_one()
                stats["saved"] = db.session.execute(
                    text("SELECT COUNT(*) FROM saved_listings WHERE user_id = :user_id"),
                    {"user_id": user_id},
                ).scalar_one()
                active_listings = db.session.execute(
                    text(
                        """
                        SELECT l.id AS listing_id, b.title, b.author, l.course, l.condition
                        FROM listings l
                        JOIN books b ON l.book_id = b.id
                        WHERE l.creator_id = :user_id
                        ORDER BY l.id DESC
                        LIMIT 3
                        """
                    ),
                    {"user_id": user_id},
                ).mappings().all()

            hot_listings = db.session.execute(
                text(
                    """
                    SELECT l.id AS listing_id, b.title, b.author, l.course, l.condition, u.username AS posted_by
                    FROM listings l
                    JOIN books b ON l.book_id = b.id
                    JOIN users u ON l.creator_id = u.id
                    ORDER BY l.id DESC
                    LIMIT 6
                    """
                )
            ).mappings().all()
        except SQLAlchemyError:
            db.session.rollback()

        return render_template(
            "home.html",
            stats=stats,
            active_listings=active_listings,
            hot_listings=hot_listings,
        )

    # register blueprints
    app.register_blueprint(search_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(listings_bp)
    app.register_blueprint(chat_bp)

    register_socket_events(socketio)

    return app
