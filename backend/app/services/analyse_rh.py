
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from app.models.demande_absence import DemandeAbsence
from app.models.employe import Employe
from app.models.departement import Departement
from app.models.type_absence import TypeAbsence
from app.models.demande_absence import DemandeAbsence


def analyser_absences_par_departement(db: Session):
    resultats = (
        db.query(
            Departement.nom.label("departement"),
            func.count(DemandeAbsence.id).label("nombre_demandes"),
            func.coalesce(
                func.sum(DemandeAbsence.nombre_jours), 0
            ).label("total_jours")
        )
        .join(Employe, Employe.departement_id == Departement.id)
        .join(DemandeAbsence, DemandeAbsence.employe_id == Employe.id)
        .filter(DemandeAbsence.statut == "approuvee")
        .group_by(Departement.id, Departement.nom)
        .order_by(func.sum(DemandeAbsence.nombre_jours).desc())
        .all()
    )

    return [
        {
            "departement": ligne.departement,
            "nombre_demandes": ligne.nombre_demandes,
            "total_jours": float(ligne.total_jours)
        }
        for ligne in resultats
    ]


def analyser_absences_par_type(db: Session):
    resultats = (
        db.query(
            TypeAbsence.nom.label("type_absence"),
            func.count(DemandeAbsence.id).label("nombre_demandes"),
            func.coalesce(
                func.sum(DemandeAbsence.nombre_jours), 0
            ).label("total_jours")
        )
        .join(
            DemandeAbsence,
            DemandeAbsence.type_absence_id == TypeAbsence.id
        )
        .filter(DemandeAbsence.statut == "approuvee")
        .group_by(TypeAbsence.id, TypeAbsence.nom)
        .order_by(func.count(DemandeAbsence.id).desc())
        .all()
    )

    return [
        {
            "type_absence": ligne.type_absence,
            "nombre_demandes": ligne.nombre_demandes,
            "total_jours": float(ligne.total_jours)
        }
        for ligne in resultats
    ]


def analyser_demandes_par_statut(db: Session):
    resultats = (
        db.query(
            DemandeAbsence.statut,
            func.count(DemandeAbsence.id).label("nombre")
        )
        .group_by(DemandeAbsence.statut)
        .all()
    )

    return [
        {
            "statut": ligne.statut,
            "nombre": ligne.nombre
        }
        for ligne in resultats
    ]


def classer_employes_par_absences(db: Session, limite: int = 10):
    resultats = (
        db.query(
            Employe.id.label("employe_id"),
            Employe.matricule,
            Employe.nom,
            Employe.prenom,
            Departement.nom.label("departement"),
            func.count(DemandeAbsence.id).label("nombre_demandes"),
            func.coalesce(
                func.sum(DemandeAbsence.nombre_jours), 0
            ).label("total_jours")
        )
        .join(
            DemandeAbsence,
            DemandeAbsence.employe_id == Employe.id
        )
        .outerjoin(
            Departement,
            Employe.departement_id == Departement.id
        )
        .filter(DemandeAbsence.statut == "approuvee")
        .group_by(
            Employe.id,
            Employe.matricule,
            Employe.nom,
            Employe.prenom,
            Departement.nom
        )
        .order_by(
            func.sum(DemandeAbsence.nombre_jours).desc()
        )
        .limit(limite)
        .all()
    )

    return [
        {
            "employe_id": ligne.employe_id,
            "matricule": ligne.matricule,
            "nom_complet": f"{ligne.prenom} {ligne.nom}",
            "departement": ligne.departement or "Non renseigné",
            "nombre_demandes": ligne.nombre_demandes,
            "total_jours": float(ligne.total_jours)
        }
        for ligne in resultats
    ]





def analyser_evolution_mensuelle(db, annee=None, statut=None):
    """
    Analyse l'évolution mensuelle du nombre de demandes
    selon la date de début de l'absence.
    """

    from sqlalchemy import func, extract
    from app.models.demande_absence import DemandeAbsence

    mois_expression = func.date_trunc(
        "month",
        DemandeAbsence.date_debut
    )

    requete = (
        db.query(
            mois_expression.label("mois"),
            func.count(DemandeAbsence.id).label("nombre_demandes")
        )
        .filter(DemandeAbsence.date_debut.isnot(None))
    )

    if annee is not None:
        requete = requete.filter(
            extract("year", DemandeAbsence.date_debut) == annee
        )

    if statut is not None and statut.lower() != "tous":
        requete = requete.filter(
            DemandeAbsence.statut == statut
        )

    resultats = (
        requete
        .group_by(mois_expression)
        .order_by(mois_expression)
        .all()
    )

    return [
        {
            "mois": resultat.mois.strftime("%Y-%m"),
            "nombre_demandes": resultat.nombre_demandes
        }
        for resultat in resultats
    ]

