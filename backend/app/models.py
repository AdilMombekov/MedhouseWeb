from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text, Float
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


class MailingBatch(Base):
    """Партия рассылки из 1С (один загруженный файл «Выгрузка XLSX»)."""
    __tablename__ = "mailing_batches"

    id = Column(Integer, primary_key=True, index=True)
    source_file = Column(String(255), nullable=False)
    sheet_name = Column(String(128), nullable=True)
    row_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class MailingRow(Base):
    """Одна строка из рассылки 1С (реализация/документ). Все поля — в raw_data (JSON), ключевые продублированы для выборок."""
    __tablename__ = "mailing_rows"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("mailing_batches.id"), nullable=False, index=True)
    row_index = Column(Integer, nullable=False)
    period_date = Column(String(20), nullable=True, index=True)  # 04.03.2026
    organization = Column(String(100), nullable=True, index=True)  # MedHouse
    kontragent = Column(String(255), nullable=True, index=True)
    nomerklatura = Column(String(512), nullable=True)
    amount = Column(Float, nullable=True)  # сумма продажи (в единицах)
    profit = Column(Float, nullable=True)  # Profit (тенге)
    raw_data = Column(Text, nullable=True)  # JSON со всеми колонками строки
    created_at = Column(DateTime, default=datetime.utcnow)


class GoogleSheet(Base):
    """Реестр Google Таблиц, доступных сервисному аккаунту (обнаружены через Drive/Sheets API)."""
    __tablename__ = "google_sheets"

    id = Column(Integer, primary_key=True, index=True)
    spreadsheet_id = Column(String(128), unique=True, nullable=False, index=True)
    name = Column(String(512), nullable=True)
    folder_id = Column(String(128), nullable=True, index=True)
    web_view_link = Column(String(512), nullable=True)
    sheet_count = Column(Integer, default=0)
    last_synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class GoogleSheetSnapshot(Base):
    """Снимок одного листа таблицы: данные залогированы в data_json (массив строк)."""
    __tablename__ = "google_sheet_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    spreadsheet_id = Column(String(128), nullable=False, index=True)
    sheet_name = Column(String(256), nullable=False, index=True)
    row_count = Column(Integer, default=0)
    col_count = Column(Integer, default=0)
    data_json = Column(Text, nullable=True)  # JSON: [[cell, cell, ...], ...]
    synced_at = Column(DateTime, default=datetime.utcnow)
