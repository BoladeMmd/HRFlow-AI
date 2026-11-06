
from calendar import monthrange
from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.employe import Employe
from app.models.regle_conges import RegleConges
from app.models.solde_conges import SoldeConges
from app.models.mouvement_conges import MouvementConges


def attribuer_conges_mensuels(
    db: Session,
    annee: int,
    mois: int,
    employe_ids: list[int] | None = None
):
    # Vérifier le mois
    if mois < 1 or mois > 12:
        raise HTTPException(400, "Le mois doit être compris entre 1 et 12.")

    debut_mois = date(annee, mois, 1)
    dernier_jour = monthrange(annee, mois)[1]
    fin_mois = date(annee, mois, dernier_jour)

    # Empêcher le crédit d'un mois futur
    if fin_mois > date.today():
        raise HTTPException(
            400,
            "L'acquisition ne peut être effectuée qu'après la fin du mois."
        )
    # Récupérer la règle applicable au mois
    regle = db.scalar(
        select(RegleConges)
        .where(
            RegleConges.actif.is_(True),
            RegleConges.date_debut <= debut_mois,
            (RegleConges.date_fin.is_(None)) |
            (RegleConges.date_fin >= debut_mois)
        )
        .order_by(RegleConges.date_debut.desc())
    )

    if regle is None:
        raise HTTPException(
            400,
            "Aucune règle de congés active pour cette période."
        )

    jours_a_attribuer = Decimal(str(regle.jours_par_mois))
    periode = f"{annee}-{mois:02d}"

    # Récupérer les employés actifs déjà embauchés à la fin du mois
    conditions = [
        Employe.statut == "actif",
        Employe.date_embauche <= fin_mois
    ]

    if employe_ids is not None:
        conditions.append(Employe.id.in_(employe_ids))

    employes = db.scalars(
        select(Employe).where(*conditions)
    ).all()

    nombre_attribues = 0
    nombre_ignores = 0

    try:
        for employe in employes:

            # Vérifier si le crédit du mois existe déjà
            mouvement_existant = db.scalar(
                select(MouvementConges).where(
                    MouvementConges.employe_id == employe.id,
                    MouvementConges.periode == periode,
                    MouvementConges.type_mouvement == "acquisition"
                )
            )

            if mouvement_existant:
                nombre_ignores += 1
                continue

            # Récupérer ou créer le solde annuel
            solde = db.scalar(
                select(SoldeConges)
                .where(
                    SoldeConges.employe_id == employe.id,
                    SoldeConges.annee == annee
                )
                .with_for_update()
            )

            if solde is None:
                solde = SoldeConges(
                    employe_id=employe.id,
                    annee=annee,
                    solde_initial=0,
                    jours_acquis=0,
                    jours_pris=0,
                    solde_reporte=0
                )
                db.add(solde)
                db.flush()

            # Mettre à jour le solde
            solde.jours_acquis = (
                Decimal(str(solde.jours_acquis))
                + jours_a_attribuer
            )

            # Enregistrer le mouvement
            mouvement = MouvementConges(
                employe_id=employe.id,
                solde_id=solde.id,
                type_mouvement="acquisition",
                nombre_jours=jours_a_attribuer,
                periode=periode
            )

            db.add(mouvement)
            nombre_attribues += 1

        db.commit()

        return {
            "message": "Traitement mensuel terminé.",
            "periode": periode,
            "jours_attribues_par_employe": str(jours_a_attribuer),
            "employes_credites": nombre_attribues,
            "employes_ignores": nombre_ignores
        }

    except Exception:
        db.rollback()
        raise
