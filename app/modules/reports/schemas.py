"""
Report Schemas
Pydantic models for request/response validation
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict

from .models import ReportType, ReportFormat, ReportStatus


# ============================================
# REPORT SCHEMAS
# ============================================

class ReportBase(BaseModel):
    """Base report schema"""

    title: str = Field(..., min_length=1, max_length=500)
    report_type: ReportType
    format: ReportFormat = ReportFormat.PDF
    parameters: Optional[Dict[str, Any]] = None


class ReportCreate(ReportBase):
    """Create report request"""

    pass


class ReportResponse(ReportBase):
    """Report response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: ReportStatus
    requested_by: int
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    generation_time_seconds: Optional[float] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


# ============================================
# SCHEDULED REPORT SCHEMAS
# ============================================

class ScheduledReportBase(BaseModel):
    """Base scheduled report schema"""

    title: str = Field(..., min_length=1, max_length=500)
    report_type: ReportType
    format: ReportFormat = ReportFormat.PDF
    parameters: Optional[Dict[str, Any]] = None
    cron_expression: str = Field(..., description="Cron expression (e.g., '0 0 * * 1')")
    email_recipients: Optional[List[str]] = None
    user_recipients: Optional[List[int]] = None
    is_active: bool = True


class ScheduledReportCreate(ScheduledReportBase):
    """Create scheduled report request"""

    pass


class ScheduledReportUpdate(BaseModel):
    """Update scheduled report"""

    title: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    cron_expression: Optional[str] = None
    email_recipients: Optional[List[str]] = None
    user_recipients: Optional[List[int]] = None
    is_active: Optional[bool] = None


class ScheduledReportResponse(ScheduledReportBase):
    """Scheduled report response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by: int
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ============================================
# REPORT PARAMETERS SCHEMAS
# ============================================

class DateRangeParams(BaseModel):
    """Date range parameters"""

    start_date: datetime
    end_date: datetime


class ProjectReportParams(DateRangeParams):
    """Project report parameters"""

    project_ids: Optional[List[int]] = None
    status_filter: Optional[List[str]] = None
    include_tasks: bool = True


class TaskReportParams(DateRangeParams):
    """Task report parameters"""

    project_ids: Optional[List[int]] = None
    assignee_ids: Optional[List[int]] = None
    status_filter: Optional[List[str]] = None
    priority_filter: Optional[List[str]] = None


class UserActivityParams(DateRangeParams):
    """User activity report parameters"""

    user_ids: Optional[List[int]] = None
    include_details: bool = False


class DeliveryReportParams(DateRangeParams):
    """Delivery report parameters"""

    vehicle_ids: Optional[List[int]] = None
    driver_ids: Optional[List[int]] = None
    status_filter: Optional[List[str]] = None


class WBReportParams(DateRangeParams):
    """WildBerries report parameters"""

    include_products: bool = True
    include_orders: bool = True
    sync_status_filter: Optional[List[str]] = None


# ============================================
# REPORT DOWNLOAD RESPONSE
# ============================================

class ReportDownloadResponse(BaseModel):
    """Report download URL response"""

    report_id: int
    download_url: str
    expires_at: datetime
    file_size: int
    format: ReportFormat
