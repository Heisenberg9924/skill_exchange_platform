from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.skill_model import Skill, SkillTag, SkillType
from app.models.user_model import User
from app.schemas.skill_schema import SkillCreate, SkillUpdate
from app.services.llm_service import (
    build_search_document,
    get_text_embedding,
    generate_skill_metadata,
    serialize_embedding,
    score_skill_match,
    search_skill_against_query,
)


def _skill_query(db: Session):
    return db.query(Skill).options(joinedload(Skill.owner), joinedload(Skill.tags))


def _sync_skill_metadata(db: Session, skill: Skill) -> None:
    metadata = generate_skill_metadata(
        title=skill.title,
        category=skill.category,
        description=skill.description,
        skill_type=skill.skill_type.value,
        proficiency_level=skill.proficiency_level,
        availability=skill.availability,
    )
    skill.ai_summary = metadata["ai_summary"]
    skill.search_document = build_search_document(skill, metadata["tag_names"])
    skill.embedding_vector = serialize_embedding(get_text_embedding(skill.search_document))

    db.query(SkillTag).filter(SkillTag.skill_id == skill.id).delete()
    for tag_name in metadata["tag_names"]:
        db.add(SkillTag(skill_id=skill.id, name=tag_name))


def create_skill(db: Session, current_user: User, payload: SkillCreate) -> Skill:
    skill = Skill(user_id=current_user.id, **payload.model_dump())
    db.add(skill)
    db.flush()
    _sync_skill_metadata(db, skill)
    db.commit()
    db.refresh(skill)
    return _skill_query(db).filter(Skill.id == skill.id).first()


def list_skills(db: Session, current_user_id: int | None = None) -> list[Skill]:
    query = _skill_query(db).order_by(Skill.created_at.desc())
    if current_user_id is not None:
        query = query.filter(Skill.user_id == current_user_id)
    return query.all()


def get_skill_or_404(db: Session, skill_id: int) -> Skill:
    skill = _skill_query(db).filter(Skill.id == skill_id).first()
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
    db.flush()
    _sync_skill_metadata(db, skill)
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
    own_request_skills = _skill_query(db).filter(
        Skill.user_id == current_user.id,
        Skill.skill_type == SkillType.REQUEST,
    ).all()

    available_offer_skills = _skill_query(db).filter(
        Skill.user_id != current_user.id,
        Skill.skill_type == SkillType.OFFER,
    ).all()

    matches: list[dict[str, Skill | float | str | list[str]]] = []
    seen_pairs: set[tuple[int, int]] = set()

    for request_skill in own_request_skills:
        for offer_skill in available_offer_skills:
            pair_key = (request_skill.id, offer_skill.id)
            if pair_key in seen_pairs:
                continue
            score_payload = score_skill_match(request_skill, offer_skill)
            if score_payload["score"] < 0.28 and not (
                request_skill.title.lower() == offer_skill.title.lower()
                and request_skill.category.lower() == offer_skill.category.lower()
            ):
                continue

            seen_pairs.add(pair_key)
            matches.append(
                {
                    "current_user_skill": request_skill,
                    "matching_skill": offer_skill,
                    "match_score": score_payload["score"],
                    "rationale": score_payload["rationale"],
                    "shared_tags": score_payload["shared_tags"],
                }
            )

    return sorted(matches, key=lambda item: item["match_score"], reverse=True)


def search_skills(db: Session, query: str, current_user: User | None = None) -> list[dict]:
    skills = list_skills(db)
    results = []
    for skill in skills:
        if current_user and skill.user_id == current_user.id:
            continue
        score_payload = search_skill_against_query(query, skill)
        if score_payload["score"] < 0.18:
            continue
        results.append(
            {
                "skill": skill,
                "score": score_payload["score"],
                "rationale": score_payload["rationale"],
                "matched_terms": score_payload["matched_terms"],
            }
        )
    return sorted(results, key=lambda item: item["score"], reverse=True)


def backfill_skill_metadata(db: Session) -> None:
    skills = _skill_query(db).all()
    updated = False
    for skill in skills:
        if skill.ai_summary and skill.search_document and skill.embedding_vector and skill.tags:
            continue
        _sync_skill_metadata(db, skill)
        updated = True
    if updated:
        db.commit()
