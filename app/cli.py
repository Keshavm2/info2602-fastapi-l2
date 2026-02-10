import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from typing import Annotated

cli = typer.Typer()

@cli.command()
def initialize():
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User('bob', 'bob@mail.com', 'bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")

"Retrieve a user by their username"
@cli.command()
def get_user(username: Annotated[str, typer.Argument(help="The username of the user to retrieve")]):
    with get_session() as db: 
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print(user)

"Get all users in the database."
@cli.command()
def get_all_users():
    with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
        else:
            for user in all_users:
                print(user)

"Change the email of a user by their username."
@cli.command()
def change_email(username: Annotated[str, typer.Argument(help="The username of the user to update")],
                new_email: Annotated[str, typer.Argument(help="The new email address for the user")]):
    with get_session() as db: 
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {user.username}'s email to {user.email}")

"Create a new user with a username, email and password"
@cli.command()
def create_user(username: Annotated[str, typer.Argument(help="The username of the user to update")],
                new_email: Annotated[str, typer.Argument(help="The new email address for the user")],
                password: Annotated[str, typer.Argument(help="The password for the new user")]):
    with get_session() as db: 
        newuser = User(username, email, password)
        try:
            db.add(newuser)
            db.commit()
        except IntegrityError as e:
            db.rollback() 
            print("Username or email already taken!") 
        else:
            print(newuser) 

"Delete a user by their username"
@cli.command()
def delete_user(username: Annotated[str, typer.Argument(help="The username of the user to delete")]):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to delete user.')
            return
        db.delete(user)
        db.commit()
        print(f'{username} deleted') 

"Search for users by a partial match on their username or email"
@cli.command()
def partial_match(search: Annotated[str, typer.Argument(help="The partial username or email to search for")]):
    with get_session() as db:
        users = db.exec(select(User).where(User.username.contains(search)| User.email.contains(search))).all()

        if not users:
            print("User not found")
        else:
            for user in users:
                print(user)

"Get a paginated list of users"
@cli.command()
def first_users( limit: Annotated[int, typer.Argument(help="Number of users to return (default 10)")] = 10,
                 offset: Annotated[int, typer.Argument(help="Number of users to skip (default 0)")] = 0):
    with get_session() as db:
        users = db.exec(select(User).offset(offset).limit(limit)).all()
        if not users:
            print("User not found")
        else:
            for user in users:
                print(user)


if __name__ == "__main__":    cli()