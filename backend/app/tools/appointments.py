from datetime import date

from langchain.tools import tool
from sqlalchemy import func, select

from app.database.database import SessionLocal
from app.database.models import Appointment, Doctor


# checking daily appointment capacity
@tool
def check_availability(
    doctor_id: int,
    appointment_date: str,
) -> str:
    """
    Check whether a doctor has remaining appointment capacity
    on a specific date.

    doctor_id must be the ID of the doctor.
    appointment_date must use YYYY-MM-DD format.
    """

    if doctor_id <= 0:
        return "Invalid doctor ID."

    try:
        requested_date = date.fromisoformat(appointment_date)
    except ValueError:
        return "Invalid appointment date. Please use YYYY-MM-DD format."

    db = SessionLocal()

    try:
        # -------------------------------------------------
        # 1. Find active doctor
        # -------------------------------------------------

        doctor_statement = select(Doctor).where(
            Doctor.id == doctor_id,
            Doctor.active.is_(True),
        )

        doctor = db.execute(
            doctor_statement
        ).scalar_one_or_none()

        if doctor is None:
            return (
                "The requested doctor does not exist "
                "or is not currently active."
            )

        # -------------------------------------------------
        # 2. Validate doctor's daily capacity
        # -------------------------------------------------

        if doctor.daily_capacity <= 0:
            return (
                f"No appointments can be booked for "
                f"{doctor.name}."
            )

        # -------------------------------------------------
        # 3. Count scheduled appointments for this date
        # -------------------------------------------------

        booked_statement = select(
            func.count(Appointment.id)
        ).where(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == requested_date,
            Appointment.status == "scheduled",
        )

        booked_count = db.execute(
            booked_statement
        ).scalar_one()

        # -------------------------------------------------
        # 4. Calculate remaining capacity
        # -------------------------------------------------

        remaining_capacity = (
            doctor.daily_capacity - booked_count
        )

        if remaining_capacity <= 0:
            return (
                f"{doctor.name} is fully booked on "
                f"{appointment_date}. "
                f"Daily capacity: {doctor.daily_capacity}. "
                f"Scheduled patients: {booked_count}."
            )

        return (
            f"{doctor.name} has availability on "
            f"{appointment_date}. "
            f"Daily capacity: {doctor.daily_capacity}. "
            f"Scheduled patients: {booked_count}. "
            f"Remaining capacity: {remaining_capacity}."
        )

    finally:
        db.close()


# appointment booking tool
@tool
def book_appointment(
    doctor_id: int,
    patient_name: str,
    patient_phone: str,
    appointment_date: str,
    patient_email: str = "",
) -> str:
    """
    Book an appointment for a patient.

    The system uses daily patient capacity rather than fixed
    appointment time slots.

    doctor_id must be the ID of the doctor.
    appointment_date must use YYYY-MM-DD format.
    """

    # ---------------------------------------------------------
    # 1. Validate basic input
    # ---------------------------------------------------------

    patient_name = patient_name.strip()
    patient_phone = patient_phone.strip()
    patient_email = patient_email.strip()

    if not patient_name:
        return "Patient name is required."

    if len(patient_name) > 100:
        return "Patient name must not exceed 100 characters."

    if not patient_phone:
        return "Patient phone number is required."

    if len(patient_phone) > 30:
        return "Patient phone number must not exceed 30 characters."

    if patient_email and len(patient_email) > 150:
        return "Patient email must not exceed 150 characters."

    try:
        requested_date = date.fromisoformat(appointment_date)
    except ValueError:
        return "Invalid appointment date. Please use YYYY-MM-DD format."

    # Prevent booking dates in the past
    if requested_date < date.today():
        return "Appointments cannot be booked for a date in the past."

    if doctor_id <= 0:
        return "Invalid doctor ID."

    db = SessionLocal()

    try:
        # -----------------------------------------------------
        # 2. Start transaction
        # -----------------------------------------------------

        with db.begin():

            # -------------------------------------------------
            # 3. Verify doctor exists and is active
            # -------------------------------------------------

            doctor_statement = (
                select(Doctor)
                .where(
                    Doctor.id == doctor_id,
                    Doctor.active.is_(True),
                )
                .with_for_update()
            )

            doctor = db.execute(
                doctor_statement
            ).scalar_one_or_none()

            if doctor is None:
                return "The requested doctor does not exist or is not currently active."

            # -------------------------------------------------
            # 4. Lock daily capacity row
            # -------------------------------------------------

            # capacity_statement = (
            #     select(DailyCapacity)
            #     .where(
            #         DailyCapacity.doctor_id == doctor_id,
            #         DailyCapacity.appointment_date == requested_date,
            #     )
            #     .with_for_update()
            # )

            # capacity = db.execute(
            #     capacity_statement
            # ).scalar_one_or_none()

            # if capacity is None:
            #     return (
            #         f"No appointment capacity has been configured "
            #         f"for {doctor.name} on {appointment_date}."
            #     )

            # -------------------------------------------------
            # 5. Validate configured capacity
            # -------------------------------------------------

            if doctor.daily_capacity <= 0:
                return (
                    f"No appointments can be booked for "
                    f"{doctor.name}."
                )

            # -------------------------------------------------
            # 6. Count currently scheduled patients
            # -------------------------------------------------

            booked_count_statement = select(
                func.count(Appointment.id)
            ).where(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == requested_date,
                Appointment.status == "scheduled",
            )

            booked_count = db.execute(
                booked_count_statement
            ).scalar_one()

            # -------------------------------------------------
            # 7. Check daily capacity
            # -------------------------------------------------

            if booked_count >= doctor.daily_capacity:
                return (
                    f"Sorry, {doctor.name} is fully booked on "
                    f"{appointment_date}. "
                    f"Daily capacity is "
                    f"{doctor.daily_capacity} patients."
                )

            # -------------------------------------------------
            # 8. Find the next patient number
            # -------------------------------------------------

            max_number_statement = select(
                func.max(Appointment.patient_number)
            ).where(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == requested_date,
            )

            max_patient_number = db.execute(
                max_number_statement
            ).scalar_one()

            if max_patient_number is None:
                next_patient_number = 1
            else:
                next_patient_number = max_patient_number + 1

            # -------------------------------------------------
            # 9. Create appointment
            # -------------------------------------------------

            appointment = Appointment(
                doctor_id=doctor_id,
                patient_number=next_patient_number,
                patient_name=patient_name,
                patient_phone=patient_phone,
                patient_email=patient_email or None,
                appointment_date=requested_date,
                status="scheduled",
            )

            db.add(appointment)

            # Generate ID before transaction commits
            db.flush()

        # -----------------------------------------------------
        # 10. Transaction committed successfully
        # -----------------------------------------------------

        return (
            f"Appointment successfully booked.\n"
            f"Appointment ID: {appointment.id}\n"
            f"Doctor: {doctor.name}\n"
            f"Patient: {patient_name}\n"
            f"Patient Number: {next_patient_number}\n"
            f"Date: {appointment_date}"
        )

    except Exception:
        db.rollback()
        return (
            "Sorry, I could not complete the appointment booking. "
            "Please try again."
        )

    finally:
        db.close()


@tool
def get_appointment(
    appointment_id: int,
    patient_phone: str,
) -> str:
    """
    Retrieve an appointment using the appointment ID
    and the patient's phone number.

    Both values are required for verification.
    """

    # ---------------------------------------------------------
    # 1. Validate input
    # ---------------------------------------------------------

    if appointment_id <= 0:
        return "Invalid appointment ID."

    patient_phone = patient_phone.strip()

    if not patient_phone:
        return "Patient phone number is required."

    if len(patient_phone) > 30:
        return "Patient phone number must not exceed 30 characters."

    db = SessionLocal()

    try:
        # -----------------------------------------------------
        # 2. Find appointment
        # -----------------------------------------------------

        statement = (
            select(Appointment)
            .where(
                Appointment.id == appointment_id,
                Appointment.patient_phone == patient_phone,
            )
        )

        appointment = db.execute(
            statement
        ).scalar_one_or_none()

        # -----------------------------------------------------
        # 3. Appointment not found
        # -----------------------------------------------------

        if appointment is None:
            return (
                "No appointment was found with the provided "
                "appointment ID and phone number."
            )

        # -----------------------------------------------------
        # 4. Return limited appointment information
        # -----------------------------------------------------

        return (
            f"Appointment found.\n"
            f"Appointment ID: {appointment.id}\n"
            f"Patient Number: {appointment.patient_number}\n"
            f"Date: {appointment.appointment_date}\n"
            f"Status: {appointment.status}"
        )

    finally:
        db.close()


@tool
def cancel_appointment(
    appointment_id: int,
    patient_phone: str,
) -> str:
    """
    Cancel an existing appointment.

    Both appointment ID and patient phone are required
    to verify the appointment.
    """

    # ---------------------------------------------------------
    # 1. Validate input
    # ---------------------------------------------------------

    if appointment_id <= 0:
        return "Invalid appointment ID."

    patient_phone = patient_phone.strip()

    if not patient_phone:
        return "Patient phone number is required."

    if len(patient_phone) > 30:
        return "Patient phone number must not exceed 30 characters."

    db = SessionLocal()

    try:
        # -----------------------------------------------------
        # 2. Find appointment
        # -----------------------------------------------------

        statement = (
            select(Appointment)
            .where(
                Appointment.id == appointment_id,
                Appointment.patient_phone == patient_phone,
            )
            .with_for_update()
        )

        appointment = db.execute(
            statement
        ).scalar_one_or_none()

        # -----------------------------------------------------
        # 3. Appointment not found
        # -----------------------------------------------------

        if appointment is None:
            return (
                "No appointment was found with the provided "
                "appointment ID and phone number."
            )

        # -----------------------------------------------------
        # 4. Check current status
        # -----------------------------------------------------

        if appointment.status == "cancelled":
            return "This appointment has already been cancelled."

        if appointment.status != "scheduled":
            return (
                f"This appointment cannot be cancelled because "
                f"its current status is '{appointment.status}'."
            )

        # -----------------------------------------------------
        # 5. Cancel appointment
        # -----------------------------------------------------

        appointment.status = "cancelled"

        db.commit()

        return (
            f"Appointment successfully cancelled.\n"
            f"Appointment ID: {appointment.id}\n"
            f"Patient Number: {appointment.patient_number}\n"
            f"Date: {appointment.appointment_date}"
        )

    except Exception:
        db.rollback()

        return (
            "Sorry, I could not cancel the appointment. "
            "Please try again."
        )

    finally:
        db.close()


@tool
def reschedule_appointment(
    appointment_id: int,
    patient_phone: str,
    new_appointment_date: str,
) -> str:
    """
    Reschedule an existing appointment to another date.

    The doctor remains the same.
    The destination date must have available capacity.

    appointment_id must be a positive integer.
    patient_phone must match the existing appointment.
    new_appointment_date must use YYYY-MM-DD format.
    """

    # -----------------------------
    # 1. Validate appointment ID
    # -----------------------------
    if appointment_id <= 0:
        return "Invalid appointment ID."

    # -----------------------------
    # 2. Validate phone number
    # -----------------------------
    patient_phone = patient_phone.strip()

    if not patient_phone:
        return "Patient phone number is required."

    if len(patient_phone) > 30:
        return "Patient phone number must not exceed 30 characters."

    # -----------------------------
    # 3. Validate new date
    # -----------------------------
    try:
        new_date = date.fromisoformat(new_appointment_date)
    except ValueError:
        return "Invalid appointment date. Please use YYYY-MM-DD format."

    # -----------------------------
    # 4. Prevent past-date booking
    # -----------------------------
    if new_date < date.today():
        return "The new appointment date cannot be in the past."

    db = SessionLocal()

    try:
        # ----------------------------------------
        # 5. Find the appointment
        # ----------------------------------------
        appointment_statement = (
            select(Appointment)
            .where(
                Appointment.id == appointment_id,
                Appointment.patient_phone == patient_phone,
            )
            .with_for_update()
        )

        appointment = db.execute(
            appointment_statement
        ).scalar_one_or_none()

        if appointment is None:
            return (
                "No appointment was found with the provided "
                "appointment ID and phone number."
            )

        # ----------------------------------------
        # 6. Check appointment status
        # ----------------------------------------
        if appointment.status == "cancelled":
            return "A cancelled appointment cannot be rescheduled."

        if appointment.status != "scheduled":
            return (
                f"This appointment cannot be rescheduled "
                f"because its current status is '{appointment.status}'."
            )

        # ----------------------------------------
        # 7. Prevent same-date rescheduling
        # ----------------------------------------
        if appointment.appointment_date == new_date:
            return (
                "The appointment is already scheduled "
                "for this date."
            )

        doctor_id = appointment.doctor_id
        old_date = appointment.appointment_date

        # ----------------------------------------
        # 8. Validate doctor's daily capacity
        # ----------------------------------------

        doctor_statement = (
            select(Doctor)
            .where(
                Doctor.id == doctor_id,
                Doctor.active.is_(True),
            )
            .with_for_update()
        )

        doctor = db.execute(
            doctor_statement
        ).scalar_one_or_none()

        if doctor is None:
            return (
                "The doctor is no longer available."
            )

        if doctor.daily_capacity <= 0:
            return (
                f"No appointments can be booked for "
                f"{doctor.name}."
            )

        # ----------------------------------------
        # 9. Count scheduled appointments
        # ----------------------------------------
        booked_statement = select(
            func.count(Appointment.id)
        ).where(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == new_date,
            Appointment.status == "scheduled",
        )

        booked_count = db.execute(
            booked_statement
        ).scalar_one()

        # ----------------------------------------
        # 10. Check destination capacity
        # ----------------------------------------
        if booked_count >= doctor.daily_capacity:
            return (
                f"Sorry, the doctor is fully booked on "
                f"{new_appointment_date}."
            )

        # ----------------------------------------
        # 11. Find next patient number
        # ----------------------------------------
        max_number_statement = select(
            func.max(Appointment.patient_number)
        ).where(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == new_date,
        )

        max_patient_number = db.execute(
            max_number_statement
        ).scalar_one()

        if max_patient_number is None:
            new_patient_number = 1
        else:
            new_patient_number = max_patient_number + 1

        # ----------------------------------------
        # 12. Move appointment
        # ----------------------------------------
        appointment.appointment_date = new_date
        appointment.patient_number = new_patient_number

        db.commit()

        return (
            "Appointment successfully rescheduled.\n"
            f"Appointment ID: {appointment.id}\n"
            f"Patient: {appointment.patient_name}\n"
            f"Doctor ID: {appointment.doctor_id}\n"
            f"Previous Date: {old_date}\n"
            f"New Date: {appointment.appointment_date}\n"
            f"New Patient Number: {appointment.patient_number}"
        )

    except Exception:
        db.rollback()
        return (
            "Sorry, I could not reschedule the appointment. "
            "Please try again."
        )

    finally:
        db.close()


@tool
def complete_appointment(
    appointment_id: int,
    patient_phone: str,
) -> str:
    """
    Mark a scheduled appointment as completed.

    The appointment ID and patient phone number are required
    to identify the appointment.
    """

    # -----------------------------
    # 1. Validate appointment ID
    # -----------------------------
    if appointment_id <= 0:
        return "Invalid appointment ID."

    # -----------------------------
    # 2. Validate phone number
    # -----------------------------
    patient_phone = patient_phone.strip()

    if not patient_phone:
        return "Patient phone number is required."

    if len(patient_phone) > 30:
        return "Patient phone number must not exceed 30 characters."

    db = SessionLocal()

    try:
        # ----------------------------------------
        # 3. Find and lock appointment
        # ----------------------------------------
        statement = (
            select(Appointment)
            .where(
                Appointment.id == appointment_id,
                Appointment.patient_phone == patient_phone,
            )
            .with_for_update()
        )

        appointment = db.execute(
            statement
        ).scalar_one_or_none()

        if appointment is None:
            return (
                "No appointment was found with the provided "
                "appointment ID and phone number."
            )

        # ----------------------------------------
        # 4. Validate current status
        # ----------------------------------------
        if appointment.status == "completed":
            return "This appointment has already been completed."

        if appointment.status == "cancelled":
            return "A cancelled appointment cannot be completed."

        if appointment.status != "scheduled":
            return (
                f"This appointment cannot be completed "
                f"because its current status is '{appointment.status}'."
            )

        # ----------------------------------------
        # 5. Mark appointment completed
        # ----------------------------------------
        appointment.status = "completed"

        db.commit()

        return (
            "Appointment successfully marked as completed.\n"
            f"Appointment ID: {appointment.id}\n"
            f"Patient: {appointment.patient_name}\n"
            f"Patient Number: {appointment.patient_number}\n"
            f"Date: {appointment.appointment_date}\n"
            f"Status: {appointment.status}"
        )

    except Exception:
        db.rollback()

        return (
            "Sorry, I could not complete the appointment. "
            "Please try again."
        )

    finally:
        db.close()

@tool
def find_doctor(name: str) -> str:
    """
    Find an active doctor by name.

    The patient may provide a full name or a partial name,
    such as "Dr. Rahman" or "Rahman".

    Returns the doctor's ID, name, and specialization.
    """

    name = name.strip()

    if not name:
        return "Doctor name is required."

    if len(name) > 100:
        return "Doctor name must not exceed 100 characters."

    db = SessionLocal()

    try:
        statement = (
            select(Doctor)
            .where(
                Doctor.active.is_(True),
                Doctor.name.ilike(f"%{name}%"),
            )
        )

        doctors = db.execute(statement).scalars().all()

        if not doctors:
            return f"No active doctor was found matching '{name}'."

        if len(doctors) > 1:
            results = "\n".join(
                f"- Doctor ID: {doctor.id}, "
                f"Name: {doctor.name}, "
                f"Specialization: {doctor.specialization}"
                for doctor in doctors
            )

            return (
                "Multiple doctors were found. "
                "Please ask the patient to specify which doctor they want:\n"
                f"{results}"
            )

        doctor = doctors[0]

        return (
            f"Doctor found.\n"
            f"Doctor ID: {doctor.id}\n"
            f"Name: {doctor.name}\n"
            f"Specialization: {doctor.specialization}"
        )

    finally:
        db.close()



"""
                    ┌──────────────────────┐
                    │     Patient Chat     │
                    └──────────┬───────────┘
                               │
                               ▼
                     ┌─────────────────┐
                     │    AI Agent     │
                     └────────┬────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
   New Appointment       Existing Booking    General Query
          │                   │
          ▼                   ▼
    find_doctor()       get_appointment()
          │                   │
          ▼              ┌─────┴─────┐
 check_availability()    ▼           ▼
          │          cancel()    reschedule()
          ▼
 book_appointment()


 """