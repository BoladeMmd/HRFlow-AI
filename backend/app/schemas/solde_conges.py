
from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class SoldeCongesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employe_id: int
    annee: int
    solde_initial: Decimal
    jours_acquis: Decimal
    jours_pris: Decimal
    solde_reporte: Decimal


class SoldeCongesDetail(SoldeCongesResponse):
    solde_disponible: Decimal
