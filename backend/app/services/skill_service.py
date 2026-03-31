from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.skill_model import Skill, SkillType
from app.models.user_model import User
from app.schemas.skill_schema import SkillCreate, SkillUpdate


def create_skill(db: Session, current_user: User, payload: SkillCreate) -> Skill:
    skill = Skill(user_id=current_user.id, **payload.model_dump())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return (
        db.query(Skill)
        .options(joinedload(Skill.owner))
        .filter(Skill.id == skill.id)
        .first()
    )


def list_skills(db: Session, current_user_id: int | None = None) -> list[Skill]:
    query = db.query(Skill).options(joinedload(Skill.owner)).order_by(Skill.created_at.desc())
    if current_user_id is not None:
        query = query.filter(Skill.user_id == current_user_id)
    return query.all()


def get_skill_or_404(db: Session, skill_id: int) -> Skill:
    skill = (
        db.query(Skill)
        .options(joinedload(Skill.owner))
        .filter(Skill.id == skill_id)
        .first()
    )
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return skill


def update_skill(
    db: Session,
    skill_id: int,
    current_user: User,
    payload: SkillUpdate,
) -> Skill:
    skill = get_skill_or_404(db, skill_id)
    if skill.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(skill, field, value)

    db.add(skill)
    db.commit()
    db.refresh(skill)
    return get_skill_or_404(db, skill.id)


def delete_skill(db: Session, skill_id: int, current_user: User) -> None:
    skill = get_skill_or_404(db, skill_id)
    if skill.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    db.delete(skill)
    db.commit()


def get_matches_for_user(db: Session, current_user: User) -> list[dict[str, Skill]]:
    own_request_skills = (
        db.query(Skill)
        .options(joinedload(Skill.owner))
        .filter(Skill.user_id == current_user.id, Skill.skill_type == SkillType.REQUEST)
        .all()
    )

    matches: list[dict[str, Skill]] = []
    seen_pairs: set[tuple[int, int]] = set()

    for request_skill in own_request_skills:
        matching_offer_skills = (
            db.query(Skill)
            .options(joinedload(Skill.owner))
            .filter(
                Skill.user_id != current_user.id,
                Skill.skill_type == SkillType.OFFER,
                func.lower(Skill.title) == request_skill.title.lower(),
                func.lower(Skill.category) == request_skill.category.lower(),
            )
            .all()
        )

        for offer_skill in matching_offer_skills:
            pair_key = (request_skill.id, offer_skill.id)
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)
            matches.append(
                {
                    "current_user_skill": request_skill,
                    "matching_skill": offer_skill,
                }
            )

    return matches
