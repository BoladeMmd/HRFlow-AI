from datetime import date
from fastapi import HTTPException
from app.models.employe import Employe
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.routes.auth import get_current_user, require_roles
from app.services.acquisition_conges import attribuer_conges_mensuels

router = APIRouter(
    prefix="/acquisition-conges",
    tags=["Acquisition des congés"]
)


@router.post("/executer")
def executer_acquisition(
    annee: int,
    mois: int,
    db: Session = Depends(get_db),
    utilisateur=Depends(require_roles("admin_rh"))
):
    return attribuer_conges_mensuels(
        db=db,
        annee=annee,
        mois=mois
    )

@router.post("/initialiser-employes-demo")
def initialiser_employes_demo(
    db: Session = Depends(get_db),
    utilisateur=Depends(require_roles("admin_rh"))
):
    employe_ids = [4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17]

    resultats = []

    for mois in range(1, 11):
        resultat = attribuer_conges_mensuels(
            db=db,
            annee=2026,
            mois=mois,
            employe_ids=employe_ids
        )
        resultats.append(resultat)

    return {
        "message": "Initialisation des soldes terminée.",
        "traitements": resultats
    }


@router.post("/rattraper/{employe_id}")
def rattraper_acquisitions_employe(
    employe_id: int,
    db: Session = Depends(get_db),
    utilisateur=Depends(require_roles("admin_rh"))
):
    employe = db.get(Employe, employe_id)

    if employe is None:
        raise HTTPException(
            status_code=404,
            detail="Employé introuvable."
        )

    if employe.statut != "actif":
        raise HTTPException(
            status_code=400,
            detail="L'employé doit être actif."
        )

    aujourd_hui = date.today()

    debut_periode = date(
        employe.date_embauche.year,
        employe.date_embauche.month,
        1
    )

    mois_courant = date(
        aujourd_hui.year,
        aujourd_hui.month,
        1
    )

    periode = debut_periode
    resultats = []

    while periode < mois_courant:
        resultat = attribuer_conges_mensuels(
            db=db,
            annee=periode.year,
            mois=periode.month,
            employe_ids=[employe.id]
        )

        resultats.append(resultat)

        if periode.month == 12:
            periode = date(periode.year + 1, 1, 1)
        else:
            periode = date(
                periode.year,
                periode.month + 1,
                1
            )

    return {
        "message": "Rattrapage des acquisitions terminé.",
        "employe_id": employe.id,
        "employe": f"{employe.prenom} {employe.nom}",
        "traitements": resultats
    }
