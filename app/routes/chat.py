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
    if not session.get("user_id"):
        return redirect(url_for("index"))

    username = session.get("username", "Anonymous")
    return render_template(
        "chat/room.html",
        listing_id=listing_id,
        username=username,
    )


# --------------- SocketIO event handlers ---------------
# These are registered on the shared `socketio` instance in __init__.py

def register_socket_events(socketio):
    """Register all chat-related SocketIO events."""

    @socketio.on("join")
    def handle_join(data):
        room = str(data.get("room"))
        username = data.get("username", "Anonymous")
        join_room(room)
        emit(
            "status",
            {"msg": f"{username} has entered the room."},
            to=room,
        )

    @socketio.on("leave")
    def handle_leave(data):
        room = str(data.get("room"))
        username = data.get("username", "Anonymous")
        leave_room(room)
        emit(
            "status",
            {"msg": f"{username} has left the room."},
            to=room,
        )

    @socketio.on("message")
    def handle_message(data):
        room = str(data.get("room"))
        emit(
            "message",
            {
                "username": data.get("username", "Anonymous"),
                "msg": data.get("msg", ""),
            },
            to=room,
        )
