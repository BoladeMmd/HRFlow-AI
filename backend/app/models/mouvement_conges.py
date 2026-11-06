
from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    ForeignKey,
    DateTime,
    CheckConstraint,
    func
)

from app.database import Base


class MouvementConges(Base):
    __tablename__ = "mouvements_conges"

    id = Column(Integer, primary_key=True, index=True)

    employe_id = Column(
        Integer,
        ForeignKey("employes.id"),
        nullable=False
    )

    solde_id = Column(
        Integer,
        ForeignKey("soldes_conges.id"),
        nullable=False
    )

    type_mouvement = Column(
        String(30),
        nullable=False
    )

    nombre_jours = Column(
        Numeric(6, 2),
        nullable=False
    )

    periode = Column(String(7))

    demande_id = Column(
        Integer,
        ForeignKey("demandes_absence.id"),
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.current_timestamp()
    )

    __table_args__ = (
        CheckConstraint("nombre_jours > 0"),
    )
