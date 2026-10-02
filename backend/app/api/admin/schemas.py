from datetime import date, datetime
from pydantic import BaseModel
from pydantic import BaseModel, Field
from datetime import date, datetime
from pydantic import BaseModel


class AdminAppointmentResponse(BaseModel):
    id: int
    patient_number: int
    patient_name: str
    patient_phone: str
    patient_email: str | None
    doctor_id: int
    doctor_name: str
    doctor_specialization: str
    appointment_date: date
    status: str
    created_at: datetime


class DashboardStatsResponse(BaseModel):
    today: date

    today_total: int
    today_scheduled: int
    today_completed: int
    today_cancelled: int

    upcoming_scheduled: int

    active_doctors: int

    today_capacity: int
    today_remaining_capacity: int

# for updating from admin section
class AdminDoctorResponse(BaseModel):
    id: int
    name: str
    specialization: str
    daily_capacity: int
    active: bool
    today_scheduled: int
    today_remaining_capacity: int


class AdminDoctorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    specialization: str = Field(min_length=1, max_length=150)
    daily_capacity: int = Field(gt=0)


class AdminDoctorUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    specialization: str = Field(min_length=1, max_length=150)
    daily_capacity: int = Field(gt=0)


# for exporing pdf
class AppointmentReportItem(BaseModel):
    id: int
    patient_number: int
    patient_name: str
    patient_phone: str
    patient_email: str | None
    doctor_id: int
    doctor_name: str
    doctor_specialization: str
    appointment_date: date
    status: str
    created_at: datetime