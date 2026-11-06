from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ValidationCreate(BaseModel):
    decision: Literal["approuvee", "rejetee"]
    commentaire: str | None = Field(
        default=None,
        max_length=2000
    )


class ValidationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    demande_id: int
    valideur_id: int
    decision: str
    commentaire: str | None
    date_decision: datetime | None