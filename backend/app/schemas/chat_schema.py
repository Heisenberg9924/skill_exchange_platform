from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.exchange_request_schema import ExchangeRequestResponse
from app.schemas.user_schema import UserResponse


class ChatMessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    thread_id: int
    sender_id: int
    content: str
    created_at: datetime
    sender: UserResponse


class ChatThreadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exchange_request_id: int
    created_at: datetime
    updated_at: datetime
    exchange_request: ExchangeRequestResponse
    messages: list[ChatMessageResponse] = []
