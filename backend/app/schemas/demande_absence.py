from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DemandeAbsenceCreate(BaseModel):
    type_absence_id: int
    date_debut: date
    date_fin: date
    motif: str = Field(min_length=3, max_length=2000)


class DemandeAbsenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employe_id: int
    type_absence_id: int
    date_debut: date
    date_fin: date
    nombre_jours: Decimal
    motif: str | None
    statut: str
    created_at: datetime | None