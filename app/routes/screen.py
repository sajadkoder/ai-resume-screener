from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

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
    match_level: Optional[str] = Query(None, description="Filter by match level: Strong, Moderate, Weak"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Screening).filter(Screening.user_id == current_user.id)
    if match_level:
        query = query.filter(Screening.match_level == match_level)
    screenings = query.order_by(Screening.created_at.desc()).offset(skip).limit(limit).all()
    return screenings


@router.get("/all", response_model=List[ScreeningResponse])
def get_all_screenings(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    match_level: Optional[str] = Query(None, description="Filter by match level: Strong, Moderate, Weak"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    query = db.query(Screening)
    if match_level:
        query = query.filter(Screening.match_level == match_level)
    screenings = query.order_by(Screening.created_at.desc()).offset(skip).limit(limit).all()
    return screenings


@router.get("/{screening_id}", response_model=ScreeningResponse)
def get_screening(
    screening_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screening not found")
    if screening.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return screening


@router.get("/stats/me", response_model=dict)
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = db.query(func.count(Screening.id)).filter(Screening.user_id == current_user.id).scalar()
    strong = db.query(func.count(Screening.id)).filter(
        Screening.user_id == current_user.id, Screening.match_level == "Strong"
    ).scalar()
    moderate = db.query(func.count(Screening.id)).filter(
        Screening.user_id == current_user.id, Screening.match_level == "Moderate"
    ).scalar()
    weak = db.query(func.count(Screening.id)).filter(
        Screening.user_id == current_user.id, Screening.match_level == "Weak"
    ).scalar()
    avg_score = db.query(func.avg(Screening.score)).filter(Screening.user_id == current_user.id).scalar()
    
    return {
        "total_screenings": total,
        "strong_matches": strong,
        "moderate_matches": moderate,
        "weak_matches": weak,
        "average_score": round(avg_score, 2) if avg_score else 0
    }


@router.get("/stats/all", response_model=dict)
def get_all_stats(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    total = db.query(func.count(Screening.id)).scalar()
    total_users = db.query(func.count(User.id)).scalar()
    strong = db.query(func.count(Screening.id)).filter(Screening.match_level == "Strong").scalar()
    moderate = db.query(func.count(Screening.id)).filter(Screening.match_level == "Moderate").scalar()
    weak = db.query(func.count(Screening.id)).filter(Screening.match_level == "Weak").scalar()
    avg_score = db.query(func.avg(Screening.score)).scalar()
    
    return {
        "total_screenings": total,
        "total_users": total_users,
        "strong_matches": strong,
        "moderate_matches": moderate,
        "weak_matches": weak,
        "average_score": round(avg_score, 2) if avg_score else 0
    }


@router.delete("/{screening_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_screening(
    screening_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screening not found")
    if screening.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    db.delete(screening)
    db.commit()
    return None
