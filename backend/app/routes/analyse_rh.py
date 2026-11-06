
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.routes.auth import require_roles

from app.services.analyse_rh import (
    analyser_absences_par_departement,
    analyser_absences_par_type,
    analyser_demandes_par_statut,
    classer_employes_par_absences,
    analyser_evolution_mensuelle
)

router = APIRouter(
    prefix="/analyse-rh",
    tags=["Analyse RH"]
)


@router.get("/departements")
def absences_par_departement(
    db: Session = Depends(get_db),
    utilisateur=Depends(require_roles("responsable"))
):
    return analyser_absences_par_departement(db)


@router.get("/types")
def absences_par_type(
    db: Session = Depends(get_db),
    utilisateur=Depends(require_roles("responsable"))
):
    return analyser_absences_par_type(db)


@router.get("/statuts")
def demandes_par_statut(
    db: Session = Depends(get_db),
    utilisateur=Depends(require_roles("responsable"))
):
    return analyser_demandes_par_statut(db)


@router.get("/employes")
def classement_employes(
    limite: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    utilisateur=Depends(require_roles("responsable"))
):
    return classer_employes_par_absences(db, limite)

@router.get("/evolution-mensuelle")
def evolution_mensuelle(
    annee: int | None = Query(default=None, ge=2000, le=2100),
    statut: str | None = Query(default="tous"),
    db: Session = Depends(get_db),
    utilisateur=Depends(require_roles("responsable"))
):
    return analyser_evolution_mensuelle(
        db,
        annee=annee,
        statut=statut
    )
