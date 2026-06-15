from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_admin, get_db
from app.schemas.common import ResponseModel
from app.schemas.report import (
    BookingStatsReport,
    OccupancyReport,
    RevenueReport,
    StudentGrowthReport,
)
from app.services import report_service

router = APIRouter(
    prefix="/api/v1/admin/reports",
    tags=["Admin - Reports"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("/occupancy", response_model=ResponseModel[OccupancyReport])
def occupancy_report(db: Session = Depends(get_db)):
    report = report_service.get_occupancy_report(db)
    return ResponseModel(data=report)


@router.get("/revenue", response_model=ResponseModel[RevenueReport])
def revenue_report(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    report = report_service.get_revenue_report(db, start_date=start_date, end_date=end_date)
    return ResponseModel(data=report)


@router.get("/students", response_model=ResponseModel[StudentGrowthReport])
def student_growth_report(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    report = report_service.get_student_growth_report(db, start_date=start_date, end_date=end_date)
    return ResponseModel(data=report)


@router.get("/bookings", response_model=ResponseModel[BookingStatsReport])
def booking_stats_report(db: Session = Depends(get_db)):
    report = report_service.get_booking_stats_report(db)
    return ResponseModel(data=report)
