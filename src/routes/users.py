import pickle

import cloudinary
import cloudinary.uploader
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Path,
    Query,
    UploadFile,
    File,
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.schemas.users import UserResponse
from src.services.auth import auth_service
from src.conf.config import config
from src.repository import users as repositories_users

router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
    secure=True,
)


@router.get(
    "/me",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    """
    The function `get_current_user` returns the current user using dependency injection in Python's
    FastAPI framework.
    
    :param user: The `get_current_user` function is an asynchronous function that takes a parameter
    `user` of type `User`. The function uses the `Depends` function from FastAPI to retrieve the current
    user. The `get_current_user` function is likely a part of an authentication service that verifies
    the user
    :type user: User
    :return: The `get_current_user` function is returning the current user object.
    """
    return user


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    This Python async function updates the avatar of a user by uploading a file to Cloudinary and
    updating the user's avatar URL in the database.
    
    :param file: The `file` parameter in the `update_avatar_user` function is of type `UploadFile` and
    is set to a default value of `File()`. This parameter is used to receive the uploaded file (avatar
    image) that the user wants to update
    :type file: UploadFile
    :param current_user: The `current_user` parameter in the `update_avatar_user` function represents
    the user who is currently authenticated and making the request. This parameter is obtained using the
    `auth_service.get_current_user` dependency, which likely handles the authentication logic and
    retrieves the current user object
    :type current_user: User
    :param db: The `db` parameter in the `update_avatar_user` function is an instance of an asynchronous
    database session. It is used to interact with the database to update the user's avatar image URL
    after uploading the new avatar image to a cloud storage service (in this case, Cloudinary). The `db
    :type db: AsyncSession
    :return: The function `update_avatar_user` returns the updated user object after updating the avatar
    image URL in the database.
    """
    r = cloudinary.uploader.upload(
        file.file, public_id=f"RestAPI/{current_user.username}", overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(f"RestAPI/{current_user.username}").build_url(
        width=250, height=250, crop="fill", version=r.get("version")
    )
    user = await repositories_users.update_avatar(current_user.email, src_url, db)
    return user
