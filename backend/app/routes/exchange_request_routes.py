from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.exchange_request_schema import (
    ExchangeRequestCreate,
    ExchangeRequestResponse,
    ExchangeRequestStatusUpdate,
)
from app.services.exchange_request_service import (
    create_exchange_request,
    list_exchange_requests,
    update_exchange_request_status,
)
from app.utils.dependencies import get_current_user, get_db


router = APIRouter(prefix="/exchange-requests", tags=["Exchange Requests"])


@router.get("/", response_model=list[ExchangeRequestResponse])
def get_exchange_requests(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_exchange_requests(db, current_user)


@router.post(
    "/",
    response_model=ExchangeRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_request(
    payload: ExchangeRequestCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_exchange_request(db, current_user, payload)


@router.patch("/{request_id}/status", response_model=ExchangeRequestResponse)
def update_request_status(
    request_id: int,
    payload: ExchangeRequestStatusUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_exchange_request_status(db, current_user, request_id, payload)
