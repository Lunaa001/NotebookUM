from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime


class Base(DeclarativeBase):
    """Base class for all ORM models"""
    pass
