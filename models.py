from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Uuid, DateTime
from sqlalchemy.orm import relationship

from database import Base


class SurgicalRecord(Base):
    __tablename__ = "surgical_records"

    id = Column(Uuid, primary_key=True, index=True)
    patient_name = Column(String, index=True)
    operation = Column(String)
    time_started = Column(DateTime)
    time_finished = Column(DateTime)
    med_pros = Column(String)

    alerts = relationship("Alert", back_populates="surgery")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Uuid, primary_key=True, index=True)
    surgery_id = Column(Uuid, ForeignKey("surgical_records.id"))
    message = Column(String)
    severity = Column(Integer)
    time_started = Column(DateTime)
    time_resolved = Column(DateTime)
    overridden = Column(Boolean)
    resolved = Column(Boolean)

    surgery = relationship("SurgicalRecord", back_populates="alerts")


class MedProfessional(Base):
    __tablename__ = "med_pros"

    id = Column(Uuid, primary_key=True, index=True)
    name = Column(String, index=True)


