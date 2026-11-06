
from sqlalchemy import (
    Column, Integer, String, Date, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship

from app.database import Base


class Employe(Base):
    __tablename__ = "employes"

    id = Column(Integer, primary_key=True, index=True)
    matricule = Column(String(30), nullable=False, unique=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    telephone = Column(String(30))
    date_embauche = Column(Date, nullable=False)
    departement_id = Column(
        Integer,
        ForeignKey("departements.id")
    )
    poste = Column(String(100))
    statut = Column(String(20), nullable=False, default="actif")
    created_at = Column(DateTime, server_default=func.current_timestamp())

    departement = relationship("Departement", back_populates="employes")
    utilisateur = relationship(
        "Utilisateur",
        back_populates="employe",
        uselist=False
    )
