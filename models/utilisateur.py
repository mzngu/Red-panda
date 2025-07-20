from sqlalchemy import Column, Integer, String, Date, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Utilisateur(Base):
    __tablename__ = 'utilisateur'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    date_naissance = Column(Date, nullable=False)
    nationalite = Column(String)
    adresse = Column(String)
    code_postal = Column(String)
    email = Column(String, nullable=False, unique=True)
    mot_de_passe = Column(String, nullable=False)
    numero_telephone = Column(String)
    role = Column(String, nullable=False)

    __table_args__ = (
        CheckConstraint("role IN ('admin', 'utilisateur')", name='check_role'),
    )

    ordonnances = relationship("Ordonnance", back_populates="utilisateur", cascade="all, delete")
    allergies = relationship("Allergie", back_populates="utilisateur", cascade="all, delete")
    antecedents = relationship("AntecedentMedical", back_populates="utilisateur", cascade="all, delete")
