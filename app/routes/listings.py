"""
Listings Flask blueprint for user profile and listing management
It handles rendering the user's profile dashboard (which displays saved & posted listings)
and provides endpoints for saving, unsaving, and deleting listings
"""
from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from app import db
from sqlalchemy import text

listings_bp = Blueprint('listings', __name__)

@listings_bp.route("/profile")
def profile_page():
    """
    Renders the user profile dashboard

    This function pulls the user's ID from the current session and fetches listings
    they have saved and have created
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
        FROM saved_listings s 
        JOIN listings l ON s.listing_id = l.id 
        JOIN books b ON l.book_id = b.id 
        WHERE s.user_id = :user_id 
        ORDER BY b.title ASC;
    """)
    saved_listings = db.session.execute(saved_query, {"user_id": user_id}).mappings().fetchall()

    # --- FETCH POSTED LISTINGS ---
    posted_query = text("""
        SELECT b.isbn, b.title, b.author, l.course, l.condition, l.id as listing_id
        FROM listings l 
        JOIN books b ON l.book_id = b.id 
        WHERE l.creator_id = :user_id 
        ORDER BY b.title ASC;
    """)
    posted_listings = db.session.execute(posted_query, {"user_id": user_id}).mappings().fetchall()

    return render_template(
        'profile.html', 
        saved_listings=saved_listings, 
        posted_listings=posted_listings
    )

@listings_bp.route('/save/<int:listing_id>', methods=['POST'])
def save_listing(listing_id):
    """
    Adds a listing to the user's saved items.
    """
    # Grab logged in user
    user_id = session.get('user_id')
    is_ajax = request.headers.get("Accept") == 'application/json'

    if not user_id:
        if is_ajax:
            return jsonify({"error": "Login required"}), 401
        flash("Please login to save listings.")
        return redirect(url_for("index"))

    try:
        db.session.execute(
            text("""
                INSERT INTO saved_listings (user_id, listing_id)
                VALUES (:user_id, :listing_id)
            """),
            {"user_id": user_id, "listing_id": listing_id}
        )
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        if is_ajax:
            return jsonify({"error": str(exc)}), 500
        flash("Could not save listing.")
        return redirect(request.referrer or url_for('search.listing_detail', listing_id=listing_id))

    if is_ajax:
        return jsonify({"success": True})
    return redirect(request.referrer or url_for('search.listing_detail', listing_id=listing_id))


@listings_bp.route('/unsave/<int:listing_id>', methods=["POST"])
def unsave_listing(listing_id):
    """
    Removes a listing from the user's saved items.
    """
    user_id = session.get('user_id')
    is_ajax = request.headers.get('Accept') == 'application/json'

    if not user_id:
        if is_ajax:
            return jsonify({"error": "Login required"}), 401
        flash("Please login.")
        return redirect(url_for("index"))

    db.session.execute(
        text("DELETE FROM saved_listings WHERE listing_id = :listing_id AND user_id = :user_id"),
        {"listing_id": listing_id, "user_id": user_id}
    )
    db.session.commit()

    if is_ajax:
        return jsonify({"success": True})
    flash("Listing removed from your saved items.")
    return redirect(request.referrer or url_for('listings.profile_page'))


@listings_bp.route('/delete/<int:listing_id>', methods=['POST'])
def delete_listing(listing_id):
    """
    Permanently deletes a listing that the user posted from the database.
    """
    user_id = session.get('user_id')
    is_ajax = request.headers.get("Accept") == "application/json"

    if not user_id:
        if is_ajax:
            return jsonify({"error": "Login required"}), 401
        return redirect(url_for("index"))

    try:
        # Verify ownership before deleting anything
        owner_check = db.session.execute(
            text("SELECT id FROM listings WHERE id = :lid AND creator_id = :uid"),
            {"lid": listing_id, "uid": user_id}
        ).first()

        if not owner_check:
            if is_ajax:
                return jsonify({"error": "Not found or unauthorized"}), 403
            return redirect(url_for("listings.profile_page"))

        # Delete the listing. 
        # (PostgreSQL ON DELETE CASCADE will automatically handle the saved_listings.
        # ON DELETE SET NULL will handle conversations pointing to this listing).
        db.session.execute(
            text("DELETE FROM listings WHERE id = :lid AND creator_id = :uid"),
            {"lid": listing_id, "uid": user_id}
        )

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"DATABASE ERROR during deletion: {str(e)}")
        if is_ajax:
            return jsonify({"error": "Deletion failed"}), 500
        return redirect(request.referrer or url_for("listings.profile_page"))

    if is_ajax:
        return jsonify({"success": True})
    return redirect(url_for("listings.profile_page"))