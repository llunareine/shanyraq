from fastapi import HTTPException
from sqlalchemy import update,delete
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import models


class FavoriteResponse(BaseModel):
    announcement_id: int

class FavoriteRepository:

    @staticmethod
    def add_to_favorites(db:Session, announcement_id, user_id):
        get_announcement = db.query(models.Announcement).get(announcement_id)
        if not get_announcement:
            raise HTTPException(status_code=404, detail="Announcement not found")

        favorite = models.UserFavorite(announcement_id=announcement_id, user_id=user_id)
        db.add(favorite)
        db.commit()
        db.refresh(favorite)
        return favorite

    @staticmethod
    def get_all_favorites(user_id: int, db: Session):
        return db.query(models.UserFavorite).where(models.UserFavorite.user_id == user_id).all()

    @staticmethod
    def delete_favorite(db: Session, favorite_id):
        deleting_favorite = delete(models.UserFavorite).where(
            models.UserFavorite.id == favorite_id)
        db.execute(deleting_favorite)
        db.commit()
        return True

    @staticmethod
    def get_favorite_by_id(db: Session, favorite_id):
        return db.query(models.UserFavorite).where(models.UserFavorite.id == favorite_id).first()

