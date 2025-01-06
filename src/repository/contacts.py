from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact
from src.schemas.schema import ContactShema


async def get_contacts(offset: int, limit: int, db: AsyncSession):
    contacts = db.query(Contact).offset(offset).limit(limit)
    return contacts


async def get_contact(contact_id: int, db: AsyncSession):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    return contact


async def create_contact(body: ContactShema, db: AsyncSession):
    contact = Contact(**body.model_dump(exclude_unset=True))
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

async def update_contact(contact_id: int, body: ContactShema, db: AsyncSession):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        contact.name=body.name
        contact.surname=body.surname
        contact.phone_number=body.phone_number
        contact.birthdate=body.birthdate
        db.commit()
    return contact


async def delete_contact(contact_id: int, db: AsyncSession):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact
