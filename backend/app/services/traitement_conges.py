
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.demande_absence import DemandeAbsence
from app.models.type_absence import TypeAbsence
from app.models.solde_conges import SoldeConges
from app.models.mouvement_conges import MouvementConges


def deduire_conges(
    db: Session,
    demande: DemandeAbsence
):
    """
    Vérifie le solde et prépare la déduction
    sans effectuer de commit.
    """

    type_absence = db.get(
        TypeAbsence,
        demande.type_absence_id
    )

    if type_absence is None:
        raise HTTPException(
            status_code=404,
            detail="Type d'absence introuvable."
        )

    # Certaines absences ne déduisent pas les congés annuels.
    if not type_absence.deduit_solde_conges:
        return None

    # Première version : une demande doit rester dans la même année.
    annee = demande.date_debut.year

    if demande.date_fin.year != annee:
        raise HTTPException(
            status_code=400,
            detail="Les demandes de congés couvrant plusieurs années ne sont pas encore prises en charge."
        )

    # Vérifier qu'aucune déduction n'a déjà été enregistrée.
    mouvement_existant = db.scalar(
        select(MouvementConges).where(
            MouvementConges.demande_id == demande.id,
            MouvementConges.type_mouvement == "consommation"
        )
    )

    if mouvement_existant is not None:
        raise HTTPException(
            status_code=400,
            detail="La déduction de cette demande a déjà été enregistrée."
        )

    # Récupérer le solde annuel de l'employé.
    solde = db.scalar(
        select(SoldeConges)
        .where(
            SoldeConges.employe_id == demande.employe_id,
            SoldeConges.annee == annee
        )
        .with_for_update()
    )

    if solde is None:
        raise HTTPException(
            status_code=400,
            detail="Aucun solde de congés n'est initialisé pour cet employé et cette année."
        )

    jours_demandes = Decimal(str(demande.nombre_jours))

    solde_disponible = (
        Decimal(str(solde.solde_initial))
        + Decimal(str(solde.jours_acquis))
        + Decimal(str(solde.solde_reporte))
        - Decimal(str(solde.jours_pris))
    )

    if jours_demandes > solde_disponible:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Solde insuffisant. Disponible : "
                f"{solde_disponible} jours ; "
                f"demandés : {jours_demandes} jours."
            )
        )

    # Mettre à jour le nombre de jours consommés.
    solde.jours_pris = (
        Decimal(str(solde.jours_pris))
        + jours_demandes
    )

    # Enregistrer le mouvement pour assurer la traçabilité.
    mouvement = MouvementConges(
        employe_id=demande.employe_id,
        solde_id=solde.id,
        type_mouvement="consommation",
        nombre_jours=jours_demandes,
        periode=demande.date_debut.strftime("%Y-%m"),
        demande_id=demande.id
    )

    db.add(mouvement)

    return mouvement
