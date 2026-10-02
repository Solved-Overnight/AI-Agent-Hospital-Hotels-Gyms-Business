from app.database.database import Base, SessionLocal, engine
from app.database.models import Doctor, Appointment, DailyCapacity


# creting the tables in the database using the defined models
def create_tables():
    Base.metadata.create_all(bind=engine)


# add a doctor to the database if it doesn't already exist
def seed_doctors():

    db = SessionLocal()

    try:
        existing_doctor = db.query(Doctor).first()

        if existing_doctor:
            print("Doctor already exists.")
            return

        doctor = Doctor(
            name="Dr. Sarah Ahmed",
            specialization="General Dentistry",
            active=True,
        )

        db.add(doctor)
        db.commit()

        print("Doctor created successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    seed_doctors()