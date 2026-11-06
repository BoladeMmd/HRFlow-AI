from sqlalchemy import Column, Integer, String, Text, Boolean
from app.database import Base


class TypeAbsence(Base):
    __tablename__ = "types_absence"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    deduit_solde_conges = Column(Boolean, default=False)
    justificatif_obligatoire = Column(Boolean, default=False)
    validation_obligatoire = Column(Boolean, default=True)
    actif = Column(Boolean, default=True)