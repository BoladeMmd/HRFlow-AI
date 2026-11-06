
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.routes.auth import require_roles
from app.services.report_conges import effectuer_report_conges


router = APIRouter(
    prefix="/report-conges",
    tags=["Report des congés"]
)


@router.post("/executer")
def executer_report(
    annee: int = Query(..., ge=2000, le=2100),
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(
        require_roles("admin_rh")
    )
):
    try:
        resultat = effectuer_report_conges(
            db=db,
            annee=annee
        )

        return resultat

    except ValueError as erreur:
        raise HTTPException(
            status_code=400,
            detail=str(erreur)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Erreur lors du report des congés."
        )
