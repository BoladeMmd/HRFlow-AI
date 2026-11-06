
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.employe import Employe

from app.database import get_db
from app.models.departement import Departement
from app.schemas.departement import (
    DepartementCreate,
    DepartementResponse
)

router = APIRouter(
    prefix="/departements",
    tags=["Départements"]
)


@router.get("/", response_model=list[DepartementResponse])
def lister_departements(db: Session = Depends(get_db)):
    return db.scalars(
        select(Departement).order_by(Departement.nom)
    ).all()


@router.post("/", response_model=DepartementResponse, status_code=201)
def creer_departement(
    donnees: DepartementCreate,
    db: Session = Depends(get_db)
):
    departement = Departement(
        nom=donnees.nom.strip(),
        description=donnees.description
    )

    db.add(departement)

    try:
        db.commit()
        db.refresh(departement)
        return departement
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ce département existe déjà."
        )

# Modifier un département
@router.patch("/{departement_id}")
def modifier_departement(
    departement_id: int,
    departement: DepartementCreate,
    db: Session = Depends(get_db)
):
    departement_db = db.get(Departement, departement_id)

    if departement_db is None:
        raise HTTPException(
            status_code=404,
            detail="Département introuvable."
        )

    departement_db.nom = departement.nom
    departement_db.description = departement.description

    db.commit()
    db.refresh(departement_db)

    return {
        "message": "Département modifié avec succès.",
        "departement": departement_db
    }

# Supprimer un département
@router.delete("/{departement_id}")
def supprimer_departement(
    departement_id: int,
    db: Session = Depends(get_db)
):
    departement = db.get(Departement, departement_id)

    if departement is None:
        raise HTTPException(
            status_code=404,
            detail="Département introuvable."
        )

    employes = db.query(Employe).filter(
        Employe.departement_id == departement_id
    ).count()

    if employes > 0:
        raise HTTPException(
            status_code=400,
            detail="Impossible de supprimer ce département : des employés y sont encore rattachés."
        )

    db.delete(departement)
    db.commit()

    return {
        "message": "Département supprimé avec succès."
    }