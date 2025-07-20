from sqlalchemy import create_engine, Column, Integer, String, Date, Enum, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from astro.settings import BASE_DIR

# --- Configuration de la base de données SQLAlchemy ---
# On utilise la même base de données que Django pour la simplicité.
SQLALCHEMY_DATABASE_URL = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- Définition des Modèles SQLAlchemy ---
# Note : On garde le modèle Utilisateur dans l'ORM de Django.
# On lie les autres modèles à l'utilisateur via `utilisateur_id`.

class Ordonnance(Base):
    __tablename__ = "sqla_ordonnances"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255))
    lieu = Column(String(255), nullable=True)
    date = Column(Date)
    details = Column(Text, nullable=True)
    nom_docteur = Column(String(255))
    type_docteur = Column(String(255))
    utilisateur_id = Column(Integer, nullable=False) # Lien vers l'utilisateur Django

    medicaments = relationship("Medicament", back_populates="ordonnance", cascade="all, delete-orphan")

class Medicament(Base):
    __tablename__ = "sqla_medicaments"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255))
    description = Column(Text, nullable=True)
    dose = Column(String(255), nullable=True)
    composant = Column(String(255), nullable=True)
    ordonnance_id = Column(Integer, ForeignKey("sqla_ordonnances.id"))
    ordonnance = relationship("Ordonnance", back_populates="medicaments")

class Allergie(Base):
    __tablename__ = "sqla_allergies"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255))
    description = Column(Text, nullable=True)
    utilisateur_id = Column(Integer, nullable=False)

class AntecedentMedical(Base):
    __tablename__ = "sqla_antecedents"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(255))
    description = Column(Text, nullable=True)
    nom = Column(String(255))
    raison = Column(Text, nullable=True)
    date_diagnostic = Column(Date, nullable=True)
    utilisateur_id = Column(Integer, nullable=False)

def init_db():
    """Crée les tables SQLAlchemy dans la base de données."""
    print("Création des tables pour SQLAlchemy...")
    Base.metadata.create_all(bind=engine)
    print("Tables créées.")