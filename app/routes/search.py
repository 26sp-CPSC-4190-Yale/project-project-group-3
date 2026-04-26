"""
Search Blueprint
Handles all search-related routes

/search                 -> renders the search form
/search/results         -> queries the database, returns matching listings
/search/<listing_id>    -> shows full details for one listing

Update SQL queries 
"""

from flask import Blueprint, render_template, request, abort, session
from app import db
from sqlalchemy import text

search_bp = Blueprint("search", __name__)

"""
Route: Search form page
URL: GET /search
"""
@search_bp.route("/search")
def search_page():
    return render_template("search/search.html")

"""
Reads query parameters from the URL
URL: GET /api/search?q=<search_terms>&condition=<conditions_list>&course_code=<course_codes_list>&sort=<sort_filter>
Query params:
    q - the search term (e.g., "calculus", "CPSC 2230")
    field - which column to search: "all", "title", "isbn", "author", "course"
"""
@search_bp.route("/api/search")
def search():
    base_query = """
        SELECT l.id AS listing_id, l.course, l.condition, l.creator_id,
                b.isbn, b.title, b.author, b.publisher, b.edition,
                u.username AS posted_by
        FROM listings l 
        JOIN books b ON l.book_id=b.id
        JOIN users u ON l.creator_id = u.id
    """

    where_clauses = []
    params = {}

    # Text Search
    q = request.args.get("q", "").strip()
    if q:
        where_clauses.append("(b.isbn ILIKE :q OR b.title ILIKE :q OR b.author ILIKE :q OR l.course ILIKE :q)")
        params["q"] = f"%{q}%"

    # Condition Filters
    conditions = request.args.getlist("condition")
    if conditions:
        clean_conditions = tuple(c.lower() for c in conditions)
        where_clauses.append("LOWER(l.condition) IN :conditions")
        params["conditions"] = clean_conditions

    # Course Code Filters
    course_codes = request.args.getlist("course_code")
    if course_codes:
        code_clauses = []
        for i, code in enumerate(course_codes):
            param_key = f"code_{i}"
            code_clauses.append(f"l.course ILIKE :{param_key}")
            params[param_key] = f"{code}%"
        where_clauses.append(f"({' OR '.join(code_clauses)})")

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # Sorting
    sort_by = request.args.get("sort")
    order_sql = "ORDER BY b.title ASC" if sort_by == "az" else "ORDER BY l.id DESC"

    # Execute
    full_query = text(f"{base_query} {where_sql} {order_sql}")
    listings = db.session.execute(full_query, params).mappings().all()

    saved_ids = []
    if session.get('user_id'):
        saved_query = text("SELECT listing_id FROM saved_listings WHERE user_id = :user_id")
        result = db.session.execute(saved_query, {"user_id": session.get('user_id')}).mappings().all()
        saved_ids = [row["listing_id"] for row in result]

    return render_template("search/partials/listing_items.html", listings=listings, saved_ids=saved_ids)

"""
Route: Single listing detail
URL: GET /search/<int:listing_id>

Shows full information about one specific listing
"""
@search_bp.route("/search/<int:listing_id>")
def listing_detail(listing_id):

    # query for one listing by primary key
    query = text("""
        SELECT l.id AS listing_id,
               l.creator_id,
               l.course,
               l.condition,
               b.isbn,
               b.title,
               b.author,
               b.publisher,
               b.edition,
               u.username AS posted_by
        FROM listings l
        JOIN books b ON l.book_id = b.id
        JOIN users u ON l.creator_id = u.id
        WHERE l.id = :lid
    """)
    
    result = db.session.execute(query, {"lid": listing_id})
    listing = result.mappings().first()

    # 404 if listing doesn't exist
    if listing is None:
        abort(404)

    return render_template(
        "search/detail.html", 
        listing=listing
    )