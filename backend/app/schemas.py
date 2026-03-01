from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class CompanyBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None


class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReportTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    report_type: Optional[str] = None
    company_id: Optional[int] = None


class ReportTemplateResponse(ReportTemplateBase):
    id: int
    file_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReportUploadCreate(BaseModel):
    report_type: Optional[str] = None
    company_id: Optional[int] = None
    period: Optional[str] = None
    notes: Optional[str] = None


class ReportUploadResponse(BaseModel):
    id: int
    file_name: str
    report_type: Optional[str] = None
    company_id: Optional[int] = None
    period: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisDatasetResponse(BaseModel):
    id: int
    source: str
    name: str
    file_path: Optional[str] = None
    period: Optional[str] = None
    company_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
