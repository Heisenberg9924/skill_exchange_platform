from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.chat_model import ChatMessage, ChatThread
from app.models.exchange_request_model import ExchangeRequest, ExchangeRequestStatus
from app.models.skill_model import Skill
from app.models.user_model import User


def _thread_query(db: Session):
    return db.query(ChatThread).options(
        joinedload(ChatThread.exchange_request)
        .joinedload(ExchangeRequest.requester),
        joinedload(ChatThread.exchange_request)
        .joinedload(ExchangeRequest.recipient),
        joinedload(ChatThread.exchange_request)
        .joinedload(ExchangeRequest.requested_skill)
        .joinedload(Skill.owner),
        joinedload(ChatThread.exchange_request)
        .joinedload(ExchangeRequest.requested_skill)
        .joinedload(Skill.tags),
        joinedload(ChatThread.exchange_request)
        .joinedload(ExchangeRequest.offered_skill)
        .joinedload(Skill.owner),
        joinedload(ChatThread.exchange_request)
        .joinedload(ExchangeRequest.offered_skill)
        .joinedload(Skill.tags),
        joinedload(ChatThread.messages).joinedload(ChatMessage.sender),
    )


def _get_request_or_404(db: Session, exchange_request_id: int) -> ExchangeRequest:
    exchange_request = db.query(ExchangeRequest).filter(
        ExchangeRequest.id == exchange_request_id
    ).first()
    if not exchange_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exchange request not found")
    return exchange_request


def _ensure_participant(current_user: User, exchange_request: ExchangeRequest) -> None:
    if current_user.id not in {exchange_request.requester_id, exchange_request.recipient_id}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


def create_or_get_thread(
    db: Session,
    current_user: User,
    exchange_request_id: int,
) -> ChatThread:
    exchange_request = _get_request_or_404(db, exchange_request_id)
    _ensure_participant(current_user, exchange_request)

    if exchange_request.status != ExchangeRequestStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat becomes available after the request is accepted",
        )

    existing_thread = _thread_query(db).filter(
        ChatThread.exchange_request_id == exchange_request_id
    ).first()
    if existing_thread:
        return existing_thread

    thread = ChatThread(exchange_request_id=exchange_request_id)
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return _thread_query(db).filter(ChatThread.id == thread.id).first()


def list_threads(db: Session, current_user: User) -> list[ChatThread]:
    return _thread_query(db).join(ChatThread.exchange_request).filter(
        (ExchangeRequest.requester_id == current_user.id)
        | (ExchangeRequest.recipient_id == current_user.id)
    ).all()


def get_thread(db: Session, current_user: User, thread_id: int) -> ChatThread:
    thread = _thread_query(db).filter(ChatThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat thread not found")
    _ensure_participant(current_user, thread.exchange_request)
    return thread


def create_message(db: Session, current_user: User, thread_id: int, content: str) -> ChatMessage:
    thread = get_thread(db, current_user, thread_id)
    if thread.exchange_request.status != ExchangeRequestStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat is only available for accepted requests",
        )

    message = ChatMessage(thread_id=thread.id, sender_id=current_user.id, content=content.strip())
    db.add(message)
    db.commit()
    db.refresh(message)
    return (
        db.query(ChatMessage)
        .options(joinedload(ChatMessage.sender))
        .filter(ChatMessage.id == message.id)
        .first()
    )
