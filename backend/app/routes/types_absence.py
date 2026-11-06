from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.type_absence import TypeAbsence
from app.models.utilisateur import Utilisateur
from app.schemas.type_absence import (
    TypeAbsenceCreate,
    TypeAbsenceUpdate,
    TypeAbsenceResponse
)
from app.routes.auth import get_current_user, require_roles


router = APIRouter(
    prefix="/types-absence",
    tags=["Types d'absence"]
)


# Consulter les types d'absence actifs
@router.get("/", response_model=list[TypeAbsenceResponse])
def lister_types_absence(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_current_user)
):
    return db.scalars(
        select(TypeAbsence)
        .where(TypeAbsence.actif == True)
        .order_by(TypeAbsence.nom)
    ).all()


# Créer un type d'absence
@router.post("/", response_model=TypeAbsenceResponse, status_code=201)
def creer_type_absence(
    donnees: TypeAbsenceCreate,
    db: Session = Depends(get_db),
    admin: Utilisateur = Depends(require_roles("admin_rh"))
):
    type_existant = db.scalar(
        select(TypeAbsence).where(
            TypeAbsence.nom == donnees.nom
        )
    )

    if type_existant:
        raise HTTPException(
            status_code=409,
            detail="Ce type d'absence existe déjà."
        )

    nouveau_type = TypeAbsence(**donnees.model_dump())

    db.add(nouveau_type)

    try:
        db.commit()
        db.refresh(nouveau_type)
        return nouveau_type

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Impossible de créer ce type d'absence."
        )


# Modifier un type d'absence
@router.patch("/{type_id}", response_model=TypeAbsenceResponse)
def modifier_type_absence(
    type_id: int,
    donnees: TypeAbsenceUpdate,
    db: Session = Depends(get_db),
    admin: Utilisateur = Depends(require_roles("admin_rh"))
):
    type_absence = db.get(TypeAbsence, type_id)

    if type_absence is None:
        raise HTTPException(
            status_code=404,
            detail="Type d'absence introuvable."
        )

    modifications = donnees.model_dump(exclude_unset=True)

    for champ, valeur in modifications.items():
        setattr(type_absence, champ, valeur)

    try:
        db.commit()
        db.refresh(type_absence)
        return type_absence

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ce nom de type d'absence est déjà utilisé."
        )