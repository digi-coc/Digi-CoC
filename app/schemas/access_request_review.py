from pydantic import BaseModel, Field


class AccessRequestReview(BaseModel):
    decision: str = Field(pattern=r"^(approved|rejected)$")
    decision_reason: str = Field(min_length=1, max_length=2000)