"""
Reports API Router
Endpoints for report generation and management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.users.dependencies import get_current_user
from .schemas import (
    ReportCreate,
    ReportResponse,
    ReportStatus as ReportStatusSchema,
)
from .models import ReportStatus
from .service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new report generation task

    The report will be generated in the background.
    Use GET /reports/{id} to check status and download when ready.
    """
    service = ReportService(db)

    # Create report record
    report = await service.create_report(
        title=report_data.title,
        report_type=report_data.report_type,
        format=report_data.format,
        requested_by=current_user.id,
        parameters=report_data.parameters,
    )

    # Schedule background generation
    background_tasks.add_task(service.generate_report, report.id)

    return report


@router.get("/", response_model=List[ReportResponse])
async def list_reports(
    status: Optional[ReportStatus] = None,
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all reports for current user"""
    service = ReportService(db)
    reports = await service.list_reports(
        user_id=current_user.id,
        status=status,
        skip=skip,
        limit=limit,
    )
    return reports


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get report details"""
    service = ReportService(db)
    report = await service.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Check ownership
    if report.requested_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return report


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download generated report file"""
    service = ReportService(db)
    report = await service.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Check ownership
    if report.requested_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if completed
    if report.status != ReportStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Report is not ready. Status: {report.status}",
        )

    # Check if file exists
    if not report.file_path:
        raise HTTPException(status_code=404, detail="Report file not found")

    # Return file
    return FileResponse(
        path=report.file_path,
        filename=f"{report.title}.{report.format}",
        media_type="application/octet-stream",
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a report"""
    service = ReportService(db)
    report = await service.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Check ownership
    if report.requested_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await service.delete_report(report_id)
    return None


@router.get("/templates/list")
async def list_report_templates(current_user = Depends(get_current_user)):
    """List available report templates"""
    from .generators import ReportTemplates

    return {
        "templates": [
            {
                "type": "projects_summary",
                **ReportTemplates.projects_summary_template(),
            },
            {
                "type": "tasks_summary",
                **ReportTemplates.tasks_summary_template(),
            },
            {
                "type": "users_activity",
                **ReportTemplates.users_activity_template(),
            },
            {
                "type": "wb_products",
                **ReportTemplates.wb_products_template(),
            },
        ]
    }
