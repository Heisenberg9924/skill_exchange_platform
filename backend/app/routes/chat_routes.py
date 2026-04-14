from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.chat_schema import ChatMessageCreate, ChatMessageResponse, ChatThreadResponse
from app.services.chat_service import create_message, create_or_get_thread, get_thread, list_threads
from app.utils.dependencies import get_current_user, get_db


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/threads", response_model=list[ChatThreadResponse])
def get_threads(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return list_threads(db, current_user)


@router.post(
    "/threads/{exchange_request_id}",
    response_model=ChatThreadResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_thread(
    exchange_request_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_or_get_thread(db, current_user, exchange_request_id)


@router.get("/threads/{thread_id}", response_model=ChatThreadResponse)
def get_thread_details(
    thread_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_thread(db, current_user, thread_id)


@router.post(
    "/threads/{thread_id}/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    thread_id: int,
    payload: ChatMessageCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_message(db, current_user, thread_id, payload.content)
