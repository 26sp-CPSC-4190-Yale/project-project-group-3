"""
Entry point for Flask app
Run with: python3 run.py
Opens at: https://127.0.0.1:5002/search
"""

from app import create_app, socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(
        app,
        host="127.0.0.1",
        port=5002,
        ssl_context=("localhost+2.pem", "localhost+2-key.pem"),
        debug=True,
        allow_unsafe_werkzeug=True,
    )