from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from src.entity.models import Contact, User
from src.schemas.contacts import ContactShema


async def get_contacts(
    name: str,
    surname: str,
    email: str,
    offset: int,
    limit: int,
    db: AsyncSession,
    user: User,
):
    filters = []
    if name:
        filters.append(Contact.name.ilike(f"%{name}%"))
    if surname:
        filters.append(Contact.surname.ilike(f"%{surname}%"))
    if email:
        filters.append(Contact.email.ilike(f"%{email}%"))
    filters.append(Contact.user == user)
    stmt = select(Contact).filter(and_(*filters)).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):

    stmt = select(Contact).filter(and_(Contact.id == contact_id, Contact.user == user))
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactShema, db: AsyncSession, user: User):
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(
    contact_id: int, body: ContactShema, db: AsyncSession, user: User
):
    stmt = select(Contact).filter(and_(Contact.id == contact_id, Contact.user == user))
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.phone_number = body.phone_number
        contact.birthdate = body.birthdate
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter(and_(Contact.id == contact_id, Contact.user == user))
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def get_birthdays_soon(offset: int, limit: int, db: AsyncSession, user: User):
    today = datetime.today()
    stmt = (
        select(Contact)
        .filter(
            and_(
                func.date_part("month", Contact.birthdate) == today.month,
                func.date_part("day", Contact.birthdate) >= today.day,
                func.date_part("day", Contact.birthdate)
                <= (today + timedelta(days=7)).day,
                Contact.user == user
            )
        )
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    return contacts
