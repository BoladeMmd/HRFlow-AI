
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date

from app.services.acquisition_conges import attribuer_conges_mensuels

from app.database import get_db
from app.models.employe import Employe
from app.models.departement import Departement
from app.schemas.employe import (
    EmployeCreate,
    EmployeUpdate,
    EmployeResponse
)

router = APIRouter(
    prefix="/employes",
    tags=["Employés"]
)


# Ajouter un employé

# Ajouter un employé
@router.post("/", response_model=EmployeResponse, status_code=201)
def creer_employe(
    donnees: EmployeCreate,
    db: Session = Depends(get_db)
):
    if donnees.departement_id is not None:
        departement = db.get(Departement, donnees.departement_id)
        if departement is None:
            raise HTTPException(
                status_code=404,
                detail="Département introuvable."
            )

    employe = Employe(**donnees.model_dump())
    db.add(employe)

    try:
        db.commit()
        db.refresh(employe)

        # Rattrapage automatique des acquisitions
        if employe.statut == "actif":
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

            while periode < mois_courant:
                attribuer_conges_mensuels(
                    db=db,
                    annee=periode.year,
                    mois=periode.month,
                    employe_ids=[employe.id]
                )

                # Passer au mois suivant
                if periode.month == 12:
                    periode = date(periode.year + 1, 1, 1)
                else:
                    periode = date(
                        periode.year,
                        periode.month + 1,
                        1
                    )

        return employe

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Matricule ou adresse e-mail déjà utilisé."
        )


# Consulter tous les employés
@router.get("/", response_model=list[EmployeResponse])
def lister_employes(db: Session = Depends(get_db)):
    return db.scalars(
        select(Employe).order_by(Employe.nom, Employe.prenom)
    ).all()


# Consulter un employé par son identifiant
@router.get("/{employe_id}", response_model=EmployeResponse)
def consulter_employe(
    employe_id: int,
    db: Session = Depends(get_db)
):
    employe = db.get(Employe, employe_id)

    if employe is None:
        raise HTTPException(
            status_code=404,
            detail="Employé introuvable."
        )

    return employe


# Modifier les informations d'un employé
@router.patch("/{employe_id}", response_model=EmployeResponse)
def modifier_employe(
    employe_id: int,
    donnees: EmployeUpdate,
    db: Session = Depends(get_db)
):
    employe = db.get(Employe, employe_id)

    if employe is None:
        raise HTTPException(
            status_code=404,
            detail="Employé introuvable."
        )

    modifications = donnees.model_dump(exclude_unset=True)

    if "departement_id" in modifications:
        departement_id = modifications["departement_id"]

        if departement_id is not None and db.get(
            Departement, departement_id
        ) is None:
            raise HTTPException(
                status_code=404,
                detail="Département introuvable."
            )

    for champ, valeur in modifications.items():
        setattr(employe, champ, valeur)

    try:
        db.commit()
        db.refresh(employe)
        return employe
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cette adresse e-mail est déjà utilisée."
        )


# Désactiver un employé sans supprimer son historique
@router.patch("/{employe_id}/desactiver")
def desactiver_employe(
    employe_id: int,
    db: Session = Depends(get_db)
):
    employe = db.get(Employe, employe_id)

    if employe is None:
        raise HTTPException(
            status_code=404,
            detail="Employé introuvable."
        )

    employe.statut = "inactif"
    db.commit()

    return {
        "message": "Employé désactivé avec succès.",
        "employe_id": employe.id
    }


# Réactiver un employé sans supprimer son historique
@router.patch("/{employe_id}/reactiver")
def reactiver_employe(
    employe_id: int,
    db: Session = Depends(get_db)
):
    employe = db.get(Employe, employe_id)

    if employe is None:
        raise HTTPException(
            status_code=404,
            detail="Employé introuvable."
        )

    if employe.statut == "actif":
        raise HTTPException(
            status_code=400,
            detail="Cet employé est déjà actif."
        )

    employe.statut = "actif"
    db.commit()

    return {
        "message": "Employé réactivé avec succès.",
        "employe_id": employe.id
    }
