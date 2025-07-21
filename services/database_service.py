from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship

from .database_service import Base

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    prenom = Column(String, index=True)
    date_naissance = Column(Date)
    email = Column(String, unique=True, index=True)
    role = Column(Enum("admin", "utilisateur", name="role_enum"), default="utilisateur")

    # Relation: Un utilisateur peut avoir plusieurs ordonnances.
    # `back_populates` lie cette relation à l'attribut 'utilisateur' dans le modèle Ordonnance.
    ordonnances = relationship("Ordonnance", back_populates="utilisateur")

class Ordonnance(Base):
    __tablename__ = "ordonnances"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String)
    date = Column(Date)
    nom_docteur = Column(String)
    type_docteur = Column(String)
    
    # Clé étrangère qui lie cette ordonnance à un utilisateur.
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    utilisateur = relationship("Utilisateur", back_populates="ordonnances")

    # Relation: Une ordonnance peut avoir plusieurs médicaments.
    # `cascade` assure que si une ordonnance est supprimée, ses médicaments le sont aussi.
    medicaments = relationship("Medicament", back_populates="ordonnance", cascade="all, delete-orphan")

class Medicament(Base):
    __tablename__ = "medicaments"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String)
    dose = Column(String)

    # Clé étrangère qui lie ce médicament à une ordonnance.
    ordonnance_id = Column(Integer, ForeignKey("ordonnances.id"))
    ordonnance = relationship("Ordonnance", back_populates="medicaments")