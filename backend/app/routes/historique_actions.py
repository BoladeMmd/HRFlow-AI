
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.routes.auth import require_roles


router = APIRouter(
    prefix="/historique-actions",
    tags=["Historique des actions"]
)


@router.get("/")
def consulter_historique(
    limite: int = Query(default=50, ge=1, le=200),
    decalage: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(
        require_roles("admin_rh")
    )
):
    requete = text("""
        SELECT
            h.id,
            h.utilisateur_id,
            h.action,
            h.description,
            h.date_action,
            u.username
        FROM historique_actions h
        LEFT JOIN utilisateurs u
            ON h.utilisateur_id = u.id
        ORDER BY h.date_action DESC NULLS LAST, h.id DESC
        LIMIT :limite
        OFFSET :decalage
    """)

    resultat = db.execute(
        requete,
        {
            "limite": limite,
            "decalage": decalage
        }
    )

    return [
        dict(ligne)
        for ligne in resultat.mappings().all()
    ]


@router.get("/nombre")
def nombre_actions(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(
        require_roles("admin_rh")
    )
):
    resultat = db.execute(
        text("""
            SELECT COUNT(*)
            FROM historique_actions
        """)
    ).scalar_one()

    return {
        "nombre_total_actions": resultat
    }
