from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from flask_socketio import emit, join_room, leave_room
from app import db
from sqlalchemy import text

"""
Chat Blueprint
Real-time chat using Flask-SocketIO with PostgreSQL persistence.

Model:
- conversations: a chat thread (1-on-1 or group). Optionally tied to a listing.
- conversation_members: who's in each conversation.
- messages: persisted history.

Each (buyer, seller, listing) tuple gets its own conversation, so a seller with
multiple interested buyers sees a separate thread per buyer.
"""

from flask import Blueprint, render_template, session, redirect, url_for, abort, request, jsonify
from flask_socketio import emit, join_room, leave_room
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app import db

chat_bp = Blueprint("chat", __name__)


# --------------- Helpers ---------------

def _find_or_create_1on1_conversation(user_a, user_b, listing_id):
    """Return conversation id between two users for a given listing.
    Creates one if none exists."""
    existing = db.session.execute(
        text(
            """
            SELECT c.id
            FROM conversations c
            JOIN conversation_members m1 ON m1.conversation_id = c.id AND m1.user_id = :a
            JOIN conversation_members m2 ON m2.conversation_id = c.id AND m2.user_id = :b
            WHERE c.is_group = FALSE
              AND c.listing_id IS NOT DISTINCT FROM :listing_id
            LIMIT 1
            """
        ),
        {"a": user_a, "b": user_b, "listing_id": listing_id},
    ).scalar()

    if existing:
        return existing

    conv_id = db.session.execute(
        text(
            """
            INSERT INTO conversations (listing_id, is_group)
            VALUES (:listing_id, FALSE)
            RETURNING id
            """
        ),
        {"listing_id": listing_id},
    ).scalar_one()

    db.session.execute(
        text(
            """
            INSERT INTO conversation_members (conversation_id, user_id)
            VALUES (:cid, :a), (:cid, :b)
            """
        ),
        {"cid": conv_id, "a": user_a, "b": user_b},
    )
    db.session.commit()
    return conv_id


def _user_in_conversation(user_id, conversation_id):
    return bool(
        db.session.execute(
            text(
                """
                SELECT 1 FROM conversation_members
                WHERE conversation_id = :cid AND user_id = :uid LIMIT 1
                """
            ),
            {"cid": conversation_id, "uid": user_id},
        ).first()
    )


# --------------- HTTP routes ---------------

@chat_bp.route("/chat")
def chat_list():
    """List all conversations the current user is in."""
    if not session.get("user_id"):
        return redirect(url_for("index"))

    user_id = session["user_id"]

    rows = db.session.execute(
        text(
            """
            SELECT
              c.id AS conversation_id,
              c.is_group,
              c.title,
              c.listing_id,
              b.title AS book_title,
              (
                SELECT u.username FROM conversation_members cm
                JOIN users u ON u.id = cm.user_id
                WHERE cm.conversation_id = c.id AND cm.user_id != :uid
                LIMIT 1
              ) AS counterpart_username,
              (
                SELECT string_agg(u.username, ', ') FROM conversation_members cm
                JOIN users u ON u.id = cm.user_id
                WHERE cm.conversation_id = c.id AND cm.user_id != :uid
              ) AS member_usernames,
              (
                SELECT COUNT(*) FROM conversation_members cm
                WHERE cm.conversation_id = c.id
              ) AS member_count,
              (
                SELECT m.body FROM messages m
                WHERE m.conversation_id = c.id
                ORDER BY m.created_at DESC LIMIT 1
              ) AS last_msg,
              (
                SELECT m.created_at FROM messages m
                WHERE m.conversation_id = c.id
                ORDER BY m.created_at DESC LIMIT 1
              ) AS last_at,
              (
                SELECT COUNT(*) FROM messages m
                WHERE m.conversation_id = c.id
                  AND m.sender_id != :uid
                  AND (cm_self.last_read_at IS NULL OR m.created_at > cm_self.last_read_at)
              ) AS unread_count
            FROM conversations c
            JOIN conversation_members cm_self
              ON cm_self.conversation_id = c.id AND cm_self.user_id = :uid
            LEFT JOIN listings l ON l.id = c.listing_id
            LEFT JOIN books b ON b.id = l.book_id
            ORDER BY last_at DESC NULLS LAST, c.created_at DESC
            """
        ),
        {"uid": user_id},
    ).mappings().all()

    return render_template("chat/list.html", conversations=rows)


@chat_bp.route("/chat/start/<int:listing_id>", methods=["POST", "GET"])
def chat_start(listing_id):
    """Find or create a 1-on-1 conversation between current user and listing seller."""
    if not session.get("user_id"):
        return redirect(url_for("index"))

    user_id = session["user_id"]

    listing = db.session.execute(
        text("SELECT id, creator_id FROM listings WHERE id = :lid"),
        {"lid": listing_id},
    ).mappings().first()

    if not listing:
        abort(404)

    seller_id = listing["creator_id"]
    if seller_id == user_id:
        return redirect(url_for("chat.chat_list"))

    conv_id = _find_or_create_1on1_conversation(user_id, seller_id, listing_id)
    return redirect(url_for("chat.conversation_room", conversation_id=conv_id))


@chat_bp.route("/chat/conversation/<int:conversation_id>")
def conversation_room(conversation_id):
    """Render the chat page for a specific conversation (loads history)."""
    if not session.get("user_id"):
        return redirect(url_for("index"))

    user_id = session["user_id"]

    if not _user_in_conversation(user_id, conversation_id):
        abort(403)

    conv = db.session.execute(
        text(
            """
            SELECT
              c.id, c.is_group, c.title, c.listing_id,
              b.title AS book_title,
              (
                SELECT u.username FROM conversation_members cm
                JOIN users u ON u.id = cm.user_id
                WHERE cm.conversation_id = c.id AND cm.user_id != :uid
                LIMIT 1
              ) AS counterpart_username,
              (
                SELECT string_agg(u.username, ', ') FROM conversation_members cm
                JOIN users u ON u.id = cm.user_id
                WHERE cm.conversation_id = c.id AND cm.user_id != :uid
              ) AS member_usernames
            FROM conversations c
            LEFT JOIN listings l ON l.id = c.listing_id
            LEFT JOIN books b ON b.id = l.book_id
            WHERE c.id = :cid
            """
        ),
        {"cid": conversation_id, "uid": user_id},
    ).mappings().first()

    history = db.session.execute(
        text(
            """
            SELECT m.id, m.body, m.created_at, u.username AS sender_username, m.sender_id
            FROM messages m
            LEFT JOIN users u ON u.id = m.sender_id
            WHERE m.conversation_id = :cid
            ORDER BY m.created_at ASC
            LIMIT 200
            """
        ),
        {"cid": conversation_id},
    ).mappings().all()

    db.session.execute(
        text(
            """
            UPDATE conversation_members
            SET last_read_at = NOW()
            WHERE conversation_id = :cid AND user_id = :uid
            """
        ),
        {"cid": conversation_id, "uid": user_id},
    )
    db.session.commit()

    return render_template(
        "chat/room.html",
        conversation=conv,
        history=history,
        username=session.get("username", "Anonymous"),
        current_user_id=user_id,
    )


@chat_bp.route("/api/users/search")
def api_search_users():
    """Search users by username prefix. Used by group-create modal."""
    if not session.get("user_id"):
        return jsonify({"users": []}), 401

    q = (request.args.get("q") or "").strip()
    if len(q) < 1:
        return jsonify({"users": []})

    rows = db.session.execute(
        text(
            """
            SELECT id, username
            FROM users
            WHERE username ILIKE :q AND id != :uid
            ORDER BY username
            LIMIT 8
            """
        ),
        {"q": f"{q}%", "uid": session["user_id"]},
    ).mappings().all()

    return jsonify({"users": [dict(r) for r in rows]})


@chat_bp.route("/api/conversations/group", methods=["POST"])
def api_create_group():
    """Create a new group conversation."""
    if not session.get("user_id"):
        return jsonify({"error": "Not authenticated"}), 401

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    member_ids = data.get("member_ids") or []

    if not title:
        return jsonify({"error": "Group name is required"}), 400
    if not isinstance(member_ids, list) or len(member_ids) < 1:
        return jsonify({"error": "Add at least one other member"}), 400

    creator_id = session["user_id"]
    all_member_ids = list({int(creator_id), *(int(m) for m in member_ids)})

    try:
        conv_id = db.session.execute(
            text(
                """
                INSERT INTO conversations (is_group, title)
                VALUES (TRUE, :title)
                RETURNING id
                """
            ),
            {"title": title},
        ).scalar_one()

        for uid in all_member_ids:
            db.session.execute(
                text(
                    """
                    INSERT INTO conversation_members (conversation_id, user_id)
                    VALUES (:cid, :uid)
                    """
                ),
                {"cid": conv_id, "uid": uid},
            )
        db.session.commit()
    except SQLAlchemyError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 500

    return jsonify({
        "conversation_id": conv_id,
        "redirect_url": url_for("chat.conversation_room", conversation_id=conv_id),
    }), 201


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

    @socketio.on("typing")
    def handle_typing(data):
        room = str(data.get("room"))
        emit(
            "typing",
            {
                "username": data.get("username", "Anonymous"),
                "sender_id": data.get("sender_id"),
            },
            to=room,
            include_self=False,
        )

    @socketio.on("stop_typing")
    def handle_stop_typing(data):
        room = str(data.get("room"))
        emit(
            "stop_typing",
            {"sender_id": data.get("sender_id")},
            to=room,
            include_self=False,
        )

    @socketio.on("message")
    def handle_message(data):
        try:
            conversation_id = int(data.get("room"))
        except (TypeError, ValueError):
            return

        sender_id = data.get("sender_id")
        body = (data.get("msg") or "").strip()
        if not body or not sender_id:
            return

        if not _user_in_conversation(sender_id, conversation_id):
            return

        row = db.session.execute(
            text(
                """
                INSERT INTO messages (conversation_id, sender_id, body)
                VALUES (:cid, :uid, :body)
                RETURNING id, created_at
                """
            ),
            {"cid": conversation_id, "uid": sender_id, "body": body},
        ).mappings().first()
        db.session.commit()

        emit(
            "message",
            {
                "id": row["id"],
                "username": data.get("username", "Anonymous"),
                "sender_id": sender_id,
                "msg": body,
                "created_at": row["created_at"].isoformat(),
            },
            to=str(conversation_id),
        )
