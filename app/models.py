from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, Float, TIMESTAMP, text, ForeignKey, DateTime, func
from .database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, unique=False, index=True)
    password = Column(String)
    city = Column(String, index=True)


class Announcement(Base):
    __tablename__ = 'announcements'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    price = Column(Float)
    address = Column(String)
    area = Column(Float)
    rooms_count = Column(Integer)
    description = Column(String)
    created_at = Column(DateTime, default=func.now())

    user_id = Column(ForeignKey('users.id'))
    total_comments = Column(Integer, default=0)


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    user_id = Column(ForeignKey('users.id'))
    announcement_id = Column(ForeignKey('announcements.id'))
    created_at = Column(TIMESTAMP, default=datetime.now().replace(second=0, microsecond=0))


class UserFavorite(Base):
    __tablename__ = 'user_favorites'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey('users.id'))
    announcement_id = Column(ForeignKey('announcements.id'))



