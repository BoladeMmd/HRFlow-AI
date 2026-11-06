from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class UtilisateurCreate(BaseModel):
    employe_id: int
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=12, max_length=128)
    role: Literal["admin_rh", "responsable", "employe"]


class UtilisateurResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employe_id: int | None
    username: str
    role: str
    actif: bool


class UtilisateurUpdate(BaseModel):
    role: Literal["admin_rh", "responsable", "employe"] | None = None
    actif: bool | None = None

class UtilisateurPasswordReset(BaseModel):
    nouveau_mot_de_passe: str = Field(min_length=12, max_length=128)