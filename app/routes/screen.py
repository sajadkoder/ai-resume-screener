from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Screening
from app.schemas import ScreeningCreate, ScreeningResponse
from app.auth import get_current_user, get_current_admin
from app.ai_service import screen_resume

router = APIRouter(prefix="/screen", tags=["Screenings"])


@router.post("/", response_model=ScreeningResponse, status_code=status.HTTP_201_CREATED)
def create_screening(
    screening_data: ScreeningCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        ai_result = screen_resume(
            job_description=screening_data.job_description,
            resume_text=screening_data.resume_text
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )

    new_screening = Screening(
        user_id=current_user.id,
        job_description=screening_data.job_description,
        resume_text=screening_data.resume_text,
        score=ai_result.get("score", 50.0),
        feedback=ai_result.get("feedback", "No feedback available"),
        match_level=ai_result.get("match_level", "Moderate"),
    )
    db.add(new_screening)
    db.commit()
    db.refresh(new_screening)
    return new_screening


@router.get("/history", response_model=List[ScreeningResponse])
def get_user_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    screenings = db.query(Screening).filter(
        Screening.user_id == current_user.id
    ).order_by(Screening.created_at.desc()).all()
    return screenings


@router.get("/all", response_model=List[ScreeningResponse])
def get_all_screenings(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    screenings = db.query(Screening).order_by(Screening.created_at.desc()).all()
    return screenings
