from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import update,delete
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import models
from .announcements_repository import AnnouncementRepository


class CommentRequest(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int
    created_at: Optional[datetime]


class CommentRepository:
    @staticmethod
    def create_comment(db: Session, user_id, announcement_id, comment: CommentRequest):
        db_comment = models.Comment(content=comment.content, user_id=user_id, announcement_id=announcement_id)
        db.add(db_comment)
        query = update(models.Announcement).where(models.Announcement.id == announcement_id).values(
            total_comments=AnnouncementRepository.get_total_comments(announcement_id, db) + 1)
        db.execute(query)


        db.commit()
        db.refresh(db_comment)
        return db_comment

    @staticmethod
    def get_comment_by_announcement_id(db:Session,announcement_id):
        return db.query(models.Comment).filter(models.Comment.announcement_id == announcement_id).all()

    @staticmethod
    def get_comment_by_comment_id(db: Session, announcement_id, comment_id):
        return db.query(models.Comment).filter(models.Comment.id == comment_id and models.Comment.announcement_id == announcement_id).first()

    @staticmethod
    def get_announcement_comments(announcement_id: int, db: Session):
        announcement = db.query(models.Announcement).filter(models.Announcement.id == announcement_id).first()
        if not announcement:
            raise HTTPException(status_code=404, detail="Announcement not found")

        comments = db.query(models.Comment).filter(models.Comment.announcement_id == announcement_id).all()
        return comments

    @staticmethod
    def update_comment(db: Session, announcement_id, comment_id, user_id, comment:CommentRequest):
        updating_comment = update(models.Comment).filter(models.Comment.id == comment_id and models.Comment.announcement_id == announcement_id and models.Comment.user_id == user_id).values(content = comment.content)
        db.execute(updating_comment)
        db.commit()
        updated_comment = db.query(models.Comment).get(comment_id)
        if updated_comment:
            return updated_comment
        raise HTTPException(status_code=404,detail="The comment not found")

    @staticmethod
    def delete_comment(db: Session, announcement_id, comment_id, user_id):
        deleting_comment = delete(models.Comment).filter(models.Comment.id == comment_id and models.Comment.announcement_id == announcement_id and models.Comment.user_id == user_id)
        db.execute(deleting_comment)
        db.commit()
        return True

