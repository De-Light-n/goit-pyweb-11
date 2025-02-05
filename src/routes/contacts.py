from re import A
from typing import Optional
from fastapi import APIRouter, status, Depends, HTTPException, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.schemas.contacts import ContactResponse, ContactShema
from src.repository import contacts as repository_contacts
from src.database.db import get_db
from src.services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "/birthdays-soon",
    response_model=list[ContactResponse],
    dependencies=[Depends(RateLimiter(times=5, seconds=20))],
)
async def get_birthdays_soon(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=10, lt=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    This asynchronous Python function retrieves upcoming birthdays of contacts based on specified offset
    and limit parameters, while also requiring database access and authentication of the current user.
    
    Args:
      offset (int): The `offset` parameter is used to specify the starting point from which to retrieve
    birthdays. It indicates the number of records to skip before starting to return results. In the
    provided code snippet, the `offset` parameter has a default value of 0 and must be a non-negative
    integer (greater than
      limit (int): The `limit` parameter in the `get_birthdays_soon` function specifies the maximum
    number of birthdays to retrieve. By default, it is set to 10, and it must be greater than or equal
    to 10 and less than 500. This means that the function will return a maximum
      db (AsyncSession): The `db` parameter in the function `get_birthdays_soon` is of type
    `AsyncSession` and is obtained by calling the `get_db` dependency. This parameter is used to
    interact with the database asynchronously within the function.
      current_user (User): The `current_user` parameter in the `get_birthdays_soon` function is of type
    `User` and is obtained by calling the `get_current_user` function from the `auth_service` module as
    a dependency. This parameter represents the currently authenticated user who is making the request
    to fetch upcoming
    
    Returns:
      The function `get_birthdays_soon` is returning a list of contacts whose birthdays are coming soon.
    The contacts are retrieved from the database using the `repository_contacts.get_birthdays_soon`
    method with the provided offset, limit, database session (`db`), and current user information.
    """
    contacts = await repository_contacts.get_birthdays_soon(
        offset, limit, db, current_user
    )
    return contacts


@router.get(
    "/",
    response_model=list[ContactResponse],
    dependencies=[Depends(RateLimiter(times=5, seconds=20))],
)
async def get_contacts(
    name: Optional[str] = None,
    surname: Optional[str] = None,
    email: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=10, lt=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The `get_contacts` function retrieves contacts based on specified criteria using async operations in
    Python.
    
    Args:
      name (Optional[str]): The `name` parameter in the `get_contacts` function is an optional string
    parameter used to filter contacts by their name. If a `name` value is provided, only contacts with
    that specific name will be retrieved. If `name` is not provided (None), the function will not filter
    contacts
      surname (Optional[str]): The `surname` parameter in the `get_contacts` function is an optional
    parameter that represents the surname of a contact. It is used as a filter criteria to search for
    contacts based on their surname. If provided, the function will retrieve contacts with the specified
    surname. If not provided, this filter will
      email (Optional[str]): The `email` parameter in the `get_contacts` function is an optional
    parameter that allows you to filter contacts based on their email address. If you provide an email
    address, the function will return contacts that match that email address. If you do not provide an
    email address, it will not be used
      offset (int): The `offset` parameter in the `get_contacts` function is used to specify the
    starting index from which the contacts should be retrieved. It determines the position in the list
    of contacts where the retrieval should begin. The `offset` parameter is an integer value and has a
    default value of 0.
      limit (int): The `limit` parameter in the `get_contacts` function specifies the maximum number of
    contacts that should be returned in a single query. By default, the `limit` is set to 10, but it
    must be greater than or equal to 10 and less than 500. This means that
      db (AsyncSession): The `db` parameter in the `get_contacts` function is of type `AsyncSession` and
    is obtained as a dependency using the `get_db` function. This parameter represents the asynchronous
    database session that will be used to interact with the database when querying for contacts.
      current_user (User): The `current_user` parameter in the `get_contacts` function is of type `User`
    and is obtained by using the `Depends` function with the dependency `auth_service.get_current_user`.
    This parameter represents the current user who is making the request to get the contacts. It is
    likely used
    
    Returns:
      The `get_contacts` function is returning the contacts retrieved from the database based on the
    provided parameters such as name, surname, email, offset, and limit. The function is using the
    `repository_contacts.get_contacts` method to fetch the contacts from the database using the provided
    parameters and the database session (`db`) and the current user information (`current_user`). The
    retrieved contacts are then returned by the function
    """
    contacts = await repository_contacts.get_contacts(
        name, surname, email, offset, limit, db, current_user
    )
    return contacts


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    dependencies=[Depends(RateLimiter(times=5, seconds=20))],
)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    This Python async function retrieves a contact by ID from a database, with authentication and error
    handling.
    
    Args:
      contact_id (int): The `contact_id` parameter is an integer that represents the unique identifier
    of the contact you want to retrieve from the database.
      db (AsyncSession): The `db` parameter is an instance of an asynchronous database session
    (`AsyncSession`) that is used to interact with the database. It is obtained using the `get_db`
    dependency, which likely sets up the database connection for the request.
      current_user (User): The `current_user` parameter in the `get_contact` function is a dependency
    that retrieves the current user making the request. It is obtained by calling the `get_current_user`
    function from the `auth_service` module. This parameter ensures that only authenticated users can
    access the `get_contact` endpoint
    
    Returns:
      The `get_contact` function is returning the contact information corresponding to the `contact_id`
    provided. If the contact is not found in the database, it raises an HTTPException with a status code
    of 404 and the detail message "Contact not found".
    """
    contact = await repository_contacts.get_contact(contact_id, db)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=5, seconds=20))],
)
async def create_contact(
    body: ContactShema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    This Python async function creates a contact using the provided data and database session, with
    authentication based on the current user.
    
    :param body: The `body` parameter in the `create_contact` function is of type `ContactSchema`. It
    likely contains the data needed to create a new contact entry in the database
    :type body: ContactShema
    :param db: The `db` parameter in the `create_contact` function is an instance of an asynchronous
    database session. It is used to interact with the database to perform operations like creating a new
    contact record. In this case, it is obtained using the `get_db` dependency, which likely provides a
    connection to
    :type db: AsyncSession
    :param current_user: The `current_user` parameter in the `create_contact` function represents the
    user who is currently authenticated and making the request. This parameter is obtained by using the
    `auth_service.get_current_user` dependency, which likely handles the authentication and
    authorization logic to identify the current user. This user is then passed
    :type current_user: User
    :return: The function `create_contact` is returning the contact that was created in the database.
    """
    contact = await repository_contacts.create_contact(body, db, current_user)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactShema,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    This Python async function updates a contact in a database using the provided contact schema,
    contact ID, database session, and current user information.
    
    :param body: The `body` parameter in the `update_contact` function represents the data that will be
    used to update a contact. It is expected to be of type `ContactSchema`, which likely contains the
    updated information for the contact such as name, email, phone number, etc. This data will be used
    :type body: ContactShema
    :param contact_id: The `contact_id` parameter in the `update_contact` function represents the unique
    identifier of the contact that you want to update in the database. This identifier is used to locate
    the specific contact record that needs to be updated with the new information provided in the `body`
    parameter
    :type contact_id: int
    :param db: The `db` parameter in the `update_contact` function is an instance of an `AsyncSession`
    object. This object is used to interact with the database asynchronously. It is typically obtained
    from a dependency called `get_db`, which provides a session to the function
    :type db: AsyncSession
    :param current_user: The `current_user` parameter in the `update_contact` function represents the
    user who is currently authenticated and making the request to update a contact. This parameter is
    obtained by using the `Depends` function with the `auth_service.get_current_user` dependency, which
    ensures that the user is authenticated before
    :type current_user: User
    :return: The `update_contact` function is returning the updated contact information after updating
    it in the database. If the contact is not found, it raises an HTTPException with a status code of
    404 and the detail message "contact not found".
    """
    contact = await repository_contacts.update_contact(
        contact_id, body, db, current_user
    )
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="contact not found"
        )
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The `delete_contact` function deletes a contact from the database with the specified contact ID
    after verifying the current user's authentication.
    
    :param contact_id: The `contact_id` parameter is an integer that represents the unique identifier of
    the contact that you want to delete from the database
    :type contact_id: int
    :param db: The `db` parameter is an instance of an `AsyncSession` object, which is used to interact
    with the database asynchronously. It is obtained as a dependency using the `get_db` function
    :type db: AsyncSession
    :param current_user: The `current_user` parameter is of type `User` and is obtained by calling the
    `get_current_user` function from the `auth_service` module as a dependency in the `delete_contact`
    function. This parameter represents the user who is currently authenticated and making the request
    to delete a contact
    :type current_user: User
    :return: The `delete_contact` function is returning the deleted contact object after successfully
    deleting it from the database.
    """
    contact = await repository_contacts.delete_contact(contact_id, db, current_user)
    return contact
