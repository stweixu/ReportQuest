from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional
import sqlite3
import uuid

from src.reports.models.ReportModels import Report
from src.reports.services.ReportService import ReportService

router = APIRouter(prefix="/reports")

# Database connection setup
conn = sqlite3.connect('database/reports.db')
report_service = ReportService(conn)  # Instantiate the ReportService

@router.post("/", response_model=Report)
async def create_report(report: Report):
    """Create a new report."""
    status_code, created_report = report_service.create_report(report)
    if status_code == 201:
        return created_report
    elif status_code == 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create report: Report ID already exists.")
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create report.")

@router.get("/user/{user_id}", response_model=list[Report])
async def get_reports_by_user_id(user_id: str):
    """Retrieve all reports submitted by a specific user."""
    status_code, reports = report_service.read_report_by_user_id(user_id)
    if status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve reports for the user.")
    return reports

@router.get("/top/{k}", response_model=list[Report])
async def get_top_k_reports_by_severity(k: int):
    """Retrieve top k reports based on severity."""
    status_code, reports = report_service.get_top_k_reports_by_severity(k)
    if status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve top k reports by severity.")
    return reports

@router.get("/{report_id}", response_model=Optional[Report])
async def read_report_by_id(report_id: str):
    """Retrieve a report by its ID."""
    status_code, report = report_service.read_report_by_id(report_id)
    if status_code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    elif status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve report.")
    return report

@router.get("/search/description", response_model=list[Report])
async def search_reports_by_description(description: str):
    """Search reports by description."""
    status_code, reports = report_service.search_reports_by_description(description)
    if status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to search reports by description.")
    return reports

@router.get("/search/title", response_model=list[Report])
async def search_reports_by_title(title: str):
    """Search reports by title."""
    status_code, reports = report_service.search_reports_by_title(title)
    if status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to search reports by title.")
    return reports

@router.get("/search/uen", response_model=list[Report])
async def search_reports_by_uen(uen: str):
    """Search reports by UEN."""
    status_code, reports = report_service.search_reports_by_uen(uen)
    if status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to search reports by UEN.")
    return reports

@router.delete("/{report_id}")
async def delete_report(report_id: str):
    """Delete a report by its ID."""
    status_code = report_service.delete_report_by_id(report_id)
    if status_code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    elif status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete report.")
    return {"detail": "Report deleted successfully."}
