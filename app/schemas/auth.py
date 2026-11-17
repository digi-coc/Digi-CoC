from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    organization_code: str = Field(min_length=1, max_length=50)
    personnel_code: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=256)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    personnel_id: str
    personnel_code: str
    full_name: str
    role: str