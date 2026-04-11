"""
Listings Flask blueprintfor user profile and listing management
It handles rendering teh user's profile dashboaard (which displays saved & posted listings)
and provides endpoints for saving, unsaving, and deleting listings
"""
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app import db
from sqlalchemy import text

listings_bp = Blueprint('listings', __name__)

@listings_bp.route("/profile")
def profile_page():
    """
    Renders the user profile dashboard

    This function pulls the user's ID from the current session and fetches listings
    they have have saved and have creatd
    """
    # Retrieve the 'user_id' from the Flask session dictionary
    user_id = session.get('user_id')

    # Check if the user_id exists.
    if not user_id:
        flash("You must be logged in to view this page.")
        return redirect(url_for("index"))
    
    # --- FETCH SAVED LISTINGS ---
    saved_query = text("""
        SELECT b.isbn, b.title, b.author, l.course, l.condition, l.id as listing_id 
        FROM users u 
        INNER JOIN saved_listings s ON u.id = s.user_id 
        INNER JOIN listings l ON s.listing_id = l.id 
        INNER JOIN books b ON l.book_id = b.id 
        WHERE u.id = :user_id 
        ORDER BY b.title ASC;
    """)

    saved_listings = db.session.execute(saved_query, {"user_id": user_id}).mappings().fetchall()

    # --- FETCH POSTED LISTINGS ---
    posted_query = text("""
        SELECT b.isbn, b.title, b.author, l.course, l.condition, l.id as listing_id 
        FROM listings l 
        INNER JOIN users u ON l.creator_id = u.id 
        INNER JOIN books b ON l.book_id = b.id 
        WHERE u.id = :user_id 
        ORDER BY b.title ASC;
    """)

    posted_listings = db.session.execute(posted_query, {"user_id": user_id}).mappings().fetchall()

    return render_template('profile.html', saved_listings=saved_listings, posted_listings=posted_listings)

@listings_bp.route('/save/<int:listing_id>', methods=['POST'])
def save_listing(listing_id):
    """
    Adds a listing to the user's saved items.
    """
    # Grab logged in user
    user_id = session.get('user_id')

    # Check if the user_id exists.
    if not user_id:
        flash("Please login to save listings.")
        return redirect(url_for("index"))
    
    insert_query = text("""
        INSERT INTO saved_listings (user_id, listing_id) 
        VALUES (:user_id, :listing_id);
    """)

    try:
        db.session.execute(insert_query, {"user_id": user_id, "listing_id": listing_id})

        db.session.commit()

        flash("Listing saved successfully!")
    except Exception as exc:
        db.session.rollback()

        flash("Could not save listing. It may already be saved")

    return redirect(request.referrer or url_for('search.listing_detail', listing_id=listing_id))


@listings_bp.route('/unsave/<int:listing_id>', methods=["POST"])
def unsave_listing(listing_id):
    """
    Removes a listing from the user's saved items.
    """
    # Grab logged in user
    user_id = session.get('user_id')

    # Check if the user_id exists.
    if not user_id:
        flash("Please login to save listings.")
        return redirect(url_for("index"))
    
    unsave_query = text("""
        DELETE FROM saved_listings 
        WHERE listing_id = :listing_id AND user_id = :user_id;
    """)

    db.session.execute(unsave_query, {"listing_id":  listing_id, "user_id": user_id})
    db.session.commit()
    flash("Listing removed from your saved items.")
    return redirect(request.referrer or url_for('listings.profile_page'))

@listings_bp.route('/delete/<int:listing_id>', methods=['POST'])
def delete_listing(listing_id):
    """
    Permanently deletes a listing that the user posted from the database.
    """
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for("index"))
    
    try:
        db.session.execute(
            text("DELETE FROM saved_listings WHERE listing_id = :listing_id"), 
            {"listing_id": listing_id}
        )

        delete_query = text("""
            DELETE FROM listings 
            WHERE id = :listing_id AND creator_id = :user_id;
        """)
        result = db.session.execute(delete_query, {"listing_id": listing_id, "user_id": user_id})
        
        db.session.commit()
        
        print(f"SUCCESS: Deleted {result.rowcount} listing(s) from the database.")

    except Exception as e:
        db.session.rollback()
        print(f"DATABASE ERROR during deletion: {str(e)}")

    return redirect(url_for("listings.profile_page"))
