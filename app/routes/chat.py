from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from flask_socketio import emit, join_room, leave_room
from app import db
from sqlalchemy import text

"""
Chat Blueprint
Primitive real-time chat using Flask-SocketIO.
No message persistence — messages live only in the browser session.

Each listing has its own chat "room" identified by the listing ID.
Users join a room when they open the chat page and leave when they navigate away.
"""

from flask import Blueprint, render_template, session, redirect, url_for
from flask_socketio import emit, join_room, leave_room

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat/<int:listing_id>")
def chat_room(listing_id):
    """Render the chat page for a specific listing."""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("index"))
    
    # Get the listing to find teh seller
    listing = db.session.execute(
        text("SELECT creator_id FROM listings WHERE id = :lid"),
        {"lid": listing_id}
    ).mappings().first()

    if not listing:
        return redirect(url_for("search.search_page"))
    
    creator_id = listing["creator_id"]
    
    # Determine the room based on Buyer v. Seller
    if user_id == creator_id:
        # Seller is viewing: Read the buyer id from the URL
        buyer_id_raw = request.args.get("buyer_id")
        buyer_id = None
        if buyer_id_raw:
            try:
                buyer_id = int(buyer_id_raw)
            except ValueError:
                return redirect(url_for("search.search_page"))

        if buyer_id:
            room = db.session.execute(
                text("SELECT id FROM rooms WHERE listing_id = :lid AND buyer_id = :bid"),
                {"lid": listing_id, "bid": buyer_id}
            ).mappings().first()
        else:
            # Fallback if no buyer clicked
            room = db.session.execute(
                text("SELECT id FROM rooms WHERE listing_id = :lid ORDER BY id DESC LIMIT 1"),
                {"lid": listing_id}
            ).mappings().first()

        if not room:
            flash("No one has messaged you about this listing yet")
            return redirect(request.referrer or url_for("search.search_page"))
        room_id = room["id"]

    else:
        # Buyer is viewing, find existing room, or create new one
        room = db.session.execute(
            text("SELECT id FROM rooms WHERE listing_id = :lid AND buyer_id = :bid"),
            {"lid": listing_id, "bid": user_id}
        ).mappings().first()

        if room:
            room_id = room["id"]
        else:
            room_id = db.session.execute(
                text("INSERT INTO rooms (listing_id, buyer_id) VALUES (:lid, :bid) RETURNING id"),
                {"lid": listing_id, "bid": user_id}
            ).scalar_one()
            db.session.commit()

    # Fetch message history
    messages = db.session.execute(
        text("""
            SELECT m.id, m.content, m.is_read, m.sender_id, u.username
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.room_id = :rid
            ORDER BY m.created_at ASC
        """),
        {"rid": room_id}
    ).mappings().fetchall()

    # Find the very first unread message from the OTHER person
    first_unread_id = None
    for m in messages:
        if m['is_read'] is False and m['sender_id'] != user_id:
            first_unread_id = m['id']
            break

    # Message break found, mark them all as read in the DB
    db.session.execute(
        text("""
            UPDATE messages 
            SET is_read = TRUE 
            WHERE room_id = :rid AND sender_id != :uid AND is_read = FALSE
        """),
        {"rid": room_id, "uid": user_id}
    )
    db.session.commit()

    username = session.get("username", "Anonymous")
    return render_template(
        "chat/room.html",
        listing_id=listing_id,
        room_id=room_id, 
        username=username,
        messages=messages,
        first_unread_id=first_unread_id
    )

@chat_bp.route("/api/unread")
def get_global_unread():
    """live-updating the notification badge."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"count": 0})
        
    count = db.session.execute(text("""
        SELECT COUNT(m.id)
        FROM messages m
        JOIN rooms r ON m.room_id = r.id
        JOIN listings l ON r.listing_id = l.id
        WHERE m.is_read = FALSE
        AND m.sender_id != :uid
        AND (r.buyer_id = :uid OR l.creator_id = :uid)
    """), {"uid": user_id}).scalar_one_or_none() or 0
    
    return jsonify({"count": count})

@chat_bp.route("/api/listing/<int:listing_id>/unread")
def listing_unread(listing_id):
    """Background endpoint to get live unread counts for a specific listing's chat buttons."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    listing = db.session.execute(
        text("SELECT creator_id FROM listings WHERE id = :lid"),
        {"lid": listing_id}
    ).mappings().first()

    if not listing:
        return jsonify({"error": "Not found"}), 404

    if user_id == listing["creator_id"]:
        # SELLER: Return a dictionary of {buyer_id: unread_count}
        rooms = db.session.execute(
            text("""
                SELECT r.buyer_id,
                       COALESCE(SUM(CASE WHEN m.is_read = FALSE AND m.sender_id = r.buyer_id THEN 1 ELSE 0 END), 0) AS unread_count
                FROM rooms r
                LEFT JOIN messages m ON m.room_id = r.id
                WHERE r.listing_id = :lid
                GROUP BY r.buyer_id
            """),
            {"lid": listing_id}
        ).mappings().all()
        
        return jsonify({
            "role": "seller", 
            "buyers": {str(row["buyer_id"]): int(row["unread_count"]) for row in rooms}
        })
    else:
        # BUYER: Return just the count of unread messages from the seller
        unread_count = db.session.execute(
            text("""
                SELECT COALESCE(SUM(CASE WHEN m.is_read = FALSE AND m.sender_id = :seller_id THEN 1 ELSE 0 END), 0)
                FROM rooms r
                JOIN messages m ON m.room_id = r.id
                WHERE r.listing_id = :lid AND r.buyer_id = :uid
            """),
            {"lid": listing_id, "uid": user_id, "seller_id": listing["creator_id"]}
        ).scalar() or 0
        
        return jsonify({"role": "buyer", "unread_count": int(unread_count)})

# --------------- SocketIO event handlers ---------------

def register_socket_events(socketio):
    """Register all chat-related SocketIO events."""

    @socketio.on("join")
    def handle_join(data):
        room = str(data.get("room"))
        join_room(room)

    @socketio.on("leave")
    def handle_leave(data):
        room = str(data.get("room"))
        leave_room(room)

    @socketio.on("message")
    def handle_message(data):
        room_id = data.get("room")
        msg = data.get("msg", "").strip()
        user_id = session.get("user_id")
        username = session.get("username", "Anonymous")

        if not user_id or not msg or not room_id:
            return
        
        # Save to database
        db.session.execute(
            text("INSERT INTO messages (room_id, sender_id, content) VALUES (:rid, :uid, :msg)"),
            {"rid": room_id, "uid": user_id, "msg": msg}
        )
        db.session.commit()

        # Broadcast to everyone in room
        emit("message", {"username": username, "msg": msg}, to=str(room_id))
