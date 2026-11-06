from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.security import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    create_access_token,
    verify_password
)

router = APIRouter(prefix="/auth", tags=["Authentification"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    utilisateur = db.scalar(
        select(Utilisateur).where(
            Utilisateur.username == form_data.username
        )
    )

    if (
        utilisateur is None
        or not utilisateur.actif
        or not verify_password(
            form_data.password,
            utilisateur.password_hash
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if (
        utilisateur.employe is not None
        and utilisateur.employe.statut != "actif"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce compte est associé à un employé inactif."
        )

    token = create_access_token(utilisateur.username)

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": utilisateur.role
    }


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Jeton invalide ou expiré.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        username = payload.get("sub")

        if not username:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    utilisateur = db.scalar(
        select(Utilisateur).where(
            Utilisateur.username == username
        )
    )

    if utilisateur is None or not utilisateur.actif:
        raise credentials_exception

    if (
        utilisateur.employe is not None
        and utilisateur.employe.statut != "actif"
    ):
        raise credentials_exception

    return utilisateur


def require_roles(*roles: str):
    def verifier_role(
        utilisateur: Utilisateur = Depends(get_current_user)
    ):
        if utilisateur.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous n'avez pas les autorisations nécessaires."
            )
        return utilisateur

    return verifier_role


@router.get("/me")
def consulter_profil(
    utilisateur: Utilisateur = Depends(get_current_user)
):
    return {
        "id": utilisateur.id,
        "username": utilisateur.username,
        "role": utilisateur.role,
        "actif": utilisateur.actif,
        "employe_id": utilisateur.employe_id
    }