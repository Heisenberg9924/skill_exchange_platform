from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.exchange_request_model import ExchangeRequestStatus
from app.schemas.skill_schema import SkillResponse
from app.schemas.user_schema import UserResponse


class ExchangeRequestCreate(BaseModel):
    requested_skill_id: int
    offered_skill_id: int | None = None
    message: str | None = Field(default=None, max_length=2000)


class ExchangeRequestStatusUpdate(BaseModel):
    status: ExchangeRequestStatus


class ExchangeRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    requester_id: int
    recipient_id: int
    requested_skill_id: int
    offered_skill_id: int | None = None
    message: str | None = None
    status: ExchangeRequestStatus
    created_at: datetime
    updated_at: datetime
    requester: UserResponse
    recipient: UserResponse
    requested_skill: SkillResponse
    offered_skill: SkillResponse | None = None
