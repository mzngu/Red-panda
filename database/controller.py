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
        numero_telephone=utilisateur.numero_telephone,
        role=utilisateur.role
    )
    db.add(db_utilisateur)
    db.commit()
    db.refresh(db_utilisateur)
    return db_utilisateur

# Remplace ou ajoute cette fonction dans database/controller.py

def update_utilisateur(db: Session, utilisateur_id: int, utilisateur_data):
    """Met à jour un utilisateur."""
    print(f"Controller - Mise à jour utilisateur ID: {utilisateur_id}")
    
    db_utilisateur = get_utilisateur(db, utilisateur_id)
    if not db_utilisateur:
        print(f"Utilisateur {utilisateur_id} non trouvé")
        return None

    # Préparer les données à mettre à jour
    if hasattr(utilisateur_data, 'dict'):
        # Si c'est un objet Pydantic
        update_data = utilisateur_data.dict(exclude_unset=True)
    else:
        # Si c'est déjà un dictionnaire
        update_data = utilisateur_data

    print(f"Données à mettre à jour: {update_data}")

    # Mise à jour des champs
    for key, value in update_data.items():
        if hasattr(db_utilisateur, key):
            print(f"Mise à jour {key}: {getattr(db_utilisateur, key)} -> {value}")
            setattr(db_utilisateur, key, value)

    try:
        db.commit()
        db.refresh(db_utilisateur)
        print(f"Utilisateur {utilisateur_id} mis à jour avec succès")
        return db_utilisateur
    except Exception as e:
        print(f"Erreur lors de la mise à jour: {str(e)}")
        db.rollback()
        raise e

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


def create_utilisateur_simple(db: Session, email: str, mot_de_passe: str, role: str = "utilisateur"):
    """Crée un utilisateur avec seulement email et mot de passe."""
    from datetime import date
    import sys
    import os
    
    # Ajouter le chemin parent pour les imports
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    from models.utilisateur import Utilisateur
    
    hashed_password = get_password_hash(mot_de_passe)
    db_utilisateur = Utilisateur(
        email=email,
        mot_de_passe=hashed_password,
        nom="",
        prenom="",
        date_naissance=date.today(),
        numero_telephone=None,
        role=role
    )
    db.add(db_utilisateur)
    db.commit()
    db.refresh(db_utilisateur)
    return db_utilisateur