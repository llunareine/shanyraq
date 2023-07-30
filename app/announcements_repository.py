from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import models

from sqlalchemy import update, delete, func



class AnnouncementRequest(BaseModel):
    type: str
    price: float
    address: str
    area: float
    rooms_count: int
    description: str


class AnnouncementResponse(BaseModel):
    id: int
    type: str
    price: float
    address: str
    area: float
    rooms_count: int
    description: str
    user_id: int
    total_comments: int = 0

class AnnouncementUpdate(BaseModel):
    type: str
    price: float
    address: str
    area: float
    rooms_count: int
    description: str


class AnnouncementRepository:

    @staticmethod
    def get_announcement_by_id(db: Session, announcement_id):
        return db.query(models.Announcement).filter(models.Announcement.id == announcement_id).first()

    @staticmethod
    def create_announcement(db: Session, announcement: AnnouncementRequest,
                            user_id: int) -> models.Announcement:
        db_announcement = models.Announcement(

            type=announcement.type,
            price=announcement.price,
            address=announcement.address,
            area=announcement.area,
            rooms_count=announcement.rooms_count,
            description=announcement.description,
            user_id=user_id
        )
        db.add(db_announcement)
        db.commit()
        db.refresh(db_announcement)
        return db_announcement

    @staticmethod
    def update_announcement(db: Session, announcement_id: int, announcement: AnnouncementRequest):
        update_data = update(models.Announcement).where(models.Announcement.id == announcement_id).values(
            type=announcement.type,
            price=announcement.price,
            address=announcement.address,
            area=announcement.area,
            rooms_count=announcement.rooms_count,
            description=announcement.description)


        db.execute(update_data)
        db.commit()

        updated_rows = db.query(models.Announcement).filter(models.Announcement.id == announcement_id)

        if updated_rows:
            return db.query(models.Announcement).get(announcement_id)

        raise HTTPException(status_code=404)

    @staticmethod
    def delete_announcement(db: Session, announcement_id: int):
        delete_data = delete(models.Announcement).where(models.Announcement.id == announcement_id)

        db.execute(delete_data)
        db.commit()


    @staticmethod
    def get_total_comments(announcement_id: int, db: Session):
        announcement = db.query(models.Announcement).filter(models.Announcement.id == announcement_id).first()
        if not announcement:
            raise HTTPException(status_code=404, detail="Announcement not found")

        comment_count = db.query(func.count(models.Comment.id)).filter(
            models.Comment.announcement_id == announcement_id).scalar()

        return comment_count

