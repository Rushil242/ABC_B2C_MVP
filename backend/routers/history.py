
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database, auth_utils

router = APIRouter(
    prefix="/api", # We can use /api/returns or /api/history/returns. User asked for /api/returns
    tags=["History"]
)

@router.get("/returns", response_model=List[schemas.ITRHistorySchema])
def get_return_history(
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(database.get_db)
):
    try:
        returns = db.query(models.ITR_Filing).filter(
            models.ITR_Filing.user_pan == current_user.pan
        ).order_by(models.ITR_Filing.ay.desc()).all()
        return returns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notices", response_model=List[schemas.NoticeSchema])
def get_notice_history(
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(database.get_db)
):
    try:
        notices = db.query(models.Notice).filter(
            models.Notice.user_pan == current_user.pan
        ).order_by(models.Notice.date.desc()).all()
        return notices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
