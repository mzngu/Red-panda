from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Ordonnance(Base):
    __tablename__ = 'ordonnance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    utilisateur_id = Column(Integer, ForeignKey('utilisateur.id'), nullable=False)
    nom = Column(String, nullable=False)
    lieu = Column(String)
    date = Column(Date, nullable=False)
    details = Column(Text)
    nom_docteur = Column(String, nullable=False)
    type_docteur = Column(String, nullable=False)

    utilisateur = relationship("Utilisateur", back_populates="ordonnances")
    medicaments = relationship("Medicament", back_populates="ordonnance", cascade="all, delete")
