from sqlalchemy import Column, Integer, Boolean, Table, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    phone_number = Column(String(15), nullable=False, unique=True)
    birthdate = Column(DateTime, nullable=False)
    created_at = Column("created_at", DateTime, default=func.now())
    