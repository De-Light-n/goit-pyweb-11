from fastapi import Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from src.database.db import get_db
from src.entity.models import User
from src.schemas.users import UserShema

async def create_user(body: UserShema, db:AsyncSession = Depends(get_db)):
    new_user = User(**body.model_dump())
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
