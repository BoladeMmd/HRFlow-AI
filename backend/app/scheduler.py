
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import text

from app.database import SessionLocal
from app.services.acquisition_conges import attribuer_conges_mensuels
from app.services.report_conges import effectuer_report_conges


logger = logging.getLogger(__name__)

DAKAR_TZ = ZoneInfo("Africa/Dakar")
scheduler = BackgroundScheduler(timezone=DAKAR_TZ)


def enregistrer_historique(db, action, description):
    """Enregistre une action automatique dans historique_actions."""
    db.execute(
        text("""
            INSERT INTO historique_actions
                (utilisateur_id, action, description, date_action)
            VALUES
                (NULL, :action, :description, :date_action)
        """),
        {
            "action": action,
            "description": description,
            "date_action": datetime.now(DAKAR_TZ).replace(tzinfo=None)
        }
    )
    db.commit()


def executer_acquisition_automatique():
    maintenant = datetime.now(DAKAR_TZ)

    # Traitement du mois précédent
    if maintenant.month == 1:
        annee = maintenant.year - 1
        mois = 12
    else:
        annee = maintenant.year
        mois = maintenant.month - 1

    periode = f"{annee}-{mois:02d}"
    db = SessionLocal()

    try:
        resultat = attribuer_conges_mensuels(
            db=db,
            annee=annee,
            mois=mois
        )

        description = (
            f"Acquisition automatique des congés pour {periode}. "
            f"Employés crédités : {resultat.get('employes_credites', 0)}. "
            f"Employés ignorés : {resultat.get('employes_ignores', 0)}."
        )

        enregistrer_historique(
            db,
            "ACQUISITION_CONGES_AUTOMATIQUE",
            description
        )

        logger.info(description)

    except Exception as erreur:
        db.rollback()

        description = (
            f"Échec de l'acquisition automatique des congés "
            f"pour {periode}. Erreur : {str(erreur)[:500]}"
        )

        logger.exception(description)

        try:
            enregistrer_historique(
                db,
                "ECHEC_ACQUISITION_CONGES",
                description
            )
        except Exception:
            db.rollback()
            logger.exception("Impossible d'enregistrer l'échec dans l'historique.")

    finally:
        db.close()




def executer_report_automatique():
    maintenant = datetime.now(DAKAR_TZ)

    # Le report annuel s'exécute uniquement en janvier.
    if maintenant.month != 1:
        return

    annee_origine = maintenant.year - 1
    db = SessionLocal()

    try:
        resultat = effectuer_report_conges(
            db=db,
            annee=annee_origine
        )

        description = (
            f"Report automatique des congés de {annee_origine} "
            f"vers {annee_origine + 1}. "
            f"Employés reportés : {resultat['employes_rapportes']}. "
            f"Employés ignorés : {resultat['employes_ignores']}. "
            f"Total reporté : {resultat['jours_total_reportes']} jours."
        )

        enregistrer_historique(
            db,
            "REPORT_CONGES_AUTOMATIQUE",
            description
        )

        logger.info(description)

    except Exception as erreur:
        db.rollback()

        description = (
            f"Échec du report automatique des congés "
            f"pour l'année {annee_origine}. "
            f"Erreur : {str(erreur)[:500]}"
        )

        logger.exception(description)

        try:
            enregistrer_historique(
                db,
                "ECHEC_REPORT_CONGES",
                description
            )
        except Exception:
            db.rollback()
            logger.exception(
                "Impossible d'enregistrer l'échec du report."
            )

    finally:
        db.close()



def demarrer_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            executer_acquisition_automatique,
            trigger="cron",
            day=1,
            hour=2,
            minute=0,
            id="acquisition_mensuelle",
            replace_existing=True,
            max_instances=1
        )
        scheduler.add_job(
            executer_report_automatique,
            trigger="cron",
            month=1,
            day=1,
            hour=2,
            minute=0,
            id="report_annuel_conges",
            replace_existing=True,
            max_instances=1
        )

        scheduler.start()
        logger.info("Planificateur HRFlow AI démarré.")


def arreter_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Planificateur HRFlow AI arrêté.")
