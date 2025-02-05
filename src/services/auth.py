from datetime import datetime, timedelta
import pickle
from typing import Optional
import redis
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt


from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import config


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = config.SECRET_KEY_JWT
    ALGORITHM = config.ALGORITHM

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
    r = redis.Redis()

    def verify_password(self, plain_password, hashed_password):
        """
        The function `verify_password` compares a plain text password with a hashed password to
        determine if they match.

        :param plain_password: The `plain_password` parameter is the password entered by the user in its
        original plain text form before it is hashed for storage or comparison
        :param hashed_password: The `hashed_password` parameter is the password that has already been
        hashed using a cryptographic hashing algorithm. This hashed password is typically stored in a
        database or some other form of storage for security reasons. When a user tries to log in, their
        input password is hashed and compared with the stored hashed password to
        :return: The `verify_password` method is returning the result of calling the `verify` method of
        `pwd_context` with the `plain_password` and `hashed_password` as arguments. This method is
        typically used to verify if a plain text password matches a hashed password.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The function `get_password_hash` takes a password as input and returns its hashed value using
        the `pwd_context` object.

        :param password: The `password` parameter is a string that represents the user's password that
        needs to be hashed for security purposes
        :type password: str
        :return: The `get_password_hash` method is returning the hashed version of the input password
        using the `pwd_context` object.
        """
        return self.pwd_context.hash(password)

    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        This Python function creates an access token with optional expiration time.

        :param data: The `data` parameter in the `create_access_token` function is a dictionary
        containing the information that you want to encode into the access token. This data could
        include details such as the user's ID, username, role, or any other relevant information that
        you want to include in the access token
        :type data: dict
        :param expires_delta: The `expires_delta` parameter in the `create_access_token` function is an
        optional parameter that specifies the duration for which the access token will be valid. It is a
        float value representing the number of seconds for the token to expire after it is created. If
        `expires_delta` is provided, the
        :type expires_delta: Optional[float]
        :return: The function `create_access_token` returns the encoded access token as a string.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now() + timedelta(minutes=15)
        to_encode.update(
            {"iat": datetime.now(), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    async def create_refresh_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        The `create_refresh_token` function generates a JWT refresh token with specified data and
        expiration time.

        :param data: The `data` parameter in the `create_refresh_token` function is a dictionary
        containing the information that needs to be encoded into the refresh token. This data could
        include user-specific information or any other data that you want to include in the token
        payload
        :type data: dict
        :param expires_delta: The `expires_delta` parameter in the `create_refresh_token` function is an
        optional parameter that specifies the time duration (in seconds) for which the refresh token
        will be valid. If `expires_delta` is provided, the refresh token will expire after the specified
        number of seconds. If `expires_delta
        :type expires_delta: Optional[float]
        :return: The function `create_refresh_token` returns an encoded refresh token as a string.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.now(), "exp": expire, "scope": "refresh_token"}
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        The function `decode_refresh_token` decodes a refresh token using a secret key and algorithm,
        checks the token scope, and returns the email if valid.

        :param refresh_token: The `decode_refresh_token` function takes a `refresh_token` as a
        parameter. This token is decoded using the `jwt.decode` method with the provided `SECRET_KEY`
        and `ALGORITHM`. If the decoded payload contains a "scope" key with the value "refresh_token",
        the function extracts
        :type refresh_token: str
        :return: The `decode_refresh_token` function is returning the email extracted from the payload
        of the decoded JWT refresh token if the scope is "refresh_token". If the scope is not
        "refresh_token", it raises an HTTPException with a status code of 401 and the detail "Invalid
        scope for token". If there is an error decoding the token (JWTError), it raises an HTTPException
        with a status code
        """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ):
        """
        The `get_current_user` function retrieves the current user based on the provided token and
        validates the user's credentials.

        :param token: The `token` parameter in the `get_current_user` function is used to authenticatethe user. It is obtained from the request headers and is expected to be a valid JWT (JSON WebToken) that contains the necessary information to identify and authorize the user
        :type token: str
        :param db: The `db` parameter in the `get_current_user` function is used to pass the databasesession dependency to the function. It is defined as an `AsyncSession` type and is obtainedusing the `get_db` dependency. This parameter allows the function to interact with the databaseasynchronously within the context
        :type db: AsyncSession
        
        :return: The `get_current_user` function returns the user object retrieved either from the cacheor the database based on the email extracted from the JWT token payload.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = self.r.get(f"user:{email}")
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)
        return user

    def create_email_token(self, data: dict):
        """
        The function `create_email_token` generates a JWT token with specified data and expiration time.

        :param data: The `data` parameter in the `create_email_token` function is a dictionary containing the information that you want to encode into a JWT token. This data could include details such as the user's email address, user ID, or any other relevant information that you want to include in the token
        :type data: dict
        
        :return: A JWT token is being returned after encoding the provided data dictionary along with the current timestamp and an expiration timestamp set to 7 days from the current time.
        """
        to_encode = data.copy()
        expire = datetime.now() + timedelta(days=7)
        to_encode.update({"iat": datetime.now(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        This asynchronous Python function decodes a JWT token to extract the email address associated
        with it, raising an exception if the token is invalid.

        :param token: The `token` parameter is a string that represents a JSON Web Token (JWT) used for
        email verification. The function `get_email_from_token` decodes the token using the provided
        `SECRET_KEY` and `ALGORITHM` to extract the email address from the payload. If the decoding is
        successful
        :type token: str
        :return: the email extracted from the JWT token payload.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )


auth_service = Auth()
