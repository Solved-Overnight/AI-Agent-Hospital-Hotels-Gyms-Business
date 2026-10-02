from datetime import date

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select

from app.database.database import SessionLocal
from app.database.models import Appointment, Doctor

from app.api.admin.schemas import (
    AdminAppointmentResponse,
    DashboardStatsResponse,
    AdminDoctorCreate,
    AdminDoctorResponse,
    AdminDoctorUpdate,
    AppointmentReportItem,
)

from io import BytesIO

from fastapi.responses import StreamingResponse
from openpyxl import Workbook

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get(
    "/appointments",
    response_model=list[AdminAppointmentResponse],
)
def get_admin_appointments(
    appointment_date: date | None = Query(
        default=None,
        description="Filter appointments by date.",
    ),
    doctor_id: int | None = Query(
        default=None,
        description="Filter appointments by doctor ID.",
    ),
    status: str | None = Query(
        default=None,
        description="Filter by appointment status.",
    ),
    search: str | None = Query(
        default=None,
        description="Search by patient name or phone.",
    ),
):
    db = SessionLocal()

    try:
        statement = (
            select(Appointment, Doctor)
            .join(
                Doctor,
                Appointment.doctor_id == Doctor.id,
            )
        )

        # ----------------------------------------
        # Date filter
        # ----------------------------------------

        if appointment_date is not None:
            statement = statement.where(
                Appointment.appointment_date == appointment_date
            )

        # ----------------------------------------
        # Doctor filter
        # ----------------------------------------

        if doctor_id is not None:
            statement = statement.where(
                Appointment.doctor_id == doctor_id
            )

        # ----------------------------------------
        # Status filter
        # ----------------------------------------

        if status is not None:
            allowed_statuses = {
                "scheduled",
                "cancelled",
                "completed",
            }

            if status not in allowed_statuses:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid appointment status.",
                )

            statement = statement.where(
                Appointment.status == status
            )

        # ----------------------------------------
        # Patient search
        # ----------------------------------------

        if search:
            search = search.strip()

            if search:
                statement = statement.where(
                    (
                        Appointment.patient_name.ilike(
                            f"%{search}%"
                        )
                    )
                    |
                    (
                        Appointment.patient_phone.ilike(
                            f"%{search}%"
                        )
                    )
                )

        # ----------------------------------------
        # Ordering
        # ----------------------------------------

        statement = statement.order_by(
            Appointment.appointment_date.asc(),
            Appointment.patient_number.asc(),
        )

        results = db.execute(statement).all()

        appointments = []

        for appointment, doctor in results:
            appointments.append(
                AdminAppointmentResponse(
                    id=appointment.id,
                    patient_number=appointment.patient_number,
                    patient_name=appointment.patient_name,
                    patient_phone=appointment.patient_phone,
                    patient_email=appointment.patient_email,
                    doctor_id=doctor.id,
                    doctor_name=doctor.name,
                    doctor_specialization=doctor.specialization,
                    appointment_date=appointment.appointment_date,
                    status=appointment.status,
                    created_at=appointment.created_at,
                )
            )

        return appointments

    finally:
        db.close()


@router.get(
    "/dashboard",
    response_model=DashboardStatsResponse,
)
def get_dashboard_stats():
    db = SessionLocal()

    try:
        today = date.today()

        # ----------------------------------------
        # Today's appointment counts
        # ----------------------------------------

        today_count_statement = select(
            func.count(Appointment.id)
        ).where(
            Appointment.appointment_date == today
        )

        today_total = db.execute(
            today_count_statement
        ).scalar_one()

        # ----------------------------------------
        # Today's scheduled
        # ----------------------------------------

        scheduled_statement = select(
            func.count(Appointment.id)
        ).where(
            Appointment.appointment_date == today,
            Appointment.status == "scheduled",
        )

        today_scheduled = db.execute(
            scheduled_statement
        ).scalar_one()

        # ----------------------------------------
        # Today's completed
        # ----------------------------------------

        completed_statement = select(
            func.count(Appointment.id)
        ).where(
            Appointment.appointment_date == today,
            Appointment.status == "completed",
        )

        today_completed = db.execute(
            completed_statement
        ).scalar_one()

        # ----------------------------------------
        # Today's cancelled
        # ----------------------------------------

        cancelled_statement = select(
            func.count(Appointment.id)
        ).where(
            Appointment.appointment_date == today,
            Appointment.status == "cancelled",
        )

        today_cancelled = db.execute(
            cancelled_statement
        ).scalar_one()

        # ----------------------------------------
        # Upcoming scheduled appointments
        #
        # Today and future dates
        # ----------------------------------------

        upcoming_statement = select(
            func.count(Appointment.id)
        ).where(
            Appointment.appointment_date >= today,
            Appointment.status == "scheduled",
        )

        upcoming_scheduled = db.execute(
            upcoming_statement
        ).scalar_one()

        # ----------------------------------------
        # Active doctors
        # ----------------------------------------

        doctors_statement = select(
            func.count(Doctor.id)
        ).where(
            Doctor.active.is_(True)
        )

        active_doctors = db.execute(
            doctors_statement
        ).scalar_one()

        # ----------------------------------------
        # Today's total capacity
        #
        # Every active doctor contributes their
        # default daily capacity.
        # ----------------------------------------

        capacity_statement = select(
            func.coalesce(
                func.sum(Doctor.daily_capacity),
                0,
            )
        ).where(
            Doctor.active.is_(True)
        )

        today_capacity = db.execute(
            capacity_statement
        ).scalar_one()

        # ----------------------------------------
        # Remaining capacity today
        #
        # Capacity - scheduled appointments
        # ----------------------------------------

        today_remaining_capacity = max(
            today_capacity - today_scheduled,
            0,
        )

        return DashboardStatsResponse(
            today=today,

            today_total=today_total,
            today_scheduled=today_scheduled,
            today_completed=today_completed,
            today_cancelled=today_cancelled,

            upcoming_scheduled=upcoming_scheduled,

            active_doctors=active_doctors,

            today_capacity=today_capacity,
            today_remaining_capacity=today_remaining_capacity,
        )

    finally:
        db.close()

@router.get("/appointments/{appointment_id}", response_model=AdminAppointmentResponse)
def get_admin_appointment(appointment_id: int):
    db = SessionLocal()

    try:
        statement = (
            select(Appointment, Doctor)
            .join(Doctor, Appointment.doctor_id == Doctor.id)
            .where(Appointment.id == appointment_id)
        )

        result = db.execute(statement).first()

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Appointment not found.",
            )

        appointment, doctor = result

        return AdminAppointmentResponse(
            id=appointment.id,
            patient_number=appointment.patient_number,
            patient_name=appointment.patient_name,
            patient_phone=appointment.patient_phone,
            patient_email=appointment.patient_email,
            doctor_id=doctor.id,
            doctor_name=doctor.name,
            doctor_specialization=doctor.specialization,
            appointment_date=appointment.appointment_date,
            status=appointment.status,
            created_at=appointment.created_at,
        )

    finally:
        db.close()

@router.post("/appointments/{appointment_id}/cancel")
def cancel_admin_appointment(appointment_id: int):
    db = SessionLocal()

    try:
        appointment = db.execute(
            select(Appointment)
            .where(Appointment.id == appointment_id)
            .with_for_update()
        ).scalar_one_or_none()

        if appointment is None:
            raise HTTPException(
                status_code=404,
                detail="Appointment not found.",
            )

        if appointment.status == "cancelled":
            raise HTTPException(
                status_code=400,
                detail="Appointment is already cancelled.",
            )

        if appointment.status == "completed":
            raise HTTPException(
                status_code=400,
                detail="Completed appointments cannot be cancelled.",
            )

        appointment.status = "cancelled"

        db.commit()

        return {
            "message": "Appointment cancelled successfully.",
            "appointment_id": appointment.id,
            "status": appointment.status,
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to cancel appointment.",
        )

    finally:
        db.close()

@router.post("/appointments/{appointment_id}/complete")
def complete_admin_appointment(appointment_id: int):
    db = SessionLocal()

    try:
        appointment = db.execute(
            select(Appointment)
            .where(Appointment.id == appointment_id)
            .with_for_update()
        ).scalar_one_or_none()

        if appointment is None:
            raise HTTPException(
                status_code=404,
                detail="Appointment not found.",
            )

        if appointment.status == "completed":
            raise HTTPException(
                status_code=400,
                detail="Appointment is already completed.",
            )

        if appointment.status == "cancelled":
            raise HTTPException(
                status_code=400,
                detail="Cancelled appointments cannot be completed.",
            )

        appointment.status = "completed"

        db.commit()

        return {
            "message": "Appointment completed successfully.",
            "appointment_id": appointment.id,
            "status": appointment.status,
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to complete appointment.",
        )

    finally:
        db.close()


@router.get("/doctors", response_model=list[AdminDoctorResponse])
def list_doctors():
    db = SessionLocal()

    try:
        today = date.today()

        doctors = (
            db.execute(
                select(Doctor)
                .order_by(Doctor.active.desc(), Doctor.name.asc())
            )
            .scalars()
            .all()
        )

        results = []

        for doctor in doctors:
            scheduled_count = db.execute(
                select(func.count(Appointment.id)).where(
                    Appointment.doctor_id == doctor.id,
                    Appointment.appointment_date == today,
                    Appointment.status == "scheduled",
                )
            ).scalar_one()

            remaining_capacity = max(
                doctor.daily_capacity - scheduled_count,
                0,
            )

            results.append(
                AdminDoctorResponse(
                    id=doctor.id,
                    name=doctor.name,
                    specialization=doctor.specialization,
                    daily_capacity=doctor.daily_capacity,
                    active=doctor.active,
                    today_scheduled=scheduled_count,
                    today_remaining_capacity=remaining_capacity,
                )
            )

        return results

    finally:
        db.close()

@router.get("/doctors/{doctor_id}", response_model=AdminDoctorResponse)
def get_doctor(doctor_id: int):
    db = SessionLocal()

    try:
        doctor = db.execute(
            select(Doctor).where(
                Doctor.id == doctor_id
            )
        ).scalar_one_or_none()

        if doctor is None:
            raise HTTPException(
                status_code=404,
                detail="Doctor not found.",
            )

        today = date.today()

        scheduled_count = db.execute(
            select(func.count(Appointment.id)).where(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date == today,
                Appointment.status == "scheduled",
            )
        ).scalar_one()

        return AdminDoctorResponse(
            id=doctor.id,
            name=doctor.name,
            specialization=doctor.specialization,
            daily_capacity=doctor.daily_capacity,
            active=doctor.active,
            today_scheduled=scheduled_count,
            today_remaining_capacity=max(
                doctor.daily_capacity - scheduled_count,
                0,
            ),
        )

    finally:
        db.close()

def _doctor_response(db, doctor: Doctor) -> AdminDoctorResponse:
    today = date.today()

    scheduled_count = db.execute(
        select(func.count(Appointment.id)).where(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date == today,
            Appointment.status == "scheduled",
        )
    ).scalar_one()

    return AdminDoctorResponse(
        id=doctor.id,
        name=doctor.name,
        specialization=doctor.specialization,
        daily_capacity=doctor.daily_capacity,
        active=doctor.active,
        today_scheduled=scheduled_count,
        today_remaining_capacity=max(
            doctor.daily_capacity - scheduled_count,
            0,
        ),
    )

@router.post(
    "/doctors",
    response_model=AdminDoctorResponse,
    status_code=201,
)
def create_doctor(payload: AdminDoctorCreate):
    db = SessionLocal()

    try:
        doctor = Doctor(
            name=payload.name.strip(),
            specialization=payload.specialization.strip(),
            daily_capacity=payload.daily_capacity,
            active=True,
        )

        db.add(doctor)
        db.commit()
        db.refresh(doctor)

        return AdminDoctorResponse(
            id=doctor.id,
            name=doctor.name,
            specialization=doctor.specialization,
            daily_capacity=doctor.daily_capacity,
            active=doctor.active,
            today_scheduled=0,
            today_remaining_capacity=doctor.daily_capacity,
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

@router.put(
    "/doctors/{doctor_id}",
    response_model=AdminDoctorResponse,
)
def update_doctor(
    doctor_id: int,
    payload: AdminDoctorUpdate,
):
    db = SessionLocal()

    try:
        doctor = db.execute(
            select(Doctor)
            .where(Doctor.id == doctor_id)
            .with_for_update()
        ).scalar_one_or_none()

        if doctor is None:
            raise HTTPException(
                status_code=404,
                detail="Doctor not found.",
            )

        doctor.name = payload.name.strip()
        doctor.specialization = payload.specialization.strip()
        doctor.daily_capacity = payload.daily_capacity

        db.commit()
        db.refresh(doctor)

        today = date.today()

        scheduled_count = db.execute(
            select(func.count(Appointment.id)).where(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date == today,
                Appointment.status == "scheduled",
            )
        ).scalar_one()

        return AdminDoctorResponse(
            id=doctor.id,
            name=doctor.name,
            specialization=doctor.specialization,
            daily_capacity=doctor.daily_capacity,
            active=doctor.active,
            today_scheduled=scheduled_count,
            today_remaining_capacity=max(
                doctor.daily_capacity - scheduled_count,
                0,
            ),
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

@router.post(
    "/doctors/{doctor_id}/activate",
    response_model=AdminDoctorResponse,
)
def activate_doctor(doctor_id: int):
    db = SessionLocal()

    try:
        doctor = db.execute(
            select(Doctor)
            .where(Doctor.id == doctor_id)
            .with_for_update()
        ).scalar_one_or_none()

        if doctor is None:
            raise HTTPException(
                status_code=404,
                detail="Doctor not found.",
            )

        doctor.active = True

        db.commit()
        db.refresh(doctor)

        return _doctor_response(db, doctor)

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

@router.post(
    "/doctors/{doctor_id}/deactivate",
    response_model=AdminDoctorResponse,
)
def deactivate_doctor(doctor_id: int):
    db = SessionLocal()

    try:
        doctor = db.execute(
            select(Doctor)
            .where(Doctor.id == doctor_id)
            .with_for_update()
        ).scalar_one_or_none()

        if doctor is None:
            raise HTTPException(
                status_code=404,
                detail="Doctor not found.",
            )

        doctor.active = False

        db.commit()
        db.refresh(doctor)

        return _doctor_response(db, doctor)

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


@router.get(
    "/reports/appointments",
    response_model=list[AppointmentReportItem],
)
def appointment_report(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    doctor_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
):
    db = SessionLocal()

    try:
        if start_date and end_date and start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="start_date cannot be after end_date",
            )

        statement = (
            select(Appointment, Doctor)
            .join(Doctor, Appointment.doctor_id == Doctor.id)
            .order_by(
                Appointment.appointment_date.desc(),
                Appointment.id.desc(),
            )
        )

        if start_date:
            statement = statement.where(
                Appointment.appointment_date >= start_date
            )

        if end_date:
            statement = statement.where(
                Appointment.appointment_date <= end_date
            )

        if doctor_id:
            statement = statement.where(
                Appointment.doctor_id == doctor_id
            )

        if status:
            statement = statement.where(
                Appointment.status == status
            )

        if search:
            search_value = f"%{search.strip()}%"

            statement = statement.where(
                Appointment.patient_name.ilike(search_value)
                | Appointment.patient_phone.ilike(search_value)
            )

        rows = db.execute(statement).all()

        return [
            AppointmentReportItem(
                id=appointment.id,
                patient_number=appointment.patient_number,
                patient_name=appointment.patient_name,
                patient_phone=appointment.patient_phone,
                patient_email=appointment.patient_email,
                doctor_id=doctor.id,
                doctor_name=doctor.name,
                doctor_specialization=doctor.specialization,
                appointment_date=appointment.appointment_date,
                status=appointment.status,
                created_at=appointment.created_at,
            )
            for appointment, doctor in rows
        ]

    finally:
        db.close()


@router.get("/reports/appointments/excel")
def export_appointments_excel(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    doctor_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
):
    db = SessionLocal()

    try:
        statement = (
            select(Appointment, Doctor)
            .join(Doctor, Appointment.doctor_id == Doctor.id)
            .order_by(
                Appointment.appointment_date.asc(),
                Appointment.id.asc(),
            )
        )

        if start_date:
            statement = statement.where(
                Appointment.appointment_date >= start_date
            )

        if end_date:
            statement = statement.where(
                Appointment.appointment_date <= end_date
            )

        if doctor_id:
            statement = statement.where(
                Appointment.doctor_id == doctor_id
            )

        if status:
            statement = statement.where(
                Appointment.status == status
            )

        rows = db.execute(statement).all()

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Appointments"

        headers = [
            "ID",
            "Patient Number",
            "Patient Name",
            "Phone",
            "Email",
            "Doctor",
            "Specialization",
            "Appointment Date",
            "Status",
            "Created At",
        ]

        worksheet.append(headers)

        for appointment, doctor in rows:
            worksheet.append([
                appointment.id,
                appointment.patient_number,
                appointment.patient_name,
                appointment.patient_phone,
                appointment.patient_email or "",
                doctor.name,
                doctor.specialization,
                appointment.appointment_date,
                appointment.status,
                appointment.created_at,
            ])

        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions

        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter

            for cell in column:
                value = str(cell.value or "")
                max_length = max(max_length, len(value))

            worksheet.column_dimensions[column_letter].width = min(
                max_length + 2,
                40,
            )

        output = BytesIO()
        workbook.save(output)
        output.seek(0)

        return StreamingResponse(
            output,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition":
                    "attachment; filename=appointments.xlsx"
            },
        )

    finally:
        db.close()


@router.get("/reports/appointments/pdf")
def export_appointments_pdf(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    doctor_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
):
    db = SessionLocal()

    try:
        statement = (
            select(Appointment, Doctor)
            .join(Doctor, Appointment.doctor_id == Doctor.id)
            .order_by(
                Appointment.appointment_date.asc(),
                Appointment.id.asc(),
            )
        )

        if start_date:
            statement = statement.where(
                Appointment.appointment_date >= start_date
            )

        if end_date:
            statement = statement.where(
                Appointment.appointment_date <= end_date
            )

        if doctor_id:
            statement = statement.where(
                Appointment.doctor_id == doctor_id
            )

        if status:
            statement = statement.where(
                Appointment.status == status
            )

        rows = db.execute(statement).all()

        output = BytesIO()

        document = SimpleDocTemplate(
            output,
            pagesize=landscape(A4),
            rightMargin=20,
            leftMargin=20,
            topMargin=20,
            bottomMargin=20,
        )

        data = [[
            "ID",
            "Patient #",
            "Patient",
            "Phone",
            "Doctor",
            "Specialization",
            "Date",
            "Status",
        ]]

        for appointment, doctor in rows:
            data.append([
                appointment.id,
                appointment.patient_number,
                appointment.patient_name,
                appointment.patient_phone,
                doctor.name,
                doctor.specialization,
                str(appointment.appointment_date),
                appointment.status,
            ])

        table = Table(
            data,
            repeatRows=1,
        )

        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.black),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )

        document.build([table])

        output.seek(0)

        return StreamingResponse(
            output,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                    "attachment; filename=appointments.pdf"
            },
        )

    finally:
        db.close()