
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.employe import Employe
from app.models.regle_conges import RegleConges
from app.models.solde_conges import SoldeConges


def calculer_mois_acquis(date_embauche: date, annee: int) -> int:
    """Compte les mois complets d'acquisition dans l'année."""

    debut = max(date_embauche, date(annee, 1, 1))
    fin = min(date.today(), date(annee, 12, 31))

    if debut > fin:
        return 0

    mois = (fin.year - debut.year) * 12 + fin.month - debut.month

    # Le mois d'embauche ne compte qu'après un mois complet.
    if fin.day < debut.day:
        mois -= 1

    return max(mois, 0)


def initialiser_solde_employe(
    db: Session,
    employe_id: int,
    annee: int
):
    employe = db.get(Employe, employe_id)

    if employe is None:
        raise ValueError("Employé introuvable.")

    solde_existant = db.scalar(
        select(SoldeConges).where(
            SoldeConges.employe_id == employe_id,
            SoldeConges.annee == annee
        )
    )

    if solde_existant:
        return solde_existant

    regle = db.scalar(
        select(RegleConges).where(
            RegleConges.actif == True,
            RegleConges.date_debut <= date.today()
        ).order_by(RegleConges.date_debut.desc())
    )

    if regle is None:
        raise ValueError("Aucune règle de congés active.")

    if regle.unite_calcul != "ouvrable":
        raise ValueError("Cette version du service prend uniquement en charge les jours ouvrables.")

    mois = calculer_mois_acquis(employe.date_embauche, annee)

    jours_acquis = (
        Decimal(str(regle.jours_par_mois))
        * Decimal(mois)
    )

    solde = SoldeConges(
        employe_id=employe_id,
        annee=annee,
        solde_initial=Decimal("0"),
        jours_acquis=jours_acquis,
        jours_pris=Decimal("0"),
        solde_reporte=Decimal("0")
    )

    db.add(solde)
    db.commit()
    db.refresh(solde)

    return solde
