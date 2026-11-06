
from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmployeCreate(BaseModel):
    matricule: str = Field(min_length=2, max_length=30)
    nom: str = Field(min_length=2, max_length=100)
    prenom: str = Field(min_length=2, max_length=100)
    email: EmailStr
    telephone: str | None = None
    date_embauche: date
    departement_id: int | None = None
    poste: str | None = None

from typing import Literal
class EmployeUpdate(BaseModel):
    nom: str | None = Field(default=None, min_length=2, max_length=100)
    prenom: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    telephone: str | None = None
    departement_id: int | None = None
    poste: str | None = None
    statut: Literal["actif", "inactif"] | None = None


class EmployeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    matricule: str
    nom: str
    prenom: str
    email: str
    telephone: str | None
    date_embauche: date
    departement_id: int | None
    poste: str | None
    statut: str
