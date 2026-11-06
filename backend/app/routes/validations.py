
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.validation import Validation
from app.models.demande_absence import DemandeAbsence
from app.models.utilisateur import Utilisateur
from app.schemas.validation import (
    ValidationCreate,
    ValidationResponse
)
from app.routes.auth import require_roles
from sqlalchemy import select
from app.services.traitement_conges import deduire_conges
from app.services.notifications import notifier_demande_traitee

router = APIRouter(
    prefix="/validations",
    tags=["Validations des demandes"]
)


# 1. Consulter les demandes en attente
@router.get("/demandes-en-attente")
def demandes_en_attente(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(
        require_roles("admin_rh", "responsable")
    )
):
    demandes = db.scalars(
        select(DemandeAbsence)
        .where(DemandeAbsence.statut == "en_attente")
        .order_by(DemandeAbsence.created_at.asc())
    ).all()

    return demandes


# 2. Approuver ou rejeter une demande

@router.post(
    "/{demande_id}",
    response_model=ValidationResponse,
    status_code=201
)
def traiter_demande(
    demande_id: int,
    donnees: ValidationCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(
        require_roles("admin_rh", "responsable")
    )
):
    # Verrouiller la demande pendant son traitement
    demande = db.scalar(
        select(DemandeAbsence)
        .where(DemandeAbsence.id == demande_id)
        .with_for_update()
    )

    if demande is None:
        raise HTTPException(
            status_code=404,
            detail="Demande d'absence introuvable."
        )

    if demande.statut != "en_attente":
        raise HTTPException(
            status_code=400,
            detail="Cette demande a déjà été traitée."
        )

    try:
        # Déduire les congés uniquement en cas d'approbation.
        if donnees.decision == "approuvee":
            deduire_conges(db, demande)

        validation = Validation(
            demande_id=demande.id,
            valideur_id=utilisateur.id,
            decision=donnees.decision,
            commentaire=donnees.commentaire
        )

        demande.statut = donnees.decision

        db.add(validation)
        notifier_demande_traitee(
            db=db,
            employe_id=demande.employe_id,
            decision=donnees.decision,
            commentaire=donnees.commentaire
        )

        # Enregistrer ensemble la décision et la déduction éventuelle.
        db.commit()
        db.refresh(validation)

        return validation

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erreur lors du traitement de la demande."
        )

    return validation
