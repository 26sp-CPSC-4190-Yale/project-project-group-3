-- users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL, -- encrypted
    email TEXT NOT NULL
);

-- books
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    publisher TEXT NOT NULL,
    edition TEXT NOT NULL
);

-- listings
CREATE TABLE listings (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL,
    creator_id INTEGER NOT NULL,
    course TEXT NOT NULL,
    condition TEXT NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE
);

-- saved listings
CREATE TABLE saved_listings (
    user_id INTEGER NOT NULL,
    listing_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE
);

-- chat rooms (conversations)
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    listing_id INTEGER NOT NULL,
    buyer_id INTEGER NOT NULL,
    UNIQUE (listing_id, buyer_id),
    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE
);

-- conversation members (stores participants of conversations)
CREATE TABLE conversation_members (
    room_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- messages, stores each message and the context where it was sent
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE
);
