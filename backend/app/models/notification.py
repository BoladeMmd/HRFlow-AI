
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    func
)

from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    employe_id = Column(
        Integer,
        ForeignKey("employes.id"),
        nullable=False
    )

    titre = Column(
        String,
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    lu = Column(
        Boolean,
        default=False,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.current_timestamp()
    )
