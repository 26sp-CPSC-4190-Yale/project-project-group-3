-- users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
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
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE SET NULL,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE SET NULL
);

-- saved listings
CREATE TABLE saved_listings (
    user_id INTEGER NOT NULL,
    listing_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE
)