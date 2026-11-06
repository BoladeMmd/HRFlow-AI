
from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    String,
    Date,
    Boolean
)

from app.database import Base


class RegleConges(Base):
    __tablename__ = "regles_conges"

    id = Column(Integer, primary_key=True, index=True)

    jours_par_mois = Column(
        Numeric(5, 2),
        nullable=False,
        default=2
    )

    unite_calcul = Column(
        String(20),
        nullable=False,
        default="ouvrable"
    )

    date_debut = Column(Date, nullable=False)

    date_fin = Column(Date, nullable=True)

    actif = Column(
        Boolean,
        nullable=False,
        default=True
    )
