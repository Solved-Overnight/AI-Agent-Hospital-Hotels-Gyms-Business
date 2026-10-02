from datetime import date

from sqlalchemy import func, select

from app.database.database import SessionLocal
from app.database.models import Appointment, DailyCapacity, Doctor
from app.tools.appointments import (
    book_appointment,
    cancel_appointment,
    check_availability,
    complete_appointment,
    get_appointment,
    reschedule_appointment,
)


# ============================================================
# TEST CONFIGURATION
# ============================================================

TEST_DOCTOR_NAME = "Test Dentist"
TEST_DOCTOR_SPECIALIZATION = "General Dentistry"

TEST_DATE_1 = "2026-10-01"
TEST_DATE_2 = "2026-10-02"

TEST_PHONE_1 = "01700000001"
TEST_PHONE_2 = "01700000002"
TEST_PHONE_3 = "01700000003"


# ============================================================
# DATABASE SETUP
# ============================================================

def setup_test_data():
    """
    Create a dedicated test doctor and daily capacities.
    """

    db = SessionLocal()

    try:
        # Remove previous test data first
        old_doctor = db.execute(
            select(Doctor).where(
                Doctor.name == TEST_DOCTOR_NAME
            )
        ).scalar_one_or_none()

        if old_doctor:
            db.query(Appointment).filter(
                Appointment.doctor_id == old_doctor.id
            ).delete(
                synchronize_session=False
            )

            db.query(DailyCapacity).filter(
                DailyCapacity.doctor_id == old_doctor.id
            ).delete(
                synchronize_session=False
            )

            db.delete(old_doctor)
            db.commit()

        # Create test doctor
        doctor = Doctor(
            name=TEST_DOCTOR_NAME,
            specialization=TEST_DOCTOR_SPECIALIZATION,
            active=True,
        )

        db.add(doctor)
        db.flush()

        # Capacity for October 1
        capacity_1 = DailyCapacity(
            doctor_id=doctor.id,
            appointment_date=date.fromisoformat(TEST_DATE_1),
            maximum_patients=3,
        )

        # Capacity for October 2
        capacity_2 = DailyCapacity(
            doctor_id=doctor.id,
            appointment_date=date.fromisoformat(TEST_DATE_2),
            maximum_patients=3,
        )

        db.add_all([
            capacity_1,
            capacity_2,
        ])

        db.commit()

        return doctor.id

    finally:
        db.close()


# ============================================================
# CLEANUP
# ============================================================

def cleanup_test_data(doctor_id):
    """
    Delete all test appointments, capacities,
    and the test doctor.
    """

    db = SessionLocal()

    try:
        db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id
        ).delete(
            synchronize_session=False
        )

        db.query(DailyCapacity).filter(
            DailyCapacity.doctor_id == doctor_id
        ).delete(
            synchronize_session=False
        )

        db.query(Doctor).filter(
            Doctor.id == doctor_id
        ).delete(
            synchronize_session=False
        )

        db.commit()

    finally:
        db.close()


# ============================================================
# TEST 1 — BOOK APPOINTMENT
# ============================================================

def test_book_appointment():

    doctor_id = setup_test_data()

    try:
        result = book_appointment.invoke({
            "doctor_id": doctor_id,
            "patient_name": "Test Patient One",
            "patient_phone": TEST_PHONE_1,
            "appointment_date": TEST_DATE_1,
        })

        assert "successfully booked" in result.lower()
        assert "Patient Number: 1" in result

    finally:
        cleanup_test_data(doctor_id)


# ============================================================
# TEST 2 — PATIENT NUMBERING
# ============================================================

def test_patient_numbering():

    doctor_id = setup_test_data()

    try:
        result_1 = book_appointment.invoke({
            "doctor_id": doctor_id,
            "patient_name": "Patient One",
            "patient_phone": TEST_PHONE_1,
            "appointment_date": TEST_DATE_1,
        })

        result_2 = book_appointment.invoke({
            "doctor_id": doctor_id,
            "patient_name": "Patient Two",
            "patient_phone": TEST_PHONE_2,
            "appointment_date": TEST_DATE_1,
        })

        result_3 = book_appointment.invoke({
            "doctor_id": doctor_id,
            "patient_name": "Patient Three",
            "patient_phone": TEST_PHONE_3,
            "appointment_date": TEST_DATE_1,
        })

        assert "Patient Number: 1" in result_1
        assert "Patient Number: 2" in result_2
        assert "Patient Number: 3" in result_3

    finally:
        cleanup_test_data(doctor_id)


# ============================================================
# TEST 3 — CAPACITY
# ============================================================

def test_capacity():

    doctor_id = setup_test_data()

    try:
        for i in range(3):

            book_appointment.invoke({
                "doctor_id": doctor_id,
                "patient_name": f"Patient {i}",
                "patient_phone": f"0170000000{i}",
                "appointment_date": TEST_DATE_1,
            })

        result = check_availability.invoke({
            "doctor_id": doctor_id,
            "appointment_date": TEST_DATE_1,
        })

        assert "fully booked" in result.lower()

    finally:
        cleanup_test_data(doctor_id)


# ============================================================
# TEST 4 — LOOKUP
# ============================================================

def test_get_appointment():

    doctor_id = setup_test_data()

    try:
        result = book_appointment.invoke({
            "doctor_id": doctor_id,
            "patient_name": "Lookup Patient",
            "patient_phone": TEST_PHONE_1,
            "appointment_date": TEST_DATE_1,
        })

        # Extract appointment ID from booking result
        appointment_id = int(
            result.split("Appointment ID: ")[1]
            .split("\n")[0]
        )

        lookup_result = get_appointment.invoke({
            "appointment_id": appointment_id,
            "patient_phone": TEST_PHONE_1,
        })

        assert "Appointment found" in lookup_result
        assert "Patient Number: 1" in lookup_result

    finally:
        cleanup_test_data(doctor_id)


# ============================================================
# TEST 5 — WRONG PHONE LOOKUP
# ============================================================

def test_lookup_wrong_phone():

    doctor_id = setup_test_data()

    try:
        result = book_appointment.invoke({
            "doctor_id": doctor_id,
            "patient_name": "Private Patient",
            "patient_phone": TEST_PHONE_1,
            "appointment_date": TEST_DATE_1,
        })

        appointment_id = int(
            result.split("Appointment ID: ")[1]
            .split("\n")[0]
        )

        lookup_result = get_appointment.invoke({
            "appointment_id": appointment_id,
            "patient_phone": "01999999999",
        })

        assert "No appointment was found" in lookup_result

    finally:
        cleanup_test_data(doctor_id)


# ============================================================
# TEST 6 — CANCELLATION
# ============================================================

def test_cancel_appointment():

    doctor_id = setup_test_data()

    try:
        result = book_appointment.invoke({
            "doctor_id": doctor_id,
            "patient_name": "Cancel Patient",
            "patient_phone": TEST_PHONE_1,
            "appointment_date": TEST_DATE_1,
        })

        appointment_id = int(
            result.split("Appointment ID: ")[1]
            .split("\n")[0]
        )

        cancel_result = cancel_appointment.invoke({
            "appointment_id": appointment_id,
            "patient_phone": TEST_PHONE_1,
        })

        assert "successfully cancelled" in cancel_result.lower()

    finally:
        cleanup_test_data(doctor_id)


# ============================================================
# TEST 7 — DOUBLE CANCELLATION
# ============================================================

def test_double_cancellation():

    doctor_id = setup_test_data()

    try:
        result = book_appointment.invoke({
            "doctor_id": doctor_id,
            "patient_name": "Double Cancel",
            "patient_phone": TEST_PHONE_1,
            "appointment_date": TEST_DATE_1,
        })

        appointment_id = int(
            result.split("Appointment ID: ")[1]
            .split("\n")[0]
        )

        cancel_appointment.invoke({
            "appointment_id": appointment_id,
            "patient_phone": TEST_PHONE_1,
        })

        second_result = cancel_appointment.invoke({
            "appointment_id": appointment_id,
            "patient_phone": TEST_PHONE_1,
        })

        assert "already been cancelled" in second_result.lower()

    finally:
        cleanup_test_data(doctor_id)


# ============================================================
# TEST 8 — RESCHEDULING
# ============================================================

def test_reschedule_appointment():

    doctor_id = setup_test_data()

    try:
        result = book_appointment.invoke({
            "doctor_id": doctor_id,
            "patient_name": "Reschedule Patient",
            "patient_phone": TEST_PHONE_1,
            "appointment_date": TEST_DATE_1,
        })

        appointment_id = int(
            result.split("Appointment ID: ")[1]
            .split("\n")[0]
        )

        reschedule_result = reschedule_appointment.invoke({
            "appointment_id": appointment_id,
            "patient_phone": TEST_PHONE_1,
            "new_appointment_date": TEST_DATE_2,
        })

        assert "successfully rescheduled" in reschedule_result.lower()
        assert TEST_DATE_2 in reschedule_result

    finally:
        cleanup_test_data(doctor_id)


# ============================================================
# TEST 9 — RESCHEDULE TO FULL DATE
# ============================================================

def test_reschedule_to_full_date():

    doctor_id = setup_test_data()

    try:
        # Fill October 2
        for i in range(3):

            book_appointment.invoke({
                "doctor_id": doctor_id,
                "patient_name": f"Existing {i}",
                "patient_phone": f"0180000000{i}",
                "appointment_date": TEST_DATE_2,
            })

        # Create appointment on October 1
        result = book_appointment.invoke({
            "doctor_id": doctor_id,
            "patient_name": "Moving Patient",
            "patient_phone": TEST_PHONE_1,
            "appointment_date": TEST_DATE_1,
        })

        appointment_id = int(
            result.split("Appointment ID: ")[1]
            .split("\n")[0]
        )

        result = reschedule_appointment.invoke({
            "appointment_id": appointment_id,
            "patient_phone": TEST_PHONE_1,
            "new_appointment_date": TEST_DATE_2,
        })

        assert "fully booked" in result.lower()

    finally:
        cleanup_test_data(doctor_id)


# ============================================================
# TEST 10 — COMPLETION
# ============================================================

def test_complete_appointment():

    doctor_id = setup_test_data()

    try:
        result = book_appointment.invoke({
            "doctor_id": doctor_id,
            "patient_name": "Completed Patient",
            "patient_phone": TEST_PHONE_1,
            "appointment_date": TEST_DATE_1,
        })

        appointment_id = int(
            result.split("Appointment ID: ")[1]
            .split("\n")[0]
        )

        complete_result = complete_appointment.invoke({
            "appointment_id": appointment_id,
            "patient_phone": TEST_PHONE_1,
        })

        assert "successfully marked as completed" in complete_result.lower()

    finally:
        cleanup_test_data(doctor_id)


# ============================================================
# TEST 11 — COMPLETED CANNOT BE CANCELLED
# ============================================================

def test_completed_cannot_be_cancelled():

    doctor_id = setup_test_data()

    try:
        result = book_appointment.invoke({
            "doctor_id": doctor_id,
            "patient_name": "Completed Patient",
            "patient_phone": TEST_PHONE_1,
            "appointment_date": TEST_DATE_1,
        })

        appointment_id = int(
            result.split("Appointment ID: ")[1]
            .split("\n")[0]
        )

        complete_appointment.invoke({
            "appointment_id": appointment_id,
            "patient_phone": TEST_PHONE_1,
        })

        cancel_result = cancel_appointment.invoke({
            "appointment_id": appointment_id,
            "patient_phone": TEST_PHONE_1,
        })

        assert "cannot be cancelled" in cancel_result.lower()

    finally:
        cleanup_test_data(doctor_id)


# ============================================================
# TEST 12 — CANCELLED CANNOT BE RESCHEDULED
# ============================================================

def test_cancelled_cannot_be_rescheduled():

    doctor_id = setup_test_data()

    try:
        result = book_appointment.invoke({
            "doctor_id": doctor_id,
            "patient_name": "Cancelled Patient",
            "patient_phone": TEST_PHONE_1,
            "appointment_date": TEST_DATE_1,
        })

        appointment_id = int(
            result.split("Appointment ID: ")[1]
            .split("\n")[0]
        )

        cancel_appointment.invoke({
            "appointment_id": appointment_id,
            "patient_phone": TEST_PHONE_1,
        })

        reschedule_result = reschedule_appointment.invoke({
            "appointment_id": appointment_id,
            "patient_phone": TEST_PHONE_1,
            "new_appointment_date": TEST_DATE_2,
        })

        assert "cannot be rescheduled" in reschedule_result.lower()

    finally:
        cleanup_test_data(doctor_id)


# ============================================================
# TEST 13 — INVALID DATE
# ============================================================

def test_invalid_booking_date():

    doctor_id = setup_test_data()

    try:
        result = book_appointment.invoke({
            "doctor_id": doctor_id,
            "patient_name": "Invalid Date Patient",
            "patient_phone": TEST_PHONE_1,
            "appointment_date": "not-a-date",
        })

        assert "invalid" in result.lower()

    finally:
        cleanup_test_data(doctor_id)


# ============================================================
# TEST 14 — PAST DATE
# ============================================================

def test_past_booking_date():

    doctor_id = setup_test_data()

    try:
        result = book_appointment.invoke({
            "doctor_id": doctor_id,
            "patient_name": "Past Date Patient",
            "patient_phone": TEST_PHONE_1,
            "appointment_date": "2020-01-01",
        })

        assert "past" in result.lower()

    finally:
        cleanup_test_data(doctor_id)


# ============================================================
# TEST 15 — WRONG PHONE CANNOT CANCEL
# ============================================================

def test_wrong_phone_cannot_cancel():

    doctor_id = setup_test_data()

    try:
        result = book_appointment.invoke({
            "doctor_id": doctor_id,
            "patient_name": "Protected Patient",
            "patient_phone": TEST_PHONE_1,
            "appointment_date": TEST_DATE_1,
        })

        appointment_id = int(
            result.split("Appointment ID: ")[1]
            .split("\n")[0]
        )

        cancel_result = cancel_appointment.invoke({
            "appointment_id": appointment_id,
            "patient_phone": "01999999999",
        })

        assert "No appointment was found" in cancel_result

    finally:
        cleanup_test_data(doctor_id)