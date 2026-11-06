from sqlalchemy import (
    Column, Integer, Date, String, Text,
    Numeric, ForeignKey, DateTime, func
)
from app.database import Base


class DemandeAbsence(Base):
    __tablename__ = "demandes_absence"

    id = Column(Integer, primary_key=True, index=True)

    employe_id = Column(
        Integer,
        ForeignKey("employes.id"),
        nullable=False
    )

    type_absence_id = Column(
        Integer,
        ForeignKey("types_absence.id"),
        nullable=False
    )

    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    nombre_jours = Column(Numeric(6, 2), nullable=False)

    motif = Column(Text)
    justificatif_path = Column(String(500))

    statut = Column(String(20), nullable=False, default="en_attente")

    created_at = Column(
        DateTime,
        server_default=func.current_timestamp()
    )