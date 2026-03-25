from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('upload.html')


# For easy local testing, use SQLite:
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///openshelf.db'

# When you are ready to connect to PostgreSQL, comment out the SQLite line above and use:
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/openshelf'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model for Textbook Listings
class Listing(db.Model):
    __tablename__ = 'listings'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    course = db.Column(db.String(100), nullable=True)
    condition = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Temporary: image_url is commented out until we add image upload support
    # image_url = db.Column(db.String(255), nullable=True)
    
    # Placeholder for the user who uploaded the textbook
    owner_id = db.Column(db.Integer, nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Helper method to convert the model record to a Python dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'course': self.course,
            'condition': self.condition,
            'description': self.description,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat()
        }

@app.route('/api/upload', methods=['POST'])
def upload_textbook():
    """
    Endpoint to upload a new textbook listing.
    Currently only accepts JSON text data (no image uploading yet).
    """
    # Ensure the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    
    # Extract required fields from the JSON payload
    title = data.get('title')
    author = data.get('author')
    condition = data.get('condition')
    
    # Basic validation for required fields
    if not title or not author or not condition:
        return jsonify({"error": "Missing required fields: title, author, condition"}), 400
        
    # Extract optional fields
    course = data.get('course')
    description = data.get('description')
    
    # Use a dummy owner_id since authentication is not yet integrated
    # We assume the Auth team member (Eric) will connect the real user session later
    dummy_owner_id = 1 
    
    try:
        # Create a new database record (Listing object)
        new_listing = Listing(
            title=title,
            author=author,
            course=course,
            condition=condition,
            description=description,
            owner_id=dummy_owner_id
        )
        
        # Add the new record to the database session and commit the transaction
        db.session.add(new_listing)
        db.session.commit()
        
        # Return success response with the newly created listing data
        return jsonify({
            "message": "Textbook uploaded successfully",
            "listing": new_listing.to_dict()
        }), 201
        
    except Exception as e:
        # Rollback the transaction in case of any database error
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Initialize the database tables before running the app
    with app.app_context():
        db.create_all()
    # Run the Flask development server on port 5000
    app.run(debug=True, port=5000)
