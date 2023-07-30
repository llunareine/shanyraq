from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session
from . import models

from sqlalchemy import update



class UserRequest(BaseModel):
    email: EmailStr
    name: str
    phone: str
    password: str = Field(min_length=8)
    city: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    phone: str
    password: str = Field(min_length=8)
    city: str

class UserUpdate(BaseModel):
    # phone: str
    name: str
    city: str

class UsersRepository:
    @staticmethod
    def get_user_by_username(db: Session, name):
        return db.query(models.User).filter(models.User.name == name).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id):
        return db.query(models.User).filter(models.User.id == user_id).first()

    @staticmethod
    def get_user_by_phone(db: Session, user_phone):
        return db.query(models.User).filter(models.User.phone == user_phone).first()

    @staticmethod
    def get_user_by_email(db: Session, user_email):
        return db.query(models.User).filter(models.User.email == user_email).first()

    @staticmethod
    def create_user(db: Session, user: UserRequest) -> models.User:
        db_user = models.User(email=user.email, name=user.name,
                              password=user.password, phone=user.phone, city=user.city)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def updated_user(db: Session, user, user_update: UserUpdate):
        db_user_update = update(models.User).where(models.User.email == user.email).values(name=user_update.name, city=user_update.city)


        db.execute(db_user_update)
        db.commit()




    @staticmethod
    def get_all_users(db: Session):
        return db.query(models.User).all()


