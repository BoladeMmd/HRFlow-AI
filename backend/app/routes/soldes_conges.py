
from sqlalchemy import select
from app.schemas.solde_conges import SoldeCongesDetail
from app.models.employe import Employe
from app.routes.auth import get_current_user, require_roles
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.solde_conges import SoldeConges
from app.models.utilisateur import Utilisateur
from app.routes.auth import require_roles

router = APIRouter(
    prefix="/soldes-conges",
    tags=["Soldes de congés"]
)

# 1. Consulter son propre solde
@router.get("/mon-solde", response_model=list[SoldeCongesDetail])
def consulter_mon_solde(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user)
):
    if utilisateur.employe_id is None:
        raise HTTPException(
            status_code=403,
            detail="Ce compte n'est pas associé à un employé."
        )

    soldes = db.scalars(
        select(SoldeConges)
        .where(SoldeConges.employe_id == utilisateur.employe_id)
        .order_by(SoldeConges.annee.desc())
    ).all()

    return [
        {
            "id": solde.id,
            "employe_id": solde.employe_id,
            "annee": solde.annee,
            "solde_initial": solde.solde_initial,
            "jours_acquis": solde.jours_acquis,
            "jours_pris": solde.jours_pris,
            "solde_reporte": solde.solde_reporte,
            "solde_disponible": solde.solde_disponible
        }
        for solde in soldes
    ]


# 2. Consulter tous les soldes (administrateur RH)
@router.get("/", response_model=list[SoldeCongesDetail])
def consulter_tous_les_soldes(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(
        require_roles("admin_rh")
    )
):
    soldes = db.scalars(
        select(SoldeConges)
        .order_by(SoldeConges.annee.desc())
    ).all()

    return [
        {
            "id": solde.id,
            "employe_id": solde.employe_id,
            "annee": solde.annee,
            "solde_initial": solde.solde_initial,
            "jours_acquis": solde.jours_acquis,
            "jours_pris": solde.jours_pris,
            "solde_reporte": solde.solde_reporte,
            "solde_disponible": solde.solde_disponible
        }
        for solde in soldes
    ]
