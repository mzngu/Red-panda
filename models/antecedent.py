from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class AntecedentMedical(Base):
    __tablename__ = 'antecedent_medical'

    id = Column(Integer, primary_key=True, autoincrement=True)
    utilisateur_id = Column(Integer, ForeignKey('utilisateur.id'), nullable=False)
    description = Column(Text, nullable=True, default="")
    nom = Column(String, nullable=True, default="")
    date_diagnostic = Column(Date, nullable=True, default="")

    utilisateur = relationship("Utilisateur", back_populates="antecedents")