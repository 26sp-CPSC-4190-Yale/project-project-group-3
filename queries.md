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

# Chat Pages

## query to create the chat room

INSERT INTO rooms (listing_id, buyer_id) VALUES (?);

'?' should be a string in the form of `listing_id, buyer_id`. listing_id = the id of the listing that the users are discussing, and buyer_id = the user who is interested in getting the books on the listing. 

(only create the chat room if it doesn't exist)

## query to see if a room already exists

SELECT id FROM rooms WHERE listing_id = ? AND buyer_id = ?;

The first '?' should be the id of the listing the user wants to inquire about. The 2nd '?' should be the id of the user interested in the listing.

## query to add users to a conversation

INSERT INTO conversation_members (room_id, user_id) VALUES (?);

'?' should be a string in the format of `room_id, user_id`. room_id should be the id of the chatroom that the user is in. user_id should be the id of the current user (note that both the user interested in the lsiting and the user who posted the listing will each have a row in the conversation_members table).

## query to get the users in a specific conversation

SELECT user_id FROM conversation_members WHERE room_id = ?;

'?' should be the id of the room that is being connected to.

## query to retrieve all messages sent in a room

SELECT sender_id, content, created_at FROM messages WHERE room_id = ?;

'?' should be the id of the current room.

## query to add a message into the messages table

INSERT INTO messages (room_id, sender_id, content) VALUES (?);

'?' should be a string in the format of `room_id, sender_id, content`. You know the drill for room_id. Sender_id should be the id of the user who sent the message. Content should be the text of what they send. Feel free to impose a character limit on content. 

Note: while the table also has a created_at field, this is automatically updated whenever a new row is added, so no need to add that in with this query.