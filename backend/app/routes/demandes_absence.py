
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.demande_absence import DemandeAbsence
from app.models.employe import Employe
from app.models.type_absence import TypeAbsence
from app.models.utilisateur import Utilisateur

from app.schemas.demande_absence import (
    DemandeAbsenceCreate,
    DemandeAbsenceResponse
)

from app.routes.auth import get_current_user, require_roles
from app.services.notifications import notifier_demande_envoyee


router = APIRouter(
    prefix="/demandes-absence",
    tags=["Demandes d'absence"]
)


def calculer_nombre_jours(date_debut, date_fin, deduit_solde):
    """
    Si la demande déduit le solde annuel :
    compter uniquement les jours du lundi au vendredi.

    Pour les autres types :
    compter les jours calendaires.
    """

    if not deduit_solde:
        return (date_fin - date_debut).days + 1

    nombre = 0
    date_actuelle = date_debut

    while date_actuelle <= date_fin:
        if date_actuelle.weekday() < 5:
            nombre += 1

        date_actuelle += timedelta(days=1)

    return nombre


@router.post(
    "/",
    response_model=DemandeAbsenceResponse,
    status_code=201
)
def creer_demande(
    donnees: DemandeAbsenceCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user)
):
    if utilisateur.employe_id is None:
        raise HTTPException(
            status_code=403,
            detail="Ce compte n'est pas associé à un employé."
        )

    employe = db.get(Employe, utilisateur.employe_id)

    if employe is None or employe.statut != "actif":
        raise HTTPException(
            status_code=403,
            detail="Votre compte employé n'est pas actif."
        )

    if donnees.date_fin < donnees.date_debut:
        raise HTTPException(
            status_code=400,
            detail="La date de fin doit être postérieure ou égale à la date de début."
        )

    type_absence = db.get(
        TypeAbsence,
        donnees.type_absence_id
    )

    if type_absence is None or not type_absence.actif:
        raise HTTPException(
            status_code=404,
            detail="Type d'absence introuvable ou inactif."
        )

    nombre_jours = calculer_nombre_jours(
        donnees.date_debut,
        donnees.date_fin,
        type_absence.deduit_solde_conges
    )

    if nombre_jours <= 0:
        raise HTTPException(
            status_code=400,
            detail="La période sélectionnée ne contient aucun jour ouvrable."
        )

    demande = DemandeAbsence(
        employe_id=employe.id,
        type_absence_id=type_absence.id,
        date_debut=donnees.date_debut,
        date_fin=donnees.date_fin,
        nombre_jours=nombre_jours,
        motif=donnees.motif,
        justificatif_path=None,
        statut="en_attente"
    )

    try:
        db.add(demande)
        db.flush()

        # Créer la notification de confirmation.
        notifier_demande_envoyee(
            db=db,
            employe_id=employe.id
        )

        # Enregistrer la demande et sa notification ensemble.
        db.commit()
        db.refresh(demande)

        return demande

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de l'enregistrement de la demande."
        )


@router.get(
    "/mes-demandes",
    response_model=list[DemandeAbsenceResponse]
)
def lister_mes_demandes(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user)
):
    if utilisateur.employe_id is None:
        raise HTTPException(
            status_code=403,
            detail="Ce compte n'est pas associé à un employé."
        )

    return db.scalars(
        select(DemandeAbsence)
        .where(DemandeAbsence.employe_id == utilisateur.employe_id)
        .order_by(DemandeAbsence.created_at.desc())
    ).all()


@router.get(
    "/",
    response_model=list[DemandeAbsenceResponse]
)
def lister_toutes_les_demandes(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(
        require_roles("admin_rh", "responsable")
    )
):
    return db.scalars(
        select(DemandeAbsence)
        .order_by(DemandeAbsence.created_at.desc())
    ).all()
