from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from app.database import Base
import enum


class Role(str, enum.Enum):
    admin = "admin"
    moderator = "moderator"
    operator = "operator"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(20), default=Role.operator.value, nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)  # medhouse, swiss_energy
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ReportTemplate(Base):
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_name = Column(String(255), nullable=False)  # имя файла на диске
    report_type = Column(String(100), nullable=True)  # тип отчётности для 1С
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ReportUpload(Base):
    __tablename__ = "report_uploads"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    stored_path = Column(String(512), nullable=False)
    report_type = Column(String(100), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    period = Column(String(50), nullable=True)  # 2025-01, 2026-Q1 и т.д.
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnalysisDataset(Base):
    """Метаданные загруженных наборов для аналитики (Анализ 2 и др.)"""
    __tablename__ = "analysis_datasets"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False)  # "analiz2", "reference", "import"
    name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=True)
    period = Column(String(50), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
