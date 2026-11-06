
from pydantic import BaseModel, ConfigDict, Field


class DepartementCreate(BaseModel):
    nom: str = Field(min_length=2, max_length=100)
    description: str | None = None


class DepartementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    description: str | None = None
