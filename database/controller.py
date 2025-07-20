from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models
from . import schemas

# --- Configuration du hachage de mot de passe ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --- CRUD pour Utilisateur ---

def get_utilisateur(db: Session, utilisateur_id: int):
    """Récupère un utilisateur par son ID."""
    return db.query(models.Utilisateur).filter(models.Utilisateur.id == utilisateur_id).first()

def get_utilisateur_by_email(db: Session, email: str):
    """Récupère un utilisateur par son email."""
    return db.query(models.Utilisateur).filter(models.Utilisateur.email == email).first()

def get_utilisateurs(db: Session, skip: int = 0, limit: int = 100):
    """Récupère une liste d'utilisateurs."""
    return db.query(models.Utilisateur).offset(skip).limit(limit).all()

def create_utilisateur(db: Session, utilisateur: schemas.UtilisateurCreate):
    """Crée un nouvel utilisateur avec un mot de passe haché."""
    hashed_password = get_password_hash(utilisateur.mot_de_passe)
    db_utilisateur = models.Utilisateur(
        email=utilisateur.email,
        mot_de_passe=hashed_password,
        nom=utilisateur.nom,
        prenom=utilisateur.prenom,
        date_naissance=utilisateur.date_naissance,
        nationalite=utilisateur.nationalite,
        adresse=utilisateur.adresse,
        code_postal=utilisateur.code_postal,
        numero_telephone=utilisateur.numero_telephone,
        role=utilisateur.role
    )
    db.add(db_utilisateur)
    db.commit()
    db.refresh(db_utilisateur)
    return db_utilisateur

def update_utilisateur(db: Session, utilisateur_id: int, utilisateur_data: schemas.UtilisateurCreate):
    """Met à jour un utilisateur."""
    db_utilisateur = get_utilisateur(db, utilisateur_id)
    if not db_utilisateur:
        return None

    update_data = utilisateur_data.model_dump(exclude_unset=True)

    if "mot_de_passe" in update_data and update_data["mot_de_passe"]:
        hashed_password = get_password_hash(update_data["mot_de_passe"])
        db_utilisateur.mot_de_passe = hashed_password
        del update_data["mot_de_passe"]

    for key, value in update_data.items():
        setattr(db_utilisateur, key, value)

    db.commit()
    db.refresh(db_utilisateur)
    return db_utilisateur

def delete_utilisateur(db: Session, utilisateur_id: int):
    """Supprime un utilisateur et ses données en cascade."""
    db_utilisateur = get_utilisateur(db, utilisateur_id)
    if not db_utilisateur:
        return None
    db.delete(db_utilisateur)
    db.commit()
    return db_utilisateur

# --- CRUD pour Ordonnance ---

def create_ordonnance_pour_utilisateur(db: Session, ordonnance: schemas.OrdonnanceCreate, utilisateur_id: int):
    """Crée une nouvelle ordonnance pour un utilisateur."""
    db_ordonnance = models.Ordonnance(**ordonnance.model_dump(), utilisateur_id=utilisateur_id)
    db.add(db_ordonnance)
    db.commit()
    db.refresh(db_ordonnance)
    return db_ordonnance

def get_ordonnances_par_utilisateur(db: Session, utilisateur_id: int, skip: int = 0, limit: int = 100):
    """Récupère toutes les ordonnances d'un utilisateur."""
    return db.query(models.Ordonnance).filter(models.Ordonnance.utilisateur_id == utilisateur_id).offset(skip).limit(limit).all()

def get_ordonnance(db: Session, ordonnance_id: int):
    """Récupère une ordonnance par son ID."""
    return db.query(models.Ordonnance).filter(models.Ordonnance.id == ordonnance_id).first()

def update_ordonnance(db: Session, ordonnance_id: int, ordonnance_data: schemas.OrdonnanceCreate):
    """Met à jour une ordonnance."""
    db_ordonnance = get_ordonnance(db, ordonnance_id)
    if not db_ordonnance:
        return None
    update_data = ordonnance_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ordonnance, key, value)
    db.commit()
    db.refresh(db_ordonnance)
    return db_ordonnance

def delete_ordonnance(db: Session, ordonnance_id: int):
    """Supprime une ordonnance."""
    db_ordonnance = get_ordonnance(db, ordonnance_id)
    if not db_ordonnance:
        return None
    db.delete(db_ordonnance)
    db.commit()
    return db_ordonnance

# --- CRUD pour Medicament ---

def create_medicament_pour_ordonnance(db: Session, medicament: schemas.MedicamentCreate, ordonnance_id: int):
    """Crée un nouveau médicament pour une ordonnance."""
    db_medicament = models.Medicament(**medicament.model_dump(), ordonnance_id=ordonnance_id)
    db.add(db_medicament)
    db.commit()
    db.refresh(db_medicament)
    return db_medicament

def get_medicaments_par_ordonnance(db: Session, ordonnance_id: int, skip: int = 0, limit: int = 100):
    """Récupère les médicaments d'une ordonnance."""
    return db.query(models.Medicament).filter(models.Medicament.ordonnance_id == ordonnance_id).offset(skip).limit(limit).all()

def get_medicament(db: Session, medicament_id: int):
    """Récupère un médicament par son ID."""
    return db.query(models.Medicament).filter(models.Medicament.id == medicament_id).first()

def update_medicament(db: Session, medicament_id: int, medicament_data: schemas.MedicamentCreate):
    """Met à jour un médicament."""
    db_medicament = get_medicament(db, medicament_id)
    if not db_medicament:
        return None
    update_data = medicament_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_medicament, key, value)
    db.commit()
    db.refresh(db_medicament)
    return db_medicament

def delete_medicament(db: Session, medicament_id: int):
    """Supprime un médicament."""
    db_medicament = get_medicament(db, medicament_id)
    if not db_medicament:
        return None
    db.delete(db_medicament)
    db.commit()
    return db_medicament

# --- CRUD pour Allergie ---

def create_allergie_pour_utilisateur(db: Session, allergie: schemas.AllergieCreate, utilisateur_id: int):
    """Crée une nouvelle allergie pour un utilisateur."""
    db_allergie = models.Allergie(**allergie.model_dump(), utilisateur_id=utilisateur_id)
    db.add(db_allergie)
    db.commit()
    db.refresh(db_allergie)
    return db_allergie

def get_allergies_par_utilisateur(db: Session, utilisateur_id: int, skip: int = 0, limit: int = 100):
    """Récupère les allergies d'un utilisateur."""
    return db.query(models.Allergie).filter(models.Allergie.utilisateur_id == utilisateur_id).offset(skip).limit(limit).all()

def get_allergie(db: Session, allergie_id: int):
    """Récupère une allergie par son ID."""
    return db.query(models.Allergie).filter(models.Allergie.id == allergie_id).first()

def update_allergie(db: Session, allergie_id: int, allergie_data: schemas.AllergieCreate):
    """Met à jour une allergie."""
    db_allergie = get_allergie(db, allergie_id)
    if not db_allergie:
        return None
    update_data = allergie_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_allergie, key, value)
    db.commit()
    db.refresh(db_allergie)
    return db_allergie

def delete_allergie(db: Session, allergie_id: int):
    """Supprime une allergie."""
    db_allergie = get_allergie(db, allergie_id)
    if not db_allergie:
        return None
    db.delete(db_allergie)
    db.commit()
    return db_allergie

# --- CRUD pour AntecedentMedical ---

def create_antecedent_pour_utilisateur(db: Session, antecedent: schemas.AntecedentMedicalCreate, utilisateur_id: int):
    """Crée un nouvel antécédent pour un utilisateur."""
    db_antecedent = models.AntecedentMedical(**antecedent.model_dump(), utilisateur_id=utilisateur_id)
    db.add(db_antecedent)
    db.commit()
    db.refresh(db_antecedent)
    return db_antecedent

def get_antecedents_par_utilisateur(db: Session, utilisateur_id: int, skip: int = 0, limit: int = 100):
    """Récupère les antécédents d'un utilisateur."""
    return db.query(models.AntecedentMedical).filter(models.AntecedentMedical.utilisateur_id == utilisateur_id).offset(skip).limit(limit).all()