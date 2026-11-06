from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.models.employe import Employe
from app.schemas.utilisateur import (
    UtilisateurCreate,
    UtilisateurResponse,
    UtilisateurUpdate
)
from app.security import hash_password
from app.routes.auth import require_roles
from app.schemas.utilisateur import UtilisateurPasswordReset
from app.security import hash_password


router = APIRouter(
    prefix="/utilisateurs",
    tags=["Gestion des utilisateurs"]
)


@router.post("/", response_model=UtilisateurResponse, status_code=201)
def creer_utilisateur(
    donnees: UtilisateurCreate,
    db: Session = Depends(get_db),
    admin: Utilisateur = Depends(require_roles("admin_rh"))
):
    employe = db.get(Employe, donnees.employe_id)

    if employe is None:
        raise HTTPException(
            status_code=404,
            detail="Employé introuvable."
        )

    if employe.statut != "actif":
        raise HTTPException(
            status_code=400,
            detail="Impossible de créer un compte pour un employé inactif."
        )

    compte_existant = db.scalar(
        select(Utilisateur).where(
            (Utilisateur.employe_id == donnees.employe_id)
            | (Utilisateur.username == donnees.username)
        )
    )

    if compte_existant:
        raise HTTPException(
            status_code=409,
            detail="Cet employé possède déjà un compte ou ce nom d'utilisateur existe."
        )

    utilisateur = Utilisateur(
        employe_id=donnees.employe_id,
        username=donnees.username,
        password_hash=hash_password(donnees.password),
        role=donnees.role,
        actif=True
    )

    db.add(utilisateur)

    try:
        db.commit()
        db.refresh(utilisateur)
        return utilisateur

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Impossible de créer ce compte : données déjà utilisées."
        )


@router.get("/", response_model=list[UtilisateurResponse])
def lister_utilisateurs(
    db: Session = Depends(get_db),
    admin: Utilisateur = Depends(require_roles("admin_rh"))
):
    return db.scalars(
        select(Utilisateur).order_by(Utilisateur.id)
    ).all()


@router.get("/{utilisateur_id}", response_model=UtilisateurResponse)
def consulter_utilisateur(
    utilisateur_id: int,
    db: Session = Depends(get_db),
    admin: Utilisateur = Depends(require_roles("admin_rh"))
):
    utilisateur = db.get(Utilisateur, utilisateur_id)

    if utilisateur is None:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable."
        )

    return utilisateur


@router.patch("/{utilisateur_id}", response_model=UtilisateurResponse)
def modifier_utilisateur(
    utilisateur_id: int,
    donnees: UtilisateurUpdate,
    db: Session = Depends(get_db),
    admin: Utilisateur = Depends(require_roles("admin_rh"))
):
    utilisateur = db.get(Utilisateur, utilisateur_id)

    if utilisateur is None:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable."
        )

    modifications = donnees.model_dump(exclude_unset=True)

    if (
        utilisateur.id == admin.id
        and modifications.get("actif") is False
    ):
        raise HTTPException(
            status_code=400,
            detail="Vous ne pouvez pas désactiver votre propre compte."
        )

    for champ, valeur in modifications.items():
        setattr(utilisateur, champ, valeur)

    db.commit()
    db.refresh(utilisateur)

    return utilisateur


@router.patch("/{utilisateur_id}/reinitialiser-mot-de-passe")
def reinitialiser_mot_de_passe(
    utilisateur_id: int,
    donnees: UtilisateurPasswordReset,
    db: Session = Depends(get_db),
    utilisateur_admin: Utilisateur = Depends(require_roles("admin_rh"))
):
    compte = db.get(Utilisateur, utilisateur_id)

    if compte is None:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable."
        )

    compte.password_hash = hash_password(
        donnees.nouveau_mot_de_passe
    )

    db.commit()

    return {
        "message": "Mot de passe réinitialisé avec succès."
    }