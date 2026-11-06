
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.notification import Notification
from app.routes.auth import get_current_user

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# Consulter les notifications de l'employé connecté
@router.get("/mes-notifications")
def mes_notifications(
    db: Session = Depends(get_db),
    utilisateur=Depends(get_current_user)
):
    if utilisateur.employe_id is None:
        raise HTTPException(
            status_code=403,
            detail="Aucun employé associé à ce compte."
        )

    notifications = db.scalars(
        select(Notification)
        .where(Notification.employe_id == utilisateur.employe_id)
        .order_by(Notification.created_at.desc())
    ).all()

    return notifications


# Compter les notifications non lues
@router.get("/non-lues/nombre")
def nombre_notifications_non_lues(
    db: Session = Depends(get_db),
    utilisateur=Depends(get_current_user)
):
    if utilisateur.employe_id is None:
        raise HTTPException(
            status_code=403,
            detail="Aucun employé associé à ce compte."
        )

    nombre = db.scalar(
        select(func.count(Notification.id))
        .where(
            Notification.employe_id == utilisateur.employe_id,
            Notification.lu == False
        )
    )

    return {"nombre_non_lues": nombre}


# Marquer une notification comme lue
@router.patch("/{notification_id}/lire")
def marquer_comme_lue(
    notification_id: int,
    db: Session = Depends(get_db),
    utilisateur=Depends(get_current_user)
):
    if utilisateur.employe_id is None:
        raise HTTPException(
            status_code=403,
            detail="Aucun employé associé à ce compte."
        )

    notification = db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.employe_id == utilisateur.employe_id
        )
    )

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification introuvable."
        )

    notification.lu = True
    db.commit()

    return {"message": "Notification marquée comme lue."}
