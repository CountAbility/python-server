from uuid import UUID
from pydantic import BaseModel
from datetime import datetime


class SurgicalRecordBase(BaseModel):
    patient_name: str
    operation: str
    med_pros: str

class SurgicalRecordCreate(SurgicalRecordBase):
    pass


class SurgicalRecord(SurgicalRecordBase):
    id: UUID
    time_started: datetime
    time_finished: datetime
    class Config:
        orm_mode = True


class AlertBase(BaseModel):
    surgery_id: UUID
    message: str
    severity: int
    time_started: datetime


class AlertCreate(AlertBase):
    pass


class Alert(AlertBase):
    overridden: bool
    resolved: bool
    time_resolved: datetime
    id: UUID

    class Config:
        orm_mode = True


class MedProfessionalBase(BaseModel):
    name: str


class MedProfessionalCreate(MedProfessionalBase):
    pass


class MedProfessional(MedProfessionalBase):
    id: UUID

    class Config:
        orm_mode = True

