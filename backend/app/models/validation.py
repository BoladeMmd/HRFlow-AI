from sqlalchemy import (
    Column, Integer, String, Text,
    ForeignKey, DateTime, func
)
from app.database import Base


class Validation(Base):
    __tablename__ = "validations"

    id = Column(Integer, primary_key=True, index=True)

    demande_id = Column(
        Integer,
        ForeignKey("demandes_absence.id"),
        nullable=False
    )

    valideur_id = Column(
        Integer,
        ForeignKey("utilisateurs.id"),
        nullable=False
    )

    decision = Column(String(20), nullable=False)

    commentaire = Column(Text)

    date_decision = Column(
        DateTime,
        server_default=func.current_timestamp()
    )