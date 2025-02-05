import re
import unittest
import asyncio
from unittest.mock import MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.schemas.users import UserShema
from src.repository.users import *

class TestAsyncContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=AsyncSession)
        self.user = User(id=1, username="test_user", email="test@gmail.com", password="qwerty123", confirmed=False)
        
        
    async def test_create_user(self):
        body = UserShema(
            username="test_user",
            email="test@gmail.com",
            password="qwerty123"
        )
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.password, body.password)
        
    async def test_update_token(self):
        token = "token"
        await update_token(user=self.user, token=token, db=self.session)
        self.assertEqual(self.user.refresh_token, token)
        
    async def test_get_user_by_email(self):
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mocked_user
        result = await get_user_by_email(email=self.user.email, db=self.session)
        self.assertEqual(result, self.user)
      
    @patch("src.repository.users.get_user_by_email")
    async def test_update_avatar(self, mock_get_user_by_email):
        mock_get_user_by_email.return_value = self.user
        result = await update_avatar(email=self.user.email, url="test", db=self.session)
        self.assertEqual(result.avatar, self.user.avatar)
        self.assertIsNotNone(result)
        
    @patch("src.repository.users.get_user_by_email")
    async def test_confirmed_email(self, mock_get_user_by_email):
        mock_get_user_by_email.return_value = self.user
        await confirmed_email(email=self.user.email, db=self.session)
        self.assertEqual(self.user.confirmed, True)