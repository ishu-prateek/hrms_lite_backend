from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional

class EmployeeBase(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    department: str

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    employee_id: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None

class Employee(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class AttendanceBase(BaseModel):
    employee_id: int
    date: datetime
    status: str  # 'Present' or 'Absent'

class AttendanceCreate(AttendanceBase):
    pass

class Attendance(AttendanceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
