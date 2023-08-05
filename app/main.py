from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Form, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .user_repository import UsersRepository, UserRequest, UserResponse, UserUpdate
from .announcements_repository import AnnouncementRepository, AnnouncementRequest, AnnouncementResponse
from .comments_repository import CommentRepository, CommentRequest, CommentResponse
from .favorites_repository import FavoriteResponse, FavoriteRepository
from . import database
from jose import jwt

from . import models

database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/users/login")

user_repo = UsersRepository()
announcement_repo = AnnouncementRepository()
comment_repo = CommentRepository()
fav_repo = FavoriteRepository()

def encode(email: str) -> str:
    body = {"email": email}
    return jwt.encode(body, "lluna", algorithm="HS256")


def decode(token: str) -> str:
    data = jwt.decode(token, "lluna", algorithms=["HS256"])
    return data["email"]


def get_db() -> Session:
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verificate_user(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)):
    user_email = decode(token)
    user = user_repo.get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="Not user such number")

    return user



@app.post("/auth/users/", tags=["Register"], response_model=UserResponse)
def auth(user: UserRequest, db: Session = Depends(get_db)) -> UserResponse:
    existing_user = user_repo.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Phone number or email already taken")
    created_user = user_repo.create_user(db, user)
    return created_user

#
@app.post("/auth/users/login", tags=["Login"], response_model=dict)
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)) -> dict:
    if "@" in username:
        user = user_repo.get_user_by_email(db, username)
    else:
        user = user_repo.get_user_by_phone(db,  username)

    if user is None or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = encode(user.email)
    return {"access_token": access_token}


@app.patch("/auth/users/me", tags=["Updated user info"])
def update_profile(userupdate: UserUpdate, user: UserRequest = Depends(verificate_user), db: Session = Depends(get_db)):
    user_repo.updated_user(db, user, userupdate)
    return {"messages": "your profile updated"}

@app.get("/auth/users/me", tags=["Profile"])
def get_profile(user=Depends(verificate_user), db: Session = Depends(get_db)):
    return user

@app.get("/shanyraks/search", tags=["Search Announcements"])
def search_announcements(
        limit: int = Query(5, gt=0),
        offset: int = Query(1, ge=1),
        type: Optional[str] = Query(None, regex="^(sell|rent)$", examples=['sell', 'rent']),
        rooms_count: Optional[int] = Query(None, gt=0),
        price_from: Optional[float] = Query(None, ge=0),
        price_until: Optional[float] = Query(None, ge=0),
        db: Session = Depends(get_db)
):
    query = db.query(models.Announcement)

    if type:
        query = query.filter(models.Announcement.type == type)
    if rooms_count:
        query = query.filter(models.Announcement.rooms_count == rooms_count)
    if price_from:
        query = query.filter(models.Announcement.price >= price_from)
    if price_until:
        query = query.filter(models.Announcement.price <= price_until)

    total_announcements = query.count()
    announcements = query.offset((offset - 1) * limit).limit(limit).all()

    return {
        "total": total_announcements,
        "announcements": announcements

    }

@app.post("/shanyraks/", tags=["Create Announcement"], response_model=AnnouncementResponse)
def create_announcement(
    announcement_data: AnnouncementRequest,
    user: UserResponse = Depends(verificate_user),
    db: Session = Depends(get_db)
) -> AnnouncementResponse:
    created_announcement = announcement_repo.create_announcement(db=db, announcement=announcement_data, user_id=user.id)
    return created_announcement

@app.get("/shanyraks/{id}", tags=["Get Announcement"])
def get_announcement(id: int, db: Session = Depends(get_db)):
    announcement = announcement_repo.get_announcement_by_id(db, id)
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement does not exist")
    return announcement



@app.patch("/shanyraks/{id_announcement}", tags=["Update Announcement"])
def update_announcement(
        id_announcement: int,
        announcement: AnnouncementRequest,
        current_user: UserResponse = Depends(verificate_user),
        db: Session = Depends(get_db)
):
    updating_announcement = announcement_repo.get_announcement_by_id(db, id_announcement)
    if not updating_announcement:
        raise HTTPException(status_code=404, detail="The announcement not found")
    if updating_announcement.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this announcement")

    announcement_repo.update_announcement(db, id_announcement, announcement)
    return {"message": "Successfully updated"}


@app.delete("/shanyraks/{id_announcement}", tags=["Delete Announcement"])
def deleting_announcement(
        id_announcement: int,
        current_user: UserResponse = Depends(verificate_user),
        db: Session = Depends(get_db)
):
    delete_announcement = announcement_repo.get_announcement_by_id(db, id_announcement)
    if not delete_announcement:
        raise HTTPException(status_code=404, detail="The announcement not found")
    if delete_announcement.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this announcement")

    announcement_repo.delete_announcement(db, id_announcement)
    return {"message": "Successfully deleted"}



@app.post("/shanyraks/{id}/comments", tags=["Add comment"], response_model=CommentResponse)
def create_comment(comment: CommentRequest,
    id_announcement: int,
    user: UserResponse = Depends(verificate_user),
    db: Session = Depends(get_db)
):

    created_comment = comment_repo.create_comment(db=db, comment=comment, announcement_id=id_announcement, user_id=user.id)
    return created_comment


@app.get("/shanyraks/{id}/comments", tags=["Get comments"])
def get_comment(
    id_announcement: int,
    db: Session = Depends(get_db)
):
    comments = comment_repo.get_announcement_comments(db=db, announcement_id=id_announcement)
    return comments


@app.patch("/shanyraks/{id}/comments/{comment_id}", tags=["Update Comment"])
def update_comment(
        comment: CommentRequest,
        id_announcement: int,
        comment_id: int,
        current_user: UserResponse = Depends(verificate_user),
        db: Session = Depends(get_db)
):
    updating_comment = comment_repo.get_comment_by_comment_id(db, comment_id, id_announcement)

    if not updating_comment:
        raise HTTPException(status_code=404, detail="The comment not found")
    if updating_comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this comment")

    comment_repo.update_comment(db, id_announcement, comment_id, user_id=current_user.id, comment=comment)
    return {"message": "Successfully updated"}



@app.delete("/shanyraks/{id}/comments/{comment_id}", tags=["Delete Comment"])
def delete_comment(
        id_announcement: int,
        comment_id:int,
        current_user: UserResponse = Depends(verificate_user),
        db: Session = Depends(get_db)
):
    deleting_comment = comment_repo.get_comment_by_comment_id(db, comment_id, id_announcement)

    if not deleting_comment:
        raise HTTPException(status_code=404, detail="The comment not found")
    if deleting_comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this comment")

    comment_repo.delete_comment(db, id_announcement, comment_id, user_id=current_user.id)
    return {"message": "Successfully deleted"}


@app.post("/auth/users/favorites/shanyraks/{id}", tags=["Add to Favorites"], response_model=dict)
def add_to_favorites(
        id: int,
        user: UserResponse = Depends(verificate_user),
        db: Session = Depends(get_db)
):
    announcement = announcement_repo.get_announcement_by_id(db, id)
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")

    fav_repo.add_to_favorites(db, id, user.id)

    return {"message": "Announcement added to favorites successfully"}

@app.get("/auth/users/favorites/shanyraks", tags=["Get Favorites"])
def get_all_favorites(user: UserResponse = Depends(verificate_user),
    db: Session = Depends(get_db)
):
    favorites = fav_repo.get_all_favorites(user.id, db)
    return favorites or []

@app.delete("/auth/users/favorites/shanyraks/{id}", tags=["Delete Favorite"])
def delete_favorite(
        favorite_id: int,
        current_user: UserResponse = Depends(verificate_user),
        db: Session = Depends(get_db)
):
    deleting_favorite = fav_repo.get_favorite_by_id(db, favorite_id)
    if not deleting_favorite:
        raise HTTPException(status_code=404, detail="Favorite is not found")
    if deleting_favorite.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to delete")

    fav_repo.delete_favorite(db, favorite_id)
    return {"message": "Successfully deleted"}






