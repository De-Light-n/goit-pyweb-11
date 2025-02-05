from typing import Optional
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Request,
    status,
    Depends,
    HTTPException,
    Query,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter

from src.schemas.users import *
from src.repository import users as repository_users
from src.database.db import get_db
from src.services.auth import auth_service
from src.services.email import send_email


router = APIRouter(prefix="/auth", tags=["auth"])
get_refresh_token = HTTPBearer()


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def signup(
    body: UserShema,
    bt: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    The `signup` function checks if a user already exists by email, creates a new user if not, and sends
    a confirmation email.
    
    Args:
      body (UserShema): The `body` parameter in the `signup` function represents the data of the user
    that is being signed up. It is expected to be of type `UserSchema`, which likely contains
    information such as the user's email, password, and other relevant details needed for creating a new
    user account.
      bt (BackgroundTasks): BackgroundTasks is a class provided by FastAPI that allows you to schedule
    background tasks to be run after a response is returned to the client. In the provided code snippet,
    the `bt` parameter is an instance of the BackgroundTasks class that is used to schedule the
    `send_email` task to be
      request (Request): The `request` parameter in the `signup` function is of type `Request`. It is
    used to access information about the incoming HTTP request, such as headers, cookies, and query
    parameters. In this context, it is being used to access the base URL of the incoming request using
    `request.base
      db (AsyncSession): The `db` parameter in the `signup` function is an `AsyncSession` object that
    represents an asynchronous database session. It is obtained as a dependency using the `get_db`
    function. This parameter is used to interact with the database to check if a user already exists,
    create a new user
    
    Returns:
      The `signup` function is returning the newly created user object after successfully creating a new
    user in the database.
    """
    user_exists = await repository_users.get_user_by_email(body.email, db)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return new_user


@router.post(
    "/login",
    response_model=TokenShema,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    The `login` function in Python handles user authentication by verifying credentials and generating
    access and refresh tokens.
    
    Args:
      body (OAuth2PasswordRequestForm): The `body` parameter in the `login` function is of type
    `OAuth2PasswordRequestForm`, which is likely a data model representing the username and password
    entered during the login process. It is being used to extract the username and password for
    authentication.
      db (AsyncSession): The `db` parameter in the `login` function is an AsyncSession dependency
    obtained using the `get_db` function. This parameter represents the database session that will be
    used to interact with the database within the scope of the `login` function. It is typically used to
    perform database operations like querying
    
    Returns:
      The `login` function returns a dictionary containing the access token, refresh token, and token
    type. The structure of the returned dictionary is as follows:
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get(
    "/confirmed_email/{token}",
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    This function confirms a user's email if it has not been confirmed already.
    
    Args:
      token (str): A string representing the token used for email verification.
      db (AsyncSession): The `db` parameter in the `confirmed_email` function is an instance of an
    asynchronous database session. It is used to interact with the database to perform operations like
    querying user data and updating the user's email confirmation status. In this case, it is obtained
    using the `get_db` dependency function
    
    Returns:
      a message indicating whether the email confirmation was successful or not. If the user's email is
    already confirmed, it will return a message stating "Your email is already confirmed". If the email
    was successfully confirmed during the function execution, it will return a message saying "Email
    confirmed".
    """
    
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/refresh_token", response_model=TokenShema)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
    db: AsyncSession = Depends(get_db),
):
    """
    This Python async function refreshes a user's access token and refresh token based on a provided
    refresh token.
    
    Args:
      credentials (HTTPAuthorizationCredentials): The `credentials` parameter in the `refresh_token`
    function is of type `HTTPAuthorizationCredentials` and is obtained by calling the
    `get_refresh_token` dependency. It represents the authorization credentials (token) provided in the
    request header for refreshing the access token.
      db (AsyncSession): The `db` parameter in the `refresh_token` function is an AsyncSession
    dependency that represents the database session used for database operations within the function. It
    is obtained through the `get_db` dependency injection. This parameter allows the function to
    interact with the database asynchronously to perform operations such as retrieving user
    
    Returns:
      The `refresh_token` function returns a dictionary containing the following keys and values:
    - "access_token": the newly created access token
    - "refresh_token": the newly created refresh token
    - "token_type": "bearer"
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.email != email:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token({"sub": email})
    refresh_token = await auth_service.create_refresh_token({"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    The function `request_email` checks if a user's email is confirmed and sends a confirmation email if
    not.
    
    Args:
      body (RequestEmail): `RequestEmail` - a data model representing the request body containing an
    email address.
      background_tasks (BackgroundTasks): The `background_tasks` parameter in the `request_email`
    function is used to add tasks that should be run in the background. In this case, the function is
    adding a task to send an email for email confirmation in the background. This allows the function to
    return a response to the user without waiting
      request (Request): The `request` parameter in the `request_email` function is of type `Request`.
    It is used to access information related to the incoming HTTP request such as headers, cookies,
    query parameters, and more. In this function, the `request` parameter is not directly used, but it
    could be
      db (AsyncSession): The `db` parameter in the function `request_email` is of type `AsyncSession`
    and is used to interact with the database asynchronously. It is obtained as a dependency using the
    `get_db` function. This parameter allows the function to perform database operations such as
    querying the database to retrieve user
    
    Returns:
      The function `request_email` returns a message based on the conditions checked in the code. If the
    user's email is already confirmed, it returns a message saying "Your email is already confirmed". If
    the user is found and their email is not confirmed, it adds a task to send an email for confirmation
    and returns a message saying "Check your email for confirmation."
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Check your email for confirmation."}
