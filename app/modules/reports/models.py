"""
Report Models
Database models for reports tracking
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class ReportType(str, enum.Enum):
    """Report type enumeration"""

    PROJECTS_SUMMARY = "projects_summary"
    TASKS_SUMMARY = "tasks_summary"
    USERS_ACTIVITY = "users_activity"
    DELIVERIES_REPORT = "deliveries_report"
    VEHICLES_UTILIZATION = "vehicles_utilization"
    FINANCIAL_SUMMARY = "financial_summary"
    WB_PRODUCTS = "wb_products"
    WB_ORDERS = "wb_orders"
    CUSTOM = "custom"


class ReportFormat(str, enum.Enum):
    """Report format enumeration"""

    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"


class ReportStatus(str, enum.Enum):
    """Report generation status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Report(Base):
    """Report generation tracking"""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Report metadata
    title: Mapped[str] = mapped_column(String(500))
    report_type: Mapped[ReportType] = mapped_column(SQLEnum(ReportType), index=True)
    format: Mapped[ReportFormat] = mapped_column(SQLEnum(ReportFormat))
    status: Mapped[ReportStatus] = mapped_column(
        SQLEnum(ReportStatus), default=ReportStatus.PENDING, index=True
    )

    # Generation info
    requested_by: Mapped[int] = mapped_column(Integer, index=True)  # user_id
    parameters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # File info
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # bytes

    # Status tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generation_time_seconds: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, index=True
    )  # For cleanup

    def __repr__(self):
        return f"<Report {self.id}: {self.title} ({self.status})>"


class ScheduledReport(Base):
    """Scheduled periodic reports"""

    __tablename__ = "scheduled_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Report configuration
    title: Mapped[str] = mapped_column(String(500))
    report_type: Mapped[ReportType] = mapped_column(SQLEnum(ReportType))
    format: Mapped[ReportFormat] = mapped_column(SQLEnum(ReportFormat))
    parameters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Schedule configuration
    cron_expression: Mapped[str] = mapped_column(String(100))  # e.g., "0 0 * * 1" (every Monday)
    is_active: Mapped[bool] = mapped_column(default=True, index=True)

    # Recipients
    email_recipients: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    user_recipients: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # user_ids

    # Tracking
    created_by: Mapped[int] = mapped_column(Integer)
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<ScheduledReport {self.id}: {self.title} ({self.cron_expression})>"
