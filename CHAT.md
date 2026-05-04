# Chat Feature

Real-time messaging between buyers and sellers, with persistent history, group conversations, unread tracking, and typing indicators.

---

## Stack

- **Server**: Flask + Flask-SocketIO (5.6.1)
- **Database**: PostgreSQL (3 new tables)
- **Transport**: WebSocket with HTTP long-polling fallback
- **Client**: Vanilla JavaScript + Socket.IO 4.7.5 (CDN)

---

## Database Schema

Three new tables in `schema.sql`:

| Table | Columns | Purpose |
|---|---|---|
| `conversations` | `id`, `listing_id`, `is_group`, `title`, `created_at` | A chat thread (1-on-1 or group). Optionally tied to a listing. |
| `conversation_members` | `conversation_id`, `user_id`, `last_read_at` | Junction table linking users to conversations. `last_read_at` powers unread tracking. |
| `messages` | `id`, `conversation_id`, `sender_id`, `body`, `created_at` | Persisted message history. Indexed on `(conversation_id, created_at DESC)` for fast scrollback. |

### Design decision: one conversation per (buyer, seller, listing) tuple

A single listing may attract multiple interested buyers. Each buyer-seller pair gets its own conversation, so messages don't get mixed across buyers. Group chats are independent of any listing.

---

## Routes

| Method | Path | Behavior |
|---|---|---|
| `GET` | `/chat` | Renders the conversation list page. Shows all conversations the current user belongs to, with last-message preview and unread count. |
| `GET` | `/chat/start/<listing_id>` | Idempotently finds-or-creates a 1-on-1 conversation between current user and listing seller, then redirects. Returns to chat list if user owns the listing. |
| `GET` | `/chat/conversation/<conv_id>` | Renders the chat room: loads up to the last 200 messages, marks the conversation as read, opens a Socket.IO connection. Returns 403 if user is not a member. |
| `GET` | `/api/users/search?q=<prefix>` | Returns up to 8 users whose `username` starts with the given prefix. Used by the group-creation modal. |
| `POST` | `/api/conversations/group` | Creates a group conversation. Body: `{title, member_ids[]}`. Inserts the creator and all members into `conversation_members`. |

---

## Socket.IO Events

| Event | Direction | Behavior |
|---|---|---|
| `join` | Client → Server | Subscribes the socket to a conversation room. |
| `leave` | Client → Server | Unsubscribes the socket from the room. |
| `message` | Client ↔ Server | Server validates membership, persists to `messages`, broadcasts to all sockets in the room. |
| `typing` | Client ↔ Server | Server relays a "user is typing" notice to other room members (`include_self=False`). |
| `stop_typing` | Client ↔ Server | Server relays the "stop typing" signal so the indicator can be cleared. |

### Server-side membership check

Every `message` event runs `_user_in_conversation(sender_id, conversation_id)` against the database before broadcasting. Non-members are silently rejected — clients cannot inject messages into conversations they do not belong to.

---

## Features

### 1. Message persistence
All messages are stored in the `messages` table. Reloading the page restores the full history (up to 200 most recent messages, ordered oldest-first).

### 2. Conversation list (`/chat`)
A "Messages" page accessible from the bottom navigation bar. Each row shows:
- Avatar with the counterpart's initials (or 👥 for groups)
- Listing context tag (book title) when the conversation is tied to a listing
- Last message preview
- Timestamp of the last activity
- Unread count badge (if any)

Sorted by most recent activity first.

### 3. Buyer-seller chat
The listing detail page exposes a **"Chat seller"** button (visible only to logged-in users who do not own the listing). Clicking it routes to `/chat/start/<listing_id>`, which transparently creates the conversation if it doesn't already exist and redirects to the room.

### 4. Group chat
The `/chat` page has a **"+ New group"** button that opens a modal:
- Enter a group title
- Search users by username prefix
- Add members as removable chips
- Submit creates the group and redirects to the new room

The group room header shows the group title and a comma-separated member list.

### 5. Unread tracking
Each `conversation_members` row stores `last_read_at`. When the user opens a conversation, this timestamp is updated to `NOW()`. The unread count for a conversation is then:

```sql
SELECT COUNT(*) FROM messages
WHERE conversation_id = :cid
  AND sender_id != :uid
  AND (last_read_at IS NULL OR created_at > last_read_at)
```

A Flask `context_processor` (`inject_unread_count`) computes the *total* unread across all conversations for the current user. This value is exposed to all templates as `unread_count`, and is rendered as a coral red badge on the bottom-nav **Chats** button across the entire app.

### 6. Typing indicator
While typing, the client sends a debounced `typing` event (1.5-second timeout). Other room members see "*username is typing...*" in italic gray text above their input box. After 1.5 seconds of inactivity, the client sends `stop_typing` and the indicator clears.

---

## File Layout

```
app/
├── __init__.py                     # SocketIO init, unread context processor
├── routes/
│   └── chat.py                     # Blueprint, HTTP routes, Socket.IO event handlers
├── templates/
│   └── chat/
│       ├── list.html               # Conversation list + group-create modal
│       └── room.html               # Chat room with history, typing indicator, real-time updates
├── static/
│   └── frontend/
│       └── styles.css              # .nav-badge style for unread indicator
└── templates/                      # All other pages updated to include "Chats" tab in bottom nav
schema.sql                          # New: conversations, conversation_members, messages
requirements.txt                    # Added Flask-SocketIO, python-socketio, python-engineio
run.py                              # Uses socketio.run() instead of app.run()
```

---

## Running Locally

```bash
# 1. Make sure PostgreSQL is running and the database exists
createdb open_shelf_db
psql -d open_shelf_db -f schema.sql

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the app (uses Socket.IO server)
python run.py
# -> http://127.0.0.1:5002
```

---

## Manual Test Plan

To exercise real-time behavior you need two logged-in users at once. Open two browsers (or one normal + one Incognito window).

| # | Test | Steps | Expected |
|---|---|---|---|
| 1 | Create conversation | Buyer opens a listing detail page, clicks **Chat seller** | Redirects to `/chat/conversation/<id>`; conversation appears in seller's `/chat` page |
| 2 | Real-time delivery | Both users open the same conversation; one sends a message | Other window receives it instantly without refresh |
| 3 | Persistence | Close and re-open the conversation | Full history is restored |
| 4 | Unread badge | Window A sends message, Window B does not open the conversation | Bottom-nav **Chats** button on Window B shows a red badge with the count |
| 5 | Mark as read | Window B opens the conversation | Badge disappears, last_read_at updated |
| 6 | Typing indicator | Window A starts typing in the input | Window B sees "*A is typing...*" within ~100ms; clears 1.5s after A stops |
| 7 | Group chat | On `/chat` page, click **+ New group**, name it, add 2+ members, submit | Redirects to new group room; all members see the group in their `/chat` list |
| 8 | Membership guard | Use socket dev tools to emit a `message` for a conversation the user is not in | Server silently drops the event, no broadcast occurs |

---

## Known Limitations

- **No file/image attachments** — text-only messages.
- **No message editing or deletion** — once sent, a message is permanent.
- **No push notifications** — unread state is visible only when the user is browsing the app.
- **No online/offline presence** — typing indicators are the only liveness signal.
- **History capped at 200 messages per page load** — older messages are not paginated yet.
