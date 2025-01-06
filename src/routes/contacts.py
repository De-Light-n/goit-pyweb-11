from typing import Optional
from fastapi import APIRouter, status, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.schema import ContactResponse, ContactShema
from src.repository import contacts as repository_contacts
from src.database.db import get_db

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/birthdays-soon", response_model=list[ContactResponse])
async def get_birthdays_soon(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=10, lt=500),
    db: AsyncSession = Depends(get_db),
):
    contacts = await repository_contacts.get_birthdays_soon(offset, limit, db)
    return contacts


@router.get("/", response_model=list[ContactResponse])
async def get_contacts(
    name: Optional[str] = None,
    surname: Optional[str] = None,
    email: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=10, lt=500),
    db: AsyncSession = Depends(get_db),
):
    contacts = await repository_contacts.get_contacts(name, surname, email, offset, limit, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact = await repository_contacts.get_contact(contact_id, db)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactShema, db: AsyncSession = Depends(get_db)):
    contact = await repository_contacts.create_contact(body, db)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactShema, contact_id: int, db: AsyncSession = Depends(get_db)
):
    contact = await repository_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="contact not found"
        )
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact = await repository_contacts.delete_contact(contact_id, db)
    return contact
