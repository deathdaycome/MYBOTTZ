"""
Report Service
Business logic for report generation and management
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import time

from app.core.logging import logger
from .models import Report, ReportStatus, ReportType, ReportFormat
from .generators import PDFGenerator, ExcelGenerator, ReportTemplates


class ReportService:
    """Service for report management"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.reports_dir = Path("./generated_reports")
        self.reports_dir.mkdir(exist_ok=True)

    async def create_report(
        self,
        title: str,
        report_type: ReportType,
        format: ReportFormat,
        requested_by: int,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Report:
        """Create a new report generation task"""
        report = Report(
            title=title,
            report_type=report_type,
            format=format,
            requested_by=requested_by,
            parameters=parameters or {},
            status=ReportStatus.PENDING,
            expires_at=datetime.utcnow() + timedelta(days=7),  # 7 days retention
        )

        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)

        logger.info(
            "report_created",
            report_id=report.id,
            report_type=report_type,
            format=format,
        )

        return report

    async def generate_report(self, report_id: int) -> Report:
        """Generate the actual report file"""
        result = await self.db.execute(select(Report).where(Report.id == report_id))
        report = result.scalar_one_or_none()

        if not report:
            raise ValueError(f"Report {report_id} not found")

        # Update status
        report.status = ReportStatus.PROCESSING
        report.started_at = datetime.utcnow()
        await self.db.commit()

        start_time = time.time()

        try:
            # Fetch data based on report type
            data = await self._fetch_report_data(report.report_type, report.parameters)

            # Get template
            template = self._get_template(report.report_type)

            # Generate file
            file_name = f"{report.report_type}_{report.id}_{int(time.time())}"
            if report.format == ReportFormat.PDF:
                file_path = str(self.reports_dir / f"{file_name}.pdf")
                PDFGenerator.generate_simple_report(
                    title=template["title"],
                    data=data,
                    headers=template["headers"],
                    output_path=file_path,
                )
            elif report.format == ReportFormat.EXCEL:
                file_path = str(self.reports_dir / f"{file_name}.xlsx")
                ExcelGenerator.generate_simple_report(
                    title=template["title"],
                    data=data,
                    headers=template["headers"],
                    output_path=file_path,
                )
            else:
                raise ValueError(f"Unsupported format: {report.format}")

            # Get file size
            file_size = Path(file_path).stat().st_size

            # Update report
            report.status = ReportStatus.COMPLETED
            report.file_path = file_path
            report.file_size = file_size
            report.completed_at = datetime.utcnow()
            report.generation_time_seconds = time.time() - start_time

            await self.db.commit()

            logger.info(
                "report_generated",
                report_id=report.id,
                file_path=file_path,
                file_size=file_size,
                generation_time=report.generation_time_seconds,
            )

            return report

        except Exception as e:
            report.status = ReportStatus.FAILED
            report.error_message = str(e)
            report.completed_at = datetime.utcnow()
            await self.db.commit()

            logger.error(
                "report_generation_failed",
                report_id=report.id,
                error=str(e),
                exc_info=True,
            )

            raise

    async def _fetch_report_data(
        self, report_type: ReportType, parameters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Fetch data for report based on type"""
        # This is a simplified version - in production, you'd query actual data

        if report_type == ReportType.PROJECTS_SUMMARY:
            # Mock data - replace with actual query
            return [
                {
                    "ID": 1,
                    "Name": "Sample Project",
                    "Status": "active",
                    "Client": "Client A",
                    "Created": "2025-01-01",
                    "Deadline": "2025-12-31",
                    "Tasks Count": 10,
                }
            ]

        elif report_type == ReportType.TASKS_SUMMARY:
            return [
                {
                    "ID": 1,
                    "Title": "Sample Task",
                    "Project": "Sample Project",
                    "Assignee": "User 1",
                    "Status": "in_progress",
                    "Priority": "high",
                    "Deadline": "2025-06-01",
                }
            ]

        elif report_type == ReportType.WB_PRODUCTS:
            return [
                {
                    "Article": "WB123",
                    "Name": "Sample Product",
                    "Price": 1000.0,
                    "Stock": 50,
                    "Last Sync": "2025-01-12",
                }
            ]

        else:
            return []

    def _get_template(self, report_type: ReportType) -> Dict[str, Any]:
        """Get report template by type"""
        templates = {
            ReportType.PROJECTS_SUMMARY: ReportTemplates.projects_summary_template(),
            ReportType.TASKS_SUMMARY: ReportTemplates.tasks_summary_template(),
            ReportType.USERS_ACTIVITY: ReportTemplates.users_activity_template(),
            ReportType.WB_PRODUCTS: ReportTemplates.wb_products_template(),
        }

        return templates.get(
            report_type,
            {"title": "Custom Report", "headers": ["Data"], "description": "Custom report"},
        )

    async def get_report(self, report_id: int) -> Optional[Report]:
        """Get report by ID"""
        result = await self.db.execute(select(Report).where(Report.id == report_id))
        return result.scalar_one_or_none()

    async def list_reports(
        self,
        user_id: Optional[int] = None,
        status: Optional[ReportStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Report]:
        """List reports with filters"""
        query = select(Report)

        if user_id:
            query = query.where(Report.requested_by == user_id)

        if status:
            query = query.where(Report.status == status)

        query = query.order_by(Report.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete_report(self, report_id: int) -> bool:
        """Delete a report"""
        report = await self.get_report(report_id)

        if not report:
            return False

        # Delete file if exists
        if report.file_path and Path(report.file_path).exists():
            Path(report.file_path).unlink()

        # Delete from database
        await self.db.delete(report)
        await self.db.commit()

        logger.info("report_deleted", report_id=report_id)

        return True
