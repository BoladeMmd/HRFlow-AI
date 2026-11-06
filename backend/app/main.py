
from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.routes.departements import router as departements_router
from app.routes.employes import router as employes_router
from app.routes.auth import router as auth_router
from app.routes.utilisateurs import router as utilisateurs_router
from app.routes.types_absence import router as types_absence_router
from app.routes.demandes_absence import router as demandes_absence_router
from app.routes.validations import router as validations_router
from app.routes.soldes_conges import router as soldes_conges_router
from app.routes.acquisition_conges import router as acquisition_conges_router
from contextlib import asynccontextmanager
from app.routes.analyse_rh import router as analyse_rh_router

from app.scheduler import demarrer_scheduler, arreter_scheduler
from app.routes import historique_actions
from app.routes import report_conges
from app.routes import notifications
from app.routes.assistant_rh import router as assistant_rh_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Démarrage de l'application
    demarrer_scheduler()

    yield

    # Arrêt propre du planificateur
    arreter_scheduler()


# Création de l'application FastAPI
app = FastAPI(
    title="HRFlow AI API",
    description="API intelligente de gestion des absences et congés",
    version="1.0.0",
    lifespan=lifespan
)


# Enregistrement des routes
app.include_router(departements_router)
app.include_router(employes_router)
app.include_router(auth_router)
app.include_router(utilisateurs_router)
app.include_router(types_absence_router)
app.include_router(demandes_absence_router)
app.include_router(validations_router)
app.include_router(soldes_conges_router)
app.include_router(acquisition_conges_router)
app.include_router(historique_actions.router)
app.include_router(report_conges.router)
app.include_router(notifications.router)
app.include_router(analyse_rh_router)
app.include_router(assistant_rh_router)

@app.get("/")
def accueil():
    return {
        "message": "Bienvenue sur HRFlow AI",
        "status": "API opérationnelle"
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception:
        return {
            "status": "unhealthy",
            "database": "disconnected"
        }
