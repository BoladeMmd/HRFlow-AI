
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, func
)
from sqlalchemy.orm import relationship

from app.database import Base


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(
        Integer,
        ForeignKey("employes.id"),
        unique=True
    )
    username = Column(String(80), nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    role = Column(String(30), nullable=False)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    employe = relationship("Employe", back_populates="utilisateur")
