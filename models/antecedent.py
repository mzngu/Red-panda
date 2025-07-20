from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class AntecedentMedical(Base):
    __tablename__ = 'antecedent_medical'

    id = Column(Integer, primary_key=True, autoincrement=True)
    utilisateur_id = Column(Integer, ForeignKey('utilisateur.id'), nullable=False)
    type = Column(String, nullable=False)
    description = Column(Text)
    nom = Column(String, nullable=False)
    raison = Column(String)
    date_diagnostic = Column(Date)

    utilisateur = relationship("Utilisateur", back_populates="antecedents")