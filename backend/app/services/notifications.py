
from sqlalchemy.orm import Session

from app.models.notification import Notification


def creer_notification(
    db: Session,
    employe_id: int,
    titre: str,
    message: str
):
    """
    Crée une notification destinée à un employé.
    """

    notification = Notification(
        employe_id=employe_id,
        titre=titre,
        message=message,
        lu=False
    )

    db.add(notification)

    return notification


def notifier_demande_envoyee(db: Session, employe_id: int):
    return creer_notification(
        db=db,
        employe_id=employe_id,
        titre="Demande envoyée",
        message="Votre demande d'absence a été transmise au service RH."
    )


def notifier_demande_traitee(
    db: Session,
    employe_id: int,
    decision: str,
    commentaire: str = None
):
    if decision == "approuvee":
        titre = "Demande approuvée"
        message = "Votre demande d'absence a été approuvée."
    else:
        titre = "Demande rejetée"
        message = "Votre demande d'absence a été rejetée."

    if commentaire:
        message += f" Commentaire : {commentaire}"

    return creer_notification(
        db=db,
        employe_id=employe_id,
        titre=titre,
        message=message
    )
