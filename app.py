"""
Compatibility entry point for the unified Flask app.
Run with: python3 app.py
Primary entry point: python3 run.py
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
