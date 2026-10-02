from datetime import date, datetime, UTC

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base

"""
# Creating the structure model for the database tables using SQLAlchemy ORM.

The Database Model structure is as follows:
Doctor
   │
   ├── DailyCapacity
   │      └── maximum_patients
   │
   └── Appointments
          ├── Patient #1
          ├── Patient #2
          ├── Patient #3
          └── ...
"""

APPOINTMENT_STATUSES = {
    "scheduled",
    "cancelled",
    "completed",
}

# model class for the doctors table
class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    specialization: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    daily_capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10,
    )

    active: Mapped[bool] = mapped_column(
        default=True,
    )

    appointments = relationship(
        "Appointment",
        back_populates="doctor",
    )


# model class for the patients table
class Appointment(Base):
    __tablename__ = "appointments"

    __table_args__ = (
        UniqueConstraint(
            "doctor_id",
            "appointment_date",
            "patient_number",
            name="uq_doctor_date_patient_number",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id"),
        nullable=False,
    )

    patient_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    patient_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    patient_phone: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    patient_email: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    appointment_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="scheduled",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    doctor = relationship(
        "Doctor",
        back_populates="appointments",
    )



# model class for Daily Capacity table
# class DailyCapacity(Base):
#     __tablename__ = "daily_capacities"

#     __table_args__ = (
#         UniqueConstraint(
#             "doctor_id",
#             "appointment_date",
#             name="uq_doctor_capacity_date"
#         ),
#     )

#     id: Mapped[int] = mapped_column(
#         primary_key=True,
#         autoincrement=True
#     )

#     doctor_id: Mapped[int] = mapped_column(
#         ForeignKey("doctors.id"),
#         nullable=False
#     )

#     appointment_date: Mapped[date] = mapped_column(
#         Date,
#         nullable=False
#     )

#     maximum_patients: Mapped[int] = mapped_column(
#         Integer,
#         nullable=False
#     )

#     doctor = relationship(
#         "Doctor",
#         back_populates="daily_capacities"
#     )