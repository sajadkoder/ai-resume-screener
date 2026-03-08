from fastapi import APIRouter, Depends, HTTPException, status, Query
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
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service unavailable: {str(e)}"
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
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    screenings = db.query(Screening).filter(
        Screening.user_id == current_user.id
    ).order_by(Screening.created_at.desc()).offset(skip).limit(limit).all()
    return screenings


@router.get("/all", response_model=List[ScreeningResponse])
def get_all_screenings(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    screenings = db.query(Screening).order_by(
        Screening.created_at.desc()
    ).offset(skip).limit(limit).all()
    return screenings


@router.delete("/{screening_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_screening(
    screening_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screening not found"
        )
    if screening.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this screening"
        )
    db.delete(screening)
    db.commit()
    return None
