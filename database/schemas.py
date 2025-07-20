from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import date

# --- Schémas Utilisateur ---

class UtilisateurBase(BaseModel):
    email: EmailStr
    nom: str
    prenom: str
    date_naissance: date
    nationalite: Optional[str] = None
    adresse: Optional[str] = None
    code_postal: Optional[str] = None
    numero_telephone: Optional[str] = None
    role: str

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str

class UtilisateurUpdate(UtilisateurBase):
    email: Optional[EmailStr] = None
    mot_de_passe: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    date_naissance: Optional[date] = None
    role: Optional[str] = None

class Utilisateur(UtilisateurBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Schémas Ordonnance ---

class OrdonnanceBase(BaseModel):
    nom: str
    lieu: Optional[str] = None
    date: date
    details: Optional[str] = None
    nom_docteur: str
    type_docteur: str

class OrdonnanceCreate(OrdonnanceBase):
    pass

class OrdonnanceUpdate(OrdonnanceBase):
    nom: Optional[str] = None
    date: Optional[date] = None
    nom_docteur: Optional[str] = None
    type_docteur: Optional[str] = None

class Ordonnance(OrdonnanceBase):
    id: int
    utilisateur_id: int
    model_config = ConfigDict(from_attributes=True)

# --- Schémas Medicament ---

class MedicamentBase(BaseModel):
    nom: str
    description: Optional[str] = None
    dose: Optional[str] = None
    composant: Optional[str] = None

class MedicamentCreate(MedicamentBase):
    pass

class MedicamentUpdate(MedicamentBase):
    nom: Optional[str] = None

class Medicament(MedicamentBase):
    id: int
    ordonnance_id: int
    model_config = ConfigDict(from_attributes=True)

# --- Schémas Allergie ---

class AllergieBase(BaseModel):
    nom: str
    description: Optional[str] = None

class AllergieCreate(AllergieBase):
    pass

class AllergieUpdate(AllergieBase):
    nom: Optional[str] = None

class Allergie(AllergieBase):
    id: int
    utilisateur_id: int
    model_config = ConfigDict(from_attributes=True)

# --- Schémas Antecedent Médical ---

class AntecedentMedicalBase(BaseModel):
    nom: str
    type: str
    description: Optional[str] = None
    raison: Optional[str] = None
    date_diagnostic: Optional[date] = None

class AntecedentMedicalCreate(AntecedentMedicalBase):
    pass

class AntecedentMedicalUpdate(AntecedentMedicalBase):
    nom: Optional[str] = None
    type: Optional[str] = None

class AntecedentMedical(AntecedentMedicalBase):
    id: int
    utilisateur_id: int
    model_config = ConfigDict(from_attributes=True)
