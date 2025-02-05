import unittest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Contact, User
from src.schemas.contacts import ContactShema
from src.repository.contacts import *


class TestAsyncContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=AsyncSession)
        self.user = User(id=1, username="test_user", password="qwerty", confirmed=True)
        self.contacts = [
            Contact(
                id=1,
                name="test",
                surname="test",
                email="test",
                phone_number="test",
                birthdate=datetime(2025, 1, 1),
                user=self.user,
            ),
            Contact(
                id=2,
                name="test2",
                surname="test2",
                email="test2",
                phone_number="test2",
                birthdate=datetime(2025, 2, 10),
                user=self.user,
            ),
        ]

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = self.contacts[0]
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(
            name="test",
            surname="test",
            email="test",
            offset=offset,
            limit=limit,
            db=self.session,
            user=self.user,
        )
        self.assertEqual(result, self.contacts[0])

    async def test_get_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = self.contacts[0]
        self.session.execute.return_value = mocked_contact
        result = await get_contact(contact_id=1, db=self.session, user=self.user)
        self.assertEqual(result, self.contacts[0])

    async def test_create_contact(self):
        body = ContactShema(
            name="test",
            surname="test",
            email="test12345",
            phone_number="1234567890",
            birthdate="2025-01-01",
        )
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)

    async def test_update_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = self.contacts[0]
        self.session.execute.return_value = mocked_contact
        body = ContactShema(
            name="test2",
            surname="test2",
            email="test12345",
            phone_number="1234567890",
            birthdate="2025-01-01",
        )
        result = await update_contact(1, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)

    async def test_delete_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = self.contacts[0]
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(1, self.session, self.user)
        self.assertEqual(result, self.contacts[0])

    @patch("src.repository.contacts.datetime")
    async def test_get_birthdays_soon(self, mock_datetime):
        limit = 10
        offset = 0
        mock_datetime.today.return_value = datetime(2025, 1, 1)
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = [self.contacts[0]]
        self.session.execute.return_value = mocked_contacts
        result = await get_birthdays_soon(offset, limit, self.session, self.user)
        self.assertEqual(result, [self.contacts[0]])