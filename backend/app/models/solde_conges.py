
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
    UniqueConstraint,
    CheckConstraint
)

from app.database import Base


class SoldeConges(Base):
    __tablename__ = "soldes_conges"

    id = Column(Integer, primary_key=True, index=True)

    employe_id = Column(
        Integer,
        ForeignKey("employes.id"),
        nullable=False
    )

    annee = Column(Integer, nullable=False)

    solde_initial = Column(Numeric(6, 2), default=0, nullable=False)
    jours_acquis = Column(Numeric(6, 2), default=0, nullable=False)
    jours_pris = Column(Numeric(6, 2), default=0, nullable=False)
    solde_reporte = Column(Numeric(6, 2), default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "employe_id",
            "annee",
            name="uq_solde_employe_annee"
        ),
        CheckConstraint("solde_initial >= 0"),
        CheckConstraint("jours_acquis >= 0"),
        CheckConstraint("jours_pris >= 0"),
        CheckConstraint("solde_reporte >= 0"),
    )

    @property
    def solde_disponible(self):
        return (
            self.solde_initial
            + self.jours_acquis
            + self.solde_reporte
            - self.jours_pris
        )
