from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.exchange_request_model import ExchangeRequest, ExchangeRequestStatus
from app.models.skill_model import Skill, SkillType
from app.models.user_model import User
from app.schemas.exchange_request_schema import (
    ExchangeRequestCreate,
    ExchangeRequestStatusUpdate,
)
from app.services.llm_service import draft_exchange_message


def _query_requests(db: Session):
    return db.query(ExchangeRequest).options(
        joinedload(ExchangeRequest.requester),
        joinedload(ExchangeRequest.recipient),
        joinedload(ExchangeRequest.requested_skill).joinedload(Skill.owner),
        joinedload(ExchangeRequest.offered_skill).joinedload(Skill.owner),
    )


def list_exchange_requests(db: Session, current_user: User) -> list[ExchangeRequest]:
    return (
        _query_requests(db)
        .filter(
            (ExchangeRequest.requester_id == current_user.id)
            | (ExchangeRequest.recipient_id == current_user.id)
        )
        .order_by(ExchangeRequest.created_at.desc())
        .all()
    )


def create_exchange_request(
    db: Session,
    current_user: User,
    payload: ExchangeRequestCreate,
) -> ExchangeRequest:
    requested_skill = db.query(Skill).filter(Skill.id == payload.requested_skill_id).first()
    if not requested_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested skill not found",
        )

    if requested_skill.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot request your own skill",
        )

    if requested_skill.skill_type != SkillType.OFFER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested skill must be an offered skill",
        )

    offered_skill = None
    if payload.offered_skill_id is not None:
        offered_skill = db.query(Skill).filter(Skill.id == payload.offered_skill_id).first()
        if not offered_skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offered skill not found",
            )
        if offered_skill.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only offer your own skills",
            )
        if offered_skill.skill_type != SkillType.OFFER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offered skill must be an offered skill",
            )

    exchange_request = ExchangeRequest(
        requester_id=current_user.id,
        recipient_id=requested_skill.user_id,
        requested_skill_id=requested_skill.id,
        offered_skill_id=offered_skill.id if offered_skill else None,
        message=payload.message
        or draft_exchange_message(requested_skill, offered_skill, current_user.name),
    )
    db.add(exchange_request)
    db.commit()
    db.refresh(exchange_request)
    return _query_requests(db).filter(ExchangeRequest.id == exchange_request.id).first()


def update_exchange_request_status(
    db: Session,
    current_user: User,
    request_id: int,
    payload: ExchangeRequestStatusUpdate,
) -> ExchangeRequest:
    exchange_request = _query_requests(db).filter(ExchangeRequest.id == request_id).first()
    if not exchange_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange request not found",
        )

    allowed_users = {exchange_request.requester_id, exchange_request.recipient_id}
    if current_user.id not in allowed_users:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if (
        payload.status in {ExchangeRequestStatus.ACCEPTED, ExchangeRequestStatus.REJECTED}
        and current_user.id != exchange_request.recipient_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the recipient can accept or reject a request",
        )

    if (
        payload.status in {ExchangeRequestStatus.CANCELLED, ExchangeRequestStatus.COMPLETED}
        and current_user.id != exchange_request.requester_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the requester can cancel or complete a request",
        )

    exchange_request.status = payload.status
    db.add(exchange_request)
    db.commit()
    db.refresh(exchange_request)
    return _query_requests(db).filter(ExchangeRequest.id == exchange_request.id).first()
