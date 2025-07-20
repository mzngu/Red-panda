from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Medicament(Base):
    __tablename__ = 'medicaments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ordonnance_id = Column(Integer, ForeignKey('ordonnance.id'), nullable=False)
    nom = Column(String, nullable=False)
    description = Column(Text)
    dose = Column(String)
    composant = Column(String)

    ordonnance = relationship("Ordonnance", back_populates="medicaments")
    ordonnance = relationship("Ordonnance", back_populates="medicaments")