
from langchain_core.tools import tool

from app.database import SessionLocal
from app.services.analyse_rh import (
    analyser_absences_par_departement,
    analyser_absences_par_type,
    analyser_demandes_par_statut,
    classer_employes_par_absences as classer_employes_sql,
    analyser_evolution_mensuelle as analyser_evolution_sql,
)


def executer_analyse(fonction, *args, **kwargs):
    """Ouvre une session, exécute une analyse et ferme la session."""
    db = SessionLocal()
    try:
        return fonction(db, *args, **kwargs)
    finally:
        db.close()


@tool
def analyser_par_departement() -> list:
    """Analyse les demandes d'absence approuvées par département.
    Retourne le nombre de demandes et le total de jours d'absence.
    """
    return executer_analyse(analyser_absences_par_departement)


@tool
def analyser_par_type() -> list:
    """Analyse les absences approuvées par type d'absence.
    Retourne le nombre de demandes et le total de jours.
    """
    return executer_analyse(analyser_absences_par_type)


@tool
def analyser_par_statut() -> list:
    """Compte les demandes d'absence selon leur statut :
    en attente, approuvées ou rejetées.
    """
    return executer_analyse(analyser_demandes_par_statut)


@tool
def classer_employes_par_absences(limite: int = 10) -> list:
    """Classe les employés selon le nombre de jours d'absence approuvés.
    Le paramètre limite détermine le nombre d'employés à retourner.
    """
    if not 1 <= limite <= 50:
        return [{"erreur": "La limite doit être comprise entre 1 et 50."}]

    return executer_analyse(
        classer_employes_sql,
        limite=limite
    )

# Liste des outils accessibles à l'agent
outils_rh = [
    analyser_par_departement,
    analyser_par_type,
    analyser_par_statut,
    classer_employes_par_absences,
]


@tool
def analyser_evolution_mensuelle_rh(
    annee: int | None = None,
    statut: str = "tous"
) -> list:
    """Analyse l'évolution mensuelle du nombre de demandes d'absence
    selon leur date de début.

    Paramètres :
    - annee : année à analyser. Si aucune année n'est fournie,
      toutes les années sont prises en compte.
    - statut : statut des demandes à analyser.
      Utiliser 'tous' pour inclure tous les statuts.
    """
    return executer_analyse(
        analyser_evolution_sql,
        annee=annee,
        statut=statut
    )

outils_rh = [
    analyser_par_departement,
    analyser_par_type,
    analyser_par_statut,
    classer_employes_par_absences,
    analyser_evolution_mensuelle_rh,
]
