from fastapi import Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from libgravatar import Gravatar

from src.database.db import get_db
from src.entity.models import User
from src.schemas.users import UserShema

async def create_user(body: UserShema, db:AsyncSession = Depends(get_db)):
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
    user.refresh_token = token
    await db.commit()
    
async def get_user_by_email(email:str, db:AsyncSession = Depends(get_db)):
    stmt = select(User).filter(User.email == email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user

async def update_avatar(email, url: str, db: AsyncSession) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user

async def confirmed_email(email: str, db: AsyncSession) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()