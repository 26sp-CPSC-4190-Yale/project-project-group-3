"""
Search Blueprint
Handles all search-related routes

/search                 -> renders the search form
/search/results         -> queries the database, returns matching listings
/search/<listing_id>    -> shows full details for one listing

Update SQL queries 
"""

from flask import Blueprint, render_template, request, abort
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
URL: GET /search/results?q=<search_terms>&field=<field_name>
Query params:
    q - the search term (e.g., "calculus", "CPSC 2230")
    field - which column to search: "all", "title", "isbn", "author", "course"
"""
@search_bp.route("/search/results")
def search_results():
    # read the query params
    q = request.args.get("q", "").strip()
    field = request.args.get("field", "all")

    # guard empty searches
    if not q:
        return render_template("search/results.html", listings=[], query=q)
    
    # query builder
    like = f"%{q}%"

    base_query = """
        SELECT  l.id AS listing_id,
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
    """

    if field == "isbn":
        where = "WHERE b.isbn ILIKE :q" 
    elif field == "title":
        where = "WHERE b.title ILIKE :q"
    elif field == "author":
        where = "WHERE b.author ILIKE :q"
    elif field == "course":
        where = "WHERE l.course ILIKE :q"
    else:
        where = """
            WHERE b.isbn ILIKE :q
            WHERE b.title ILIKE :q
            WHERE b.author ILIKE :q
            OR l.course ILIKE :q
        """

    order = "ORDER BY l.id DESC"

    full_query = text(f"{base_query} {where} {order}")

    result = db.session.execute(full_query, {"q": like})
    listings = result.mappings().all

    return render_template("search/results.html", listings=listings, query=q)

"""
Route: Signle listing detail
URL: GET /search/<int:listing_id>

Shows full information about one specific listing
"""
@search_bp.route("/search/<int:listing_id>")
def listing_detail(listing_id):

    # query for one listing by primary key
    query = text("""
        SELECT l.id       AS listing_id,
                    l.course,
                    l.condition,
                    b.isbn,
                    b.title,
                    b.author,
                    b.publisher,
                    b.edition,
                    u.username AS posted_by
                FROM listings l
                JOIN books b ON l.book_id    = b.id
                JOIN users u ON l.creator_id = u.id
                WHERE l.id = :lid
                 """)
    
    result = db.session.execute(query, {"lid": listing_id})
    listing = result.mappings.first()

    # 404 if listing doesn't exist
    if listing is None:
        abort(404)

    return render_template("search/detail.html", listing=listing)
