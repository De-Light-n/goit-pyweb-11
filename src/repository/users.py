from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.entity.models import User
from src.schemas.users import UserShema

async def create_user(body: UserShema, db:AsyncSession = Depends(get_db)):
    """
    The function `create_user` creates a new user in a database with an optional Gravatar avatar based
    on the provided user data.
    
    Args:
      body (UserShema): The `body` parameter in the `create_user` function is of type `UserSchema`,
    which likely contains information about the user being created, such as their name, email, and any
    other relevant details.
      db (AsyncSession): The `db` parameter in the `create_user` function is an instance of an
    asynchronous database session. It is used to interact with the database to add a new user record,
    commit the changes, and refresh the session with the newly added user.
    
    Returns:
      The function `create_user` is returning the newly created user object after adding it to the
    database, committing the changes, and refreshing the object from the database.
    """
    
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def update_token(user:User, token:str|None, db:AsyncSession):
    """
    This Python async function updates the refresh token for a user in a database session.
    
    Args:
      user (User): User object representing a user in the system
      token (str|None): The `token` parameter is a string that represents the new refresh token for the
    user. It can also be `None` if the user wants to remove the refresh token.
      db (AsyncSession): The `db` parameter is an asynchronous session object that allows you to
    interact with the database in an asynchronous manner. In this context, it is used to commit the
    changes made to the `user` object's refresh token to the database.
    """
    
    user.refresh_token = token
    await db.commit()
    
async def get_user_by_email(email:str, db:AsyncSession = Depends(get_db)):
    """
    The function `get_user_by_email` retrieves a user from the database based on their email address.
    
    Args:
      email (str): The `email` parameter is a string that represents the email address of the user you
    want to retrieve from the database.
      db (AsyncSession): The `db` parameter is an instance of an asynchronous database session that is
    used to interact with the database. In this case, it is obtained using the `get_db` dependency,
    which likely sets up the database connection and session for the function to use. The
    `get_user_by_email` function
    
    Returns:
      The function `get_user_by_email` is returning a user object based on the email provided. If a user
    with the specified email exists in the database, that user object will be returned. If no user is
    found with the given email, the function will return `None`.
    """
    
    stmt = select(User).filter(User.email == email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user

async def update_avatar(email, url: str, db: AsyncSession) -> User:
    """
    This async function updates the avatar URL for a user in a database based on their email.
    
    Args:
      email: The `email` parameter is a string representing the email address of the user whose avatar
    you want to update.
      url (str): The `url` parameter in the `update_avatar` function is a string that represents the new
    avatar URL that will be assigned to the user with the specified email address.
      db (AsyncSession): The `db` parameter in the `update_avatar` function is an instance of an
    asynchronous database session (`AsyncSession`). This parameter is used to interact with the database
    to update the user's avatar URL.
    
    Returns:
      The function `update_avatar` returns a `User` object after updating the avatar URL for the user
    with the specified email in the database.
    """
    
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    return user

async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    This function confirms a user's email address in a database by updating the user's confirmation
    status to True.
    
    Args:
      email (str): The `email` parameter is a string that represents the email address of the user whose
    email confirmation status needs to be updated.
      db (AsyncSession): The `db` parameter is an asynchronous session object that is used to interact
    with the database. It allows you to perform database operations such as querying, updating, and
    committing data in an asynchronous manner. In this context, it is being used to retrieve a user by
    email, update the user's confirmation
    """
    
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()