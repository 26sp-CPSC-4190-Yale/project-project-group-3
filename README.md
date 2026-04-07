[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/D8kToVOh)

# OpenShelf MVP

This repo now runs as one Flask app with:

- `/` for the landing page
- `/search` for textbook search
- `/search/<listing_id>` for listing details
- `/upload` for creating a listing that feeds the shared search experience

## Database setup

The app uses PostgreSQL with the schema in `schema.sql` and the sample data in `seed.sql`.

1. Install PostgreSQL.
2. Create the database:
   `sudo -u postgres createdb open_shelf_db`
3. Load the schema:
   `sudo -u postgres psql -d open_shelf_db -f schema.sql`
4. Seed sample data:
   `sudo -u postgres psql -d open_shelf_db -f seed.sql`

## App setup

1. Create and activate a virtual environment:
   `python3 -m venv .venv`
   `source .venv/bin/activate`
2. Install dependencies:
   `pip install -r requirements.txt`
3. Set your database connection if needed:
   `export DATABASE_URL=postgresql:///open_shelf_db`
4. Start the app:
   `python3 run.py`

## Notes

- Authentication UI exists on the landing page, but backend auth is not connected yet.
- The upload flow currently uses a placeholder `creator_id = 1` until auth is integrated.
- The current schema does not store free-form listing notes yet, so upload notes are collected but not saved.
