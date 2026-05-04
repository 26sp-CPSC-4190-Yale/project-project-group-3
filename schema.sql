DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversation_members CASCADE;
DROP TABLE IF EXISTS rooms CASCADE;
DROP TABLE IF EXISTS saved_listings CASCADE;
DROP TABLE IF EXISTS listings CASCADE;
DROP TABLE IF EXISTS books CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL, 
    email TEXT NOT NULL UNIQUE
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
    UNIQUE (user_id, listing_id), -- Prevents double saving
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE
);

-- conversations (1-on-1 or group)
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    listing_id INTEGER REFERENCES listings(id) ON DELETE SET NULL,
    is_group BOOLEAN NOT NULL DEFAULT FALSE,
    title TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- conversation members (who's in each conversation)
CREATE TABLE conversation_members (
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    last_read_at TIMESTAMP,
    PRIMARY KEY (conversation_id, user_id)
);

-- messages
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conv ON messages(conversation_id, created_at DESC);
CREATE INDEX idx_members_user ON conversation_members(user_id);
