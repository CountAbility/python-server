import datetime

from sqlalchemy.orm import Session
from uuid import uuid4, UUID
from datetime import datetime

import schemas, models


def create_surgery(db: Session, surgery: schemas.SurgicalRecordCreate):
    db_surgery = models.SurgicalRecord(
        id=uuid4(),
        patient_name=surgery.patient_name,
        operation=surgery.operation,
        med_pros=surgery.med_pros,
        time_started=datetime.min,
        time_finished=datetime.max
    )
    db.add(db_surgery)
    db.commit()
    db.refresh(db_surgery)
    return db_surgery


def create_alert(db: Session, alert: schemas.AlertCreate):
    db_alert = models.Alert(
        id=uuid4(),
        surgery_id=alert.surgery_id,
        message=alert.message,
        severity=alert.severity,
        time_started=alert.time_started
    )

    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


def create_med_pro(db: Session, med_pro: schemas.MedProfessionalCreate):
    db_med_pro = models.MedProfessional(
        id=uuid4(),
        name=med_pro.name
    )
    db.add(db_med_pro)
    db.commit()
    db.refresh(db_med_pro)
    return db_med_pro


def get_surgery_alerts(db: Session, surgery_id: UUID):
    return db.query(models.Alert).filter(models.Alert.surgery_id == surgery_id).all()


def get_med_pro_by_id(db: Session, id: UUID):
    return db.query(models.MedProfessional).filter(models.MedProfessional.id == id).first()


def get_med_pro_by_name(db: Session, name: str):
    return db.query(models.MedProfessional).filter(models.MedProfessional.name == name).first()


def get_surgeries(db: Session):
    return db.query(models.SurgicalRecord).all()
