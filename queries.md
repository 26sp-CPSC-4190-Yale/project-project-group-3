File used for stories the queries to be used on the backend. Feel free to delete this file once you have finished implimentation.

# Login:

SELECT id FROM users WHERE email = ? AND password = ?;

Returns only the id, so im assuming no need to valdate login credentials. If you do want to double check the validation of login credentials then feel free to use this one which returns the entire row.

SELECT * FROM users WHERE email = ? AND password = ?;

# Account Creation:

## Query to check if any of the credentials are already in use:

SELECT id FROM users WHERE username = ? OR password = ? OR email = ?;

Only the id is returned to keep user anonymity. The person attempting to create an account should not be able to know any details for whoever they are overlapping with.

## query to add new user to the database

INSERT INTO users (username, password, email) VALUES (?);

'?' should be in the format `username, password, email`.

# Account Page:

## query to fetch all saved listings by the user

Assuming that the id of the user being logged in is stored and used in this query.

SELECT b.isbn, b.title, b.author, l.course, l.condition FROM users u INNER JOIN saved_listings s ON u.id = s.user_id INNER JOIN listings l ON s.listing_id = l.id INNER JOIN books b ON l.book_id = b.id WHERE u.id = ? ORDER BY b.title ASC;

'?' should be the id of the user who is currently logged in.

## query to remove saved listing ('unsave' it)

DELETE FROM saved_listings WHERE listing_id = ? AND user_id = ?;

The first '?' should be the id of the listing that the user wants to 'unsave'. The second '?' should be the id of the user who is currently logged in.

This query will only remove the associated row in the saved_listings table. No other tables will be affected.

## query to fetch all the listings posted by the user

SELECT b.isbn, b.title, b.author, l.course, l.condition FROM listings l INNER JOIN users u ON l.creator_id = u.id INNER JOIN books b ON l.book_id = b.id WHERE u.id = ? ORDER BY b.title ASC;

'?' should be the id of the user that is currently logged in.

## query to delete a listing owned by the user

DELETE FROM listings WHERE id = ?;

'?' should be the id of the listing that the owner wants to delete.

The database automatically updates and removes all assocaited rows in the saved_listings table, i.e rows that have the listing_id of '?', so there is no need for an additional query to do that.

# Upload Textbook

INSERT INTO books (isbn, title, author, publisher, edition) VALUES (?);

'?' should be a string in the format of `isbn, title, author, publisher, edition`.

# Textbook Listing Page

SELECT l.id, b.title, b.author, b.publisher, l.course, FROM listings l INNER JOIN books b ON l.book_id = b.id WHERE b.title ILIKE ? OR b.author ILIKE ? OR b.publisher ILIKE ? OR l.course ILIKE ?;

'?'s should be the fields of the form that were submitted. Let me know if there are formatting issues.

# Listing Information Page

## query to get the listing information

SELECT b.isbn, b.title, b.author, b.publisher, b.edition, l.course, l.condition, u.username FROM listings l INNER JOIN books b ON l.book_id = b.id INNER JOIN users u ON l.creator_id = u.id WHERE l.id = ?;

'?' should be the id of the listing that the user wants to view.

## query to add the currently viewed listing to the user's saved listings

INSERT INTO saved_listings (user_id, listing_id) VALUES (?);

'?' should be a string in the format of `user_id, listing_id`. Where user_id = the id of the currently logged in user, and listing id = the id of the listing that is currently being viewed.