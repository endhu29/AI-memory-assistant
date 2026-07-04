from datetime import datetime, date
from sqlalchemy import (Column, Integer, String, Boolean, DateTime,
                        Date, Float, Text, ForeignKey)
from sqlalchemy.orm import relationship
from app.database import Base


# ── 1. USER ──────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(80),  unique=True, nullable=False, index=True)
    email         = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime, default=datetime.utcnow)
    last_login    = Column(DateTime, nullable=True)

    profile      = relationship("Profile",     back_populates="user", uselist=False, cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="user", cascade="all, delete-orphan")
    medicines    = relationship("Medicine",    back_populates="user", cascade="all, delete-orphan")
    health_logs  = relationship("HealthLog",   back_populates="user", cascade="all, delete-orphan")
    alert_logs   = relationship("AlertLog",    back_populates="user", cascade="all, delete-orphan")
    dose_logs    = relationship("DoseLog",     back_populates="user", cascade="all, delete-orphan")


# ── 2. PROFILE ────────────────────────────────────────────────────────
class Profile(Base):
    __tablename__ = "profiles"

    id                      = Column(Integer, primary_key=True, index=True)
    user_id                 = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name               = Column(String(120), nullable=False)
    date_of_birth           = Column(Date,        nullable=False)
    gender                  = Column(String(10),  nullable=False)
    blood_group             = Column(String(5),   nullable=True)
    phone                   = Column(String(15),  nullable=True)
    address                 = Column(Text,         nullable=True)
    known_conditions        = Column(Text,         nullable=True)
    allergies               = Column(Text,         nullable=True)
    primary_doctor_name     = Column(String(120),  nullable=True)
    primary_doctor_phone    = Column(String(15),   nullable=True)
    guardian_name           = Column(String(120),  nullable=False)
    guardian_relationship   = Column(String(60),   nullable=True)
    guardian_phone          = Column(String(15),   nullable=True)
    guardian_email          = Column(String(120),  nullable=False)
    emergency_contact_name  = Column(String(120),  nullable=True)
    emergency_contact_phone = Column(String(15),   nullable=True)
    photo_path              = Column(String(256),  nullable=True)
    updated_at              = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")

    @property
    def age(self):
        today = date.today()
        dob   = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


# ── 3. APPOINTMENT ────────────────────────────────────────────────────
class Appointment(Base):
    __tablename__ = "appointments"

    id                  = Column(Integer, primary_key=True, index=True)
    user_id             = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_name         = Column(String(120), nullable=False)
    speciality          = Column(String(80),  nullable=True)
    appointment_dt      = Column(DateTime,    nullable=False)
    hospital            = Column(String(120), nullable=True)
    notes               = Column(Text,        nullable=True)
    status              = Column(String(20),  default="Scheduled")
    send_reminder_email = Column(Boolean,     default=False)
    reminder_sent       = Column(Boolean,     default=False)
    created_at          = Column(DateTime,    default=datetime.utcnow)
    updated_at          = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="appointments")


# ── 4. MEDICINE ───────────────────────────────────────────────────────
class Medicine(Base):
    __tablename__ = "medicines"

    id                   = Column(Integer, primary_key=True, index=True)
    user_id              = Column(Integer, ForeignKey("users.id"), nullable=False)
    name                 = Column(String(120), nullable=False)
    dosage               = Column(String(60),  nullable=False)
    frequency            = Column(String(30),  nullable=False)
    intake_times         = Column(Text,        nullable=False)   # JSON: ["08:00","20:00"]
    start_date           = Column(Date,        nullable=False)
    end_date             = Column(Date,        nullable=True)
    with_food            = Column(String(10),  default="either")
    special_instructions = Column(Text,        nullable=True)
    alert_on_miss        = Column(Boolean,     default=True)
    is_active            = Column(Boolean,     default=True)
    created_at           = Column(DateTime,    default=datetime.utcnow)

    user      = relationship("User",    back_populates="medicines")
    dose_logs = relationship("DoseLog", back_populates="medicine", cascade="all, delete-orphan")


# ── 5. DOSE LOG ───────────────────────────────────────────────────────
class DoseLog(Base):
    __tablename__ = "dose_logs"

    id           = Column(Integer, primary_key=True, index=True)
    medicine_id  = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    user_id      = Column(Integer, ForeignKey("users.id"),     nullable=False)
    scheduled_dt = Column(DateTime, nullable=False)
    taken_at     = Column(DateTime, nullable=True)
    status       = Column(String(20), default="pending")   # pending/taken/missed
    notes        = Column(Text,       nullable=True)
    alert_sent   = Column(Boolean,    default=False)

    medicine = relationship("Medicine", back_populates="dose_logs")
    user     = relationship("User",     back_populates="dose_logs")


# ── 6. HEALTH LOG ─────────────────────────────────────────────────────
class HealthLog(Base):
    __tablename__ = "health_logs"

    id                = Column(Integer, primary_key=True, index=True)
    user_id           = Column(Integer, ForeignKey("users.id"), nullable=False)
    log_date          = Column(Date,    nullable=False)
    weight_kg         = Column(Float,   nullable=True)
    bp_systolic       = Column(Integer, nullable=True)
    bp_diastolic      = Column(Integer, nullable=True)
    blood_sugar_mgdl  = Column(Integer, nullable=True)
    heart_rate_bpm    = Column(Integer, nullable=True)
    spo2_pct          = Column(Integer, nullable=True)
    temperature_c     = Column(Float,   nullable=True)
    health_feeling    = Column(Integer, nullable=True)   # 1-5
    notes             = Column(Text,    nullable=True)
    alert_sent        = Column(Boolean, default=False)
    created_at        = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="health_logs")


# ── 7. ALERT LOG ──────────────────────────────────────────────────────
class AlertLog(Base):
    __tablename__ = "alert_logs"

    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    alert_type    = Column(String(40),  nullable=False)
    message       = Column(Text,        nullable=False)
    sent_to_email = Column(String(120), nullable=False)
    status        = Column(String(10),  nullable=False)   # sent/failed
    error_detail  = Column(Text,        nullable=True)
    created_at    = Column(DateTime,    default=datetime.utcnow)

    user = relationship("User", back_populates="alert_logs")