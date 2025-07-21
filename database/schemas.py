from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import date

# --- Schémas Utilisateur ---

class UtilisateurBase(BaseModel):
    email: EmailStr
    nom: Optional[str] = ""
    prenom: Optional[str] = ""
    date_naissance: Optional[date] = None
    numero_telephone: Optional[str] = None
    role: str = "utilisateur"

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str

class UtilisateurUpdate(BaseModel):
    email: Optional[EmailStr] = None
    mot_de_passe: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    date_naissance: Optional[date] = None
    numero_telephone: Optional[str] = None
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

# --- Schémas d'authentification ---

class LoginRequest(BaseModel):
    email: EmailStr
    mot_de_passe: str

class LoginResponse(BaseModel):
    message: str
    user: Utilisateur

class RegisterRequest(BaseModel):
    email: EmailStr
    mot_de_passe: str
    role: str = "utilisateur"

class LogoutResponse(BaseModel):
    message: str