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
    """
    This Python async function retrieves contacts based on specified criteria from a database session.
    
    :param name: The `name` parameter is a string used to filter contacts by their name. If provided,
    contacts with names containing the specified string will be included in the results
    :type name: str
    :param surname: The `surname` parameter in the `get_contacts` function is used to filter contacts
    based on the surname of the contact. If a value is provided for the `surname` parameter, contacts
    with surnames that match the provided value (partially or fully) will be included in the results
    :type surname: str
    :param email: The `email` parameter in the `get_contacts` function is used as a filter criteria to
    search for contacts whose email addresses contain the specified value. If a value is provided for
    the `email` parameter, contacts with email addresses that match the provided value (partially or
    fully) will be included
    :type email: str
    :param offset: The `offset` parameter in the `get_contacts` function is used to specify the number
    of results to skip before starting to return data. It is typically used for pagination, where you
    can retrieve a subset of results starting from a specific position in the result set
    :type offset: int
    :param limit: The `limit` parameter in the `get_contacts` function specifies the maximum number of
    contacts that should be returned in the result set. It limits the number of contacts that will be
    retrieved from the database and returned by the function
    :type limit: int
    :param db: The `db` parameter in the `get_contacts` function is an AsyncSession object. This object
    represents a connection to the database that allows you to execute asynchronous database queries. It
    is used to interact with the database and perform operations like executing queries, committing
    transactions, and managing database connections in an asynchronous
    :type db: AsyncSession
    :param user: The `user` parameter in the `get_contacts` function is of type `User`. It is used to
    filter contacts based on the user to whom they belong. The function retrieves contacts from the
    database that match the specified criteria (name, surname, email) and belong to the specified user
    :type user: User
    :return: The function `get_contacts` returns a list of contacts that match the specified criteria
    (name, surname, email) for a specific user. The contacts are retrieved from the database using the
    provided AsyncSession `db` and the query is filtered based on the input parameters. The function
    returns all the contacts that match the criteria within the specified offset and limit.
    """
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
    """
    This Python async function retrieves a contact from the database based on the contact ID and user.
    
    Args:
      contact_id (int): The `contact_id` parameter is an integer that represents the unique identifier
    of the contact you want to retrieve from the database.
      db (AsyncSession): AsyncSession is an asynchronous database session object that allows you to
    interact with the database asynchronously. It is typically used in asynchronous Python applications
    that work with databases using an ORM (Object-Relational Mapping) library like SQLAlchemy.
      user (User): The `user` parameter in the `get_contact` function is an instance of the `User`
    class. It is used to filter the query to retrieve a specific contact associated with that user.
    
    Returns:
      The function `get_contact` is returning a single `Contact` object that matches the provided
    `contact_id` and belongs to the specified `user`. The return value is obtained using the
    `scalar_one_or_none()` method, which will return either the single result found or `None` if no
    matching contact is found.
    """
    stmt = select(Contact).filter(and_(Contact.id == contact_id, Contact.user == user))
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactShema, db: AsyncSession, user: User):
    """
    This Python function creates a new contact record in a database using the provided data and user
    information.
    
    Args:
      body (ContactShema): ContactSchema object containing the data for creating a new contact.
      db (AsyncSession): The `db` parameter in the `create_contact` function is an instance of an
    asynchronous database session (`AsyncSession`). This session is used to interact with the database
    in an asynchronous manner, allowing you to perform database operations such as adding, committing,
    and refreshing data.
      user (User): The `user` parameter in the `create_contact` function is an instance of the `User`
    class. It is used to associate the newly created contact with a specific user.
    
    Returns:
      The function `create_contact` is returning the newly created `contact` object after it has been
    added to the database, committed, and refreshed.
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(
    contact_id: int, body: ContactShema, db: AsyncSession, user: User
):
    """
    This async function updates a contact in the database based on the provided contact ID, user, and
    contact information.
    
    Args:
      contact_id (int): The `contact_id` parameter is an integer that represents the unique identifier
    of the contact that you want to update in the database.
      body (ContactShema): The `body` parameter in the `update_contact` function represents the data
    that will be used to update the contact information. It likely contains fields such as `name`,
    `surname`, `phone_number`, and `birthdate` which will be used to update the corresponding fields of
    the contact identified by `
      db (AsyncSession): The `db` parameter in the `update_contact` function is an instance of an
    asynchronous database session (`AsyncSession`). This session is used to interact with the database
    asynchronously, allowing you to execute queries and commit transactions in an asynchronous manner.
      user (User): The `user` parameter in the `update_contact` function represents the user who is
    updating the contact information. This parameter is used to ensure that the user can only update
    contacts that belong to them. The function filters contacts based on both the `contact_id` and the
    `user` to make sure
    
    Returns:
      The `update_contact` function is returning the updated contact object after updating its
    attributes with the values provided in the `body` parameter.
    """
    stmt = select(Contact).filter(and_(Contact.id == contact_id, Contact.user == user))
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birthdate = body.birthdate
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    """
    This function deletes a contact from the database based on the contact ID and user, if the contact
    exists.
    
    Args:
      contact_id (int): The `contact_id` parameter is an integer that represents the unique identifier
    of the contact that you want to delete from the database.
      db (AsyncSession): The `db` parameter is an instance of an asynchronous database session
    (`AsyncSession`). It is used to interact with the database in an asynchronous manner, allowing you
    to execute queries and perform database operations without blocking the main thread. In the provided
    function `delete_contact`, the `db` parameter is used
      user (User): The `user` parameter in the `delete_contact` function is an instance of the `User`
    class. It is used to filter the contact that needs to be deleted based on the user who owns the
    contact.
    
    Returns:
      The function `delete_contact` returns the deleted contact if it exists, otherwise it returns
    `None`.
    """
    
    stmt = select(Contact).filter(and_(Contact.id == contact_id, Contact.user == user))
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def get_birthdays_soon(offset: int, limit: int, db: AsyncSession, user: User):
    """
    This function retrieves upcoming birthdays of contacts within a specified timeframe for a given user
    from a database session asynchronously.
    
    Args:
      offset (int): The `offset` parameter is used to specify the starting index from where the query
    should begin fetching results. It is typically used for pagination, allowing you to retrieve results
    in chunks rather than all at once.
      limit (int): The `limit` parameter in the `get_birthdays_soon` function specifies the maximum
    number of contacts to retrieve from the database. It limits the number of results returned by the
    query to the specified value.
      db (AsyncSession): The `db` parameter in the function `get_birthdays_soon` is an AsyncSession
    object that represents a connection to the database. It is used to execute queries asynchronously
    and interact with the database to retrieve contact information for upcoming birthdays.
      user (User): The `user` parameter in the function `get_birthdays_soon` is of type `User`. It is
    used to filter contacts based on the user to whom they belong. This parameter helps in retrieving
    contacts whose birthdays are coming up soon for a specific user.
    
    Returns:
      The function `get_birthdays_soon` returns a list of contacts whose birthdays fall within the next
    7 days starting from today's date. The contacts are filtered based on the provided `user` parameter
    and are retrieved from the database using the provided `db` AsyncSession. The function returns the
    list of contacts that meet the specified criteria.
    """
    
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
