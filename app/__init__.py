from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

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

    @app.route("/")
    def index():
        return render_template("home.html")

    # register blueprints
    app.register_blueprint(search_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(auth_bp)

    return app
