"""
Entry point for Flask app
Run with: python3 run.py
Opens at: http://127.0.0.1:5000/search
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)