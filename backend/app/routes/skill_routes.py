from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.schemas.skill_schema import (
    MatchResponse,
    SkillCreate,
    SkillResponse,
    SkillSearchResponse,
    SkillSuggestionRequest,
    SkillSuggestionResponse,
    SkillUpdate,
)
from app.schemas.user_schema import MessageResponse
from app.services.llm_service import suggest_skill_listing
from app.services.skill_service import (
    create_skill,
    delete_skill,
    get_matches_for_user,
    list_skills,
    search_skills,
    update_skill,
)
from app.utils.dependencies import get_current_user, get_db


router = APIRouter(prefix="/skills", tags=["Skills"])


@router.get("/", response_model=list[SkillResponse])
def get_skills(db: Session = Depends(get_db)):
    return list_skills(db)


@router.get("/me", response_model=list[SkillResponse])
def get_my_skills(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_skills(db, current_user.id)


@router.post("/ai-suggest", response_model=SkillSuggestionResponse)
def get_skill_suggestions(payload: SkillSuggestionRequest):
    return suggest_skill_listing(payload.model_dump())


@router.post("/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill_listing(
    payload: SkillCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_skill(db, current_user, payload)


@router.put("/{skill_id}", response_model=SkillResponse)
def update_skill_listing(
    skill_id: int,
    payload: SkillUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_skill(db, skill_id, current_user, payload)


@router.delete("/{skill_id}", response_model=MessageResponse)
def delete_skill_listing(
    skill_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_skill(db, skill_id, current_user)
    return {"message": "Skill deleted successfully"}


@router.get("/matches/me", response_model=list[MatchResponse])
def get_my_matches(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_matches_for_user(db, current_user)


@router.get("/search", response_model=list[SkillSearchResponse])
def search_skill_listings(
    q: str = Query(min_length=2),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return search_skills(db, q, current_user)
