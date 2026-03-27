[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/D8kToVOh)


# database branch
The database must be reconstructed on other peopl's device if you need to use it. Same for populating it along with the seed data. Instructions for doing so are to follow.

1. Download postgreSQL (on mac its pretty easy with homebrew but im not sure how to do it on windows)
2. run the following commands:
    createdb -U postgres open_shelf_db
    psql -U postgres -d open_shelf_db -f schema.sql
    psql -U postgres -d open_shelf_db -f seed.sql
3. Done! For testing, run the following command:
    psql -U postgres -d open_shelf_db
4. Then run any queries you want.
5. If at any point you want to reconstruct the table just run the following command followed by the commands in step 2:
    dropdb -U postgres open_shelf_db