from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from datetime import datetime, date
from src.database import SessionLocal
from src.models.models import Attendance, Employee
from src.models.schemas import Attendance as AttendanceSchema, AttendanceCreate

router = APIRouter(prefix="/attendance", tags=["attendance"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/", response_model=list[AttendanceSchema])
def get_attendance(
    db: Session = Depends(get_db),
    start_date: date = Query(None, description="Start date for filtering"),
    end_date: date = Query(None, description="End date for filtering")
):
    query = db.query(Attendance)
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    attendance = query.all()
    return attendance

@router.get("/api/summary", response_model=list[dict])
def get_attendance_summary(db: Session = Depends(get_db)):
    summary = db.query(
        Employee.id,
        Employee.employee_id,
        Employee.full_name,
        func.count(Attendance.id).label('total_days'),
        func.sum(case((Attendance.status == 'Present', 1), else_=0)).label('present_days'),
        func.sum(case((Attendance.status == 'Absent', 1), else_=0)).label('absent_days')
    ).outerjoin(Attendance).group_by(Employee.id).all()

    return [
        {
            'employee_id': emp.employee_id,
            'full_name': emp.full_name,
            'total_days': emp.total_days or 0,
            'present_days': emp.present_days or 0,
            'absent_days': emp.absent_days or 0
        }
        for emp in summary
    ]

@router.get("/api/stats")
def get_attendance_stats(db: Session = Depends(get_db)):
    total_employees = db.query(Employee).count()
    total_attendance = db.query(Attendance).count()
    total_present = db.query(Attendance).filter(Attendance.status == 'Present').count()
    total_absent = db.query(Attendance).filter(Attendance.status == 'Absent').count()

    return {
        'total_employees': total_employees,
        'total_attendance_records': total_attendance,
        'total_present': total_present,
        'total_absent': total_absent
    }

@router.post("/api/", response_model=AttendanceSchema)
def create_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    # Check if employee exists
    if not db.query(Employee).filter(Employee.id == attendance.employee_id).first():
        raise HTTPException(status_code=404, detail="Employee not found")
    # Check if attendance already marked for that date and employee
    existing = db.query(Attendance).filter(
        Attendance.employee_id == attendance.employee_id,
        Attendance.date == attendance.date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Attendance already marked for this date")
    db_attendance = Attendance(**attendance.dict())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

@router.get("/api/employee/{employee_id}", response_model=list[AttendanceSchema])
def get_employee_attendance(employee_id: int, db: Session = Depends(get_db)):
    if not db.query(Employee).filter(Employee.id == employee_id).first():
        raise HTTPException(status_code=404, detail="Employee not found")
    attendance = db.query(Attendance).filter(Attendance.employee_id == employee_id).all()
    return attendance
