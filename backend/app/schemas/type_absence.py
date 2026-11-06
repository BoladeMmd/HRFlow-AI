from pydantic import BaseModel, ConfigDict, Field


class TypeAbsenceCreate(BaseModel):
    nom: str = Field(min_length=2, max_length=100)
    description: str | None = None
    deduit_solde_conges: bool = False
    justificatif_obligatoire: bool = False
    validation_obligatoire: bool = True


class TypeAbsenceUpdate(BaseModel):
    nom: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None
    deduit_solde_conges: bool | None = None
    justificatif_obligatoire: bool | None = None
    validation_obligatoire: bool | None = None
    actif: bool | None = None


class TypeAbsenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    description: str | None
    deduit_solde_conges: bool
    justificatif_obligatoire: bool
    validation_obligatoire: bool
    actif: bool