
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.solde_conges import SoldeConges
from app.models.mouvement_conges import MouvementConges


def effectuer_report_conges(db: Session, annee: int):
    """
    Report intégral des congés annuels non utilisés
    de l'année indiquée vers l'année suivante.

    Exemple : annee=2026 reporte les soldes vers 2027.
    """

    if annee < 2000:
        raise ValueError("Année invalide.")

    periode_origine = f"{annee}-12"
    annee_suivante = annee + 1

    employes_rapportes = 0
    jours_total_reportes = Decimal("0.00")
    employes_ignores = 0

    try:
        # Récupérer et verrouiller les soldes de l'année d'origine.
        soldes_sources = db.scalars(
            select(SoldeConges)
            .where(SoldeConges.annee == annee)
            .order_by(SoldeConges.employe_id)
            .with_for_update()
        ).all()

        for solde_source in soldes_sources:

            # Vérifier si le report a déjà été effectué.
            report_existant = db.scalar(
                select(MouvementConges.id).where(
                    MouvementConges.employe_id == solde_source.employe_id,
                    MouvementConges.type_mouvement == "report",
                    MouvementConges.periode == periode_origine
                ).limit(1)
            )

            if report_existant is not None:
                employes_ignores += 1
                continue

            # Calculer le solde disponible à reporter.
            jours_disponibles = Decimal(
                str(solde_source.solde_disponible)
            ).quantize(Decimal("0.01"))

            if jours_disponibles <= 0:
                employes_ignores += 1
                continue

            # Rechercher le solde de l'année suivante.
            solde_destination = db.scalar(
                select(SoldeConges)
                .where(
                    SoldeConges.employe_id == solde_source.employe_id,
                    SoldeConges.annee == annee_suivante
                )
                .with_for_update()
            )

            # Créer le solde annuel s'il n'existe pas.
            if solde_destination is None:
                solde_destination = SoldeConges(
                    employe_id=solde_source.employe_id,
                    annee=annee_suivante,
                    solde_initial=Decimal("0.00"),
                    jours_acquis=Decimal("0.00"),
                    jours_pris=Decimal("0.00"),
                    solde_reporte=Decimal("0.00")
                )

                db.add(solde_destination)
                db.flush()

            # Ajouter les jours reportés au solde destination.
            solde_destination.solde_reporte = (
                Decimal(str(solde_destination.solde_reporte))
                + jours_disponibles
            )

            # Tracer le mouvement de report.
            mouvement = MouvementConges(
                employe_id=solde_source.employe_id,
                solde_id=solde_destination.id,
                type_mouvement="report",
                nombre_jours=jours_disponibles,
                periode=periode_origine,
                demande_id=None
            )

            db.add(mouvement)

            employes_rapportes += 1
            jours_total_reportes += jours_disponibles

        db.commit()

        return {
            "message": "Report des congés terminé.",
            "annee_origine": annee,
            "annee_destination": annee_suivante,
            "employes_rapportes": employes_rapportes,
            "employes_ignores": employes_ignores,
            "jours_total_reportes": str(jours_total_reportes)
        }

    except Exception:
        db.rollback()
        raise
