from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.skill_model import SkillType


class SkillBase(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    category: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=10, max_length=2000)
    skill_type: SkillType
    proficiency_level: str | None = Field(default=None, max_length=50)
    availability: str | None = Field(default=None, max_length=120)


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=100)
    category: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, min_length=10, max_length=2000)
    skill_type: SkillType | None = None
    proficiency_level: str | None = Field(default=None, max_length=50)
    availability: str | None = Field(default=None, max_length=120)


class SkillOwnerSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    city: str | None = None


class SkillResponse(SkillBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    owner: SkillOwnerSummary
    ai_summary: str | None = None
    tag_names: list[str] = []


class SkillSuggestionRequest(BaseModel):
    title: str | None = Field(default=None, max_length=100)
    category: str | None = Field(default=None, max_length=100)
    description: str = Field(min_length=4, max_length=2000)
    skill_type: SkillType
    proficiency_level: str | None = Field(default=None, max_length=50)
    availability: str | None = Field(default=None, max_length=120)


class SkillSuggestionResponse(SkillBase):
    ai_summary: str | None = None
    tag_names: list[str] = []


class SkillSearchResponse(BaseModel):
    skill: SkillResponse
    score: float
    rationale: str
    matched_terms: list[str] = []


class MatchResponse(BaseModel):
    current_user_skill: SkillResponse
    matching_skill: SkillResponse
    match_score: float
    rationale: str
    shared_tags: list[str] = []
