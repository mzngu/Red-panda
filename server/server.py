import asyncio
import json
import websockets
import sys
import os
import base64
from io import BytesIO
from PIL import Image
import logging
from dotenv import load_dotenv
from datetime import datetime # <-- Importer datetime

load_dotenv(override=True)
from fastapi import FastAPI, Depends, HTTPException, Response, Cookie, status, BackgroundTasks, Body

from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from threading import Thread
from datetime import timedelta
from server.routes import ordonnances

# Charger les variables d'environnement AVANT tout
load_dotenv()

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Imports relatifs au projet
from services.service import generate_response, system_instruction
from database.database import init_db, get_db
from database.auth import AuthService, get_current_user, get_current_user_optional
import database.controller as crud
import database.schemas as schemas
import models 

# Imports relatifs à l'oubli du mdp
from pydantic import BaseModel, EmailStr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, ssl, uuid
from jose import jwt, JWTError  
import time



FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:4321")
SMTP_HOST    = os.getenv("SMTP_HOST", "smtp.example.com")
SMTP_PORT    = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER    = os.getenv("SMTP_USER", "")
SMTP_PASS    = os.getenv("SMTP_PASS", "")
SMTP_FROM    = os.getenv("SMTP_FROM", "no-reply@dontpanic.local")

JWT_SECRET   = os.getenv("JWT_SECRET", "change-me")   # doit matcher celui d'Auth
JWT_ALG      = os.getenv("JWT_ALGORITHM", "HS256")

class SecureLinkRequest(BaseModel):
    email: EmailStr
    path: str = "/home/home"
    login: bool = False


# Jetons consommés (usage unique)
_consumed_jti = set()

# Configuration
HOST = "localhost"
WEBSOCKET_PORT = 8000
FASTAPI_PORT = 8080

# Stockage des conversations par client
conversations = {}

# Créer l'application FastAPI
app = FastAPI(
    title="Sorrel API",
    description="API pour la gestion des données médicales des utilisateurs.",
    version="1.0.0",
)

# Configuration CORS pour permettre les requêtes depuis Astro
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321", "http://localhost:8000"],  # Ports Astro
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(ordonnances.router)

if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))


def _filled(x) -> bool:
    return x is not None and str(x).strip() != ""

def compute_is_profile_complete(user) -> bool:
    return all([
        _filled(getattr(user, "nom", None)),
        _filled(getattr(user, "prenom", None)),
        _filled(getattr(user, "numero_telephone", None)),
        _filled(getattr(user, "sexe", None)),
    ])


def _send_email_link(to_email: str, link: str):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🔐 Réinitialisation de votre mot de passe"
        msg["From"] = SMTP_FROM
        msg["To"] = to_email

        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #2c3e50;">Bonjour,</h2>
            <p>Vous avez demandé à réinitialiser votre mot de passe.</p>
            <p>Cliquez sur le bouton ci-dessous pour accéder au lien sécurisé :</p>
            <p style="text-align: center; margin: 30px;">
              <a href="{link}" style="background-color: #4CAF50; 
                                       color: white; 
                                       padding: 12px 20px; 
                                       text-decoration: none; 
                                       border-radius: 5px;">
                Réinitialiser mon mot de passe
              </a>
            </p>
            <p>⚠️ Ce lien est valable <b>15 minutes</b> uniquement.</p>
            <p>Si vous n’êtes pas à l’origine de cette demande, ignorez cet email.</p>
            <br>
            <p style="font-size: 12px; color: #777;">L'équipe Don't Panic 🚀</p>
          </body>
        </html>
        """
        msg.attach(MIMEText(html, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_FROM, to_email, msg.as_string())

        print(f"✅ Mail envoyé à {to_email}")
    except Exception as e:
        print(f"❌ Erreur envoi mail : {e}")


@app.post("/mail/send-secure-link", tags=["Mail"])
async def send_secure_link(payload: SecureLinkRequest, background: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Envoie un email avec un lien sécurisé.
    - Génère un JWT (15 min) avec jti, purpose, path
    - Le lien pointe vers /auth/consume-link?token=...
    - Optionnel: login=True pour connecter automatiquement l'utilisateur
    """
    # (Optionnel) si tu veux lier le lien à un utilisateur existant :
    user = crud.get_utilisateur_by_email(db, email=payload.email)
    user_id = str(user.id) if user else "anonymous"

    jti = str(uuid.uuid4())
    token = jwt.encode(
        {
            "sub": user_id,
            "purpose": "magic-link",
            "jti": jti,
            "path": payload.path,
            "login": payload.login,
            "exp": int(time.time()) + 15 * 60 
        },
        JWT_SECRET,
        algorithm=JWT_ALG,
    )

    reset_url = f"{FRONTEND_URL}/reset-password/reset-password?token={token}"
    background.add_task(_send_email_link, payload.email, reset_url)

    return {"ok": True}


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@app.post("/auth/reset-password", tags=["Authentication"])
async def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    payload = AuthService.verify_access_token(data.token, JWT_SECRET, JWT_ALG)
    if not payload or payload.get("purpose") != "magic-link":
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")

    user_id = payload.get("sub")
    if not user_id or user_id == "anonymous":
        raise HTTPException(status_code=400, detail="Utilisateur introuvable")

    user = crud.get_utilisateur(db, utilisateur_id=int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    # ✅ Hash côté AuthService
    hashed = AuthService.get_password_hash(data.new_password)
    crud.update_utilisateur_password(db, utilisateur_id=user.id, hashed_password=hashed)

    return {"message": "Mot de passe réinitialisé avec succès"}


# --- Routes d'authentification ---

@app.post("/auth/register", tags=["Authentication"])
async def register(
    user_data: schemas.RegisterRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """Inscription d'un nouvel utilisateur (email et mot de passe seulement)."""
    try:
        print(f"Données reçues pour inscription: {user_data}")
        
        # Vérifier si l'email existe déjà
        db_user = crud.get_utilisateur_by_email(db, email=user_data.email)
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Un compte avec cet email existe déjà"
            )
        
        # Créer l'utilisateur avec la fonction simplifiée
        new_user = crud.create_utilisateur_simple(
            db=db,
            email=user_data.email,
            mot_de_passe=user_data.mot_de_passe,
            role=user_data.role
        )
        
        print(f"Utilisateur créé: {new_user.id}")
        
        # Créer le token de session
        access_token = AuthService.create_access_token(
            data={"sub": str(new_user.id)},
            expires_delta=timedelta(days=7)
        )
        
        # Définir le cookie de session
        response.set_cookie(
            key="session_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=7 * 24 * 60 * 60
        )
        
        return {
            "message": "Inscription réussie",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "role": new_user.role
            }
        }
        
    except HTTPException as e:
        print(f"Erreur HTTP: {e.detail}")
        raise e
    except Exception as e:
        print(f"Erreur lors de l'inscription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.post("/auth/login", tags=["Authentication"])
async def login(
    login_data: schemas.LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """Connexion d'un utilisateur."""
    try:
        print(f"Tentative de connexion pour: {login_data.email}")
        
        user = AuthService.authenticate_user(db, login_data.email, login_data.mot_de_passe)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Email ou mot de passe incorrect"
            )
        
        # Créer le token de session
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(days=7)
        )
        
        # Définir le cookie de session
        response.set_cookie(
            key="session_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=7 * 24 * 60 * 60
        )
        
        return {
            "message": "Connexion réussie",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role
            }
        }
        
    except HTTPException as e:
        print(f"Erreur HTTP lors de la connexion: {e.detail}")
        raise e
    except Exception as e:
        print(f"Erreur lors de la connexion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.post("/auth/logout", tags=["Authentication"])
async def logout(response: Response):
    """Déconnexion d'un utilisateur."""
    response.delete_cookie(key="session_token")
    return {"message": "Déconnexion réussie"}



def _build_front_url(path: str) -> str:
    """Construit une URL sûre vers le frontend."""
    return f"{FRONTEND_URL.rstrip('/')}/{path.lstrip('/')}"

@app.get("/auth/consume-link", tags=["Authentication"])
async def consume_link(token: str, response: Response):
    """
    Vérifie le JWT (signature, exp, purpose), empêche les réutilisations (jti),
    et redirige uniquement vers une page interne à FRONTEND_URL.
    Optionnel: connexion auto en plaçant le cookie de session.
    """
    fallback_ok = _build_front_url("/verified")
    fallback_err = _build_front_url("/verify-error")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        if payload.get("purpose") != "magic-link":
            return RedirectResponse(fallback_err, status_code=302)

        jti = payload.get("jti")
        if not jti or jti in _consumed_jti:
            return RedirectResponse(fallback_err, status_code=302)

        # Marque comme consommé (usage unique)
        _consumed_jti.add(jti)

        # Détermine la page de redirection
        safe_target = _build_front_url(payload.get("path") or "/")
        resp = RedirectResponse(safe_target, status_code=302)

        # Si login=True, créer un cookie de session
        if payload.get("login") and payload.get("sub") and payload.get("sub") != "anonymous":
            access_token = AuthService.create_access_token(
                data={"sub": payload["sub"]},
                expires_delta=timedelta(days=7)
            )
            resp.set_cookie(
                key="session_token",
                value=access_token,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age=7 * 24 * 60 * 60
            )

        return resp

    except JWTError:
        return RedirectResponse(fallback_err, status_code=302)
    except Exception as e:
        print(f"Erreur consume_link : {e}")
        return RedirectResponse(fallback_err, status_code=302)


@app.get("/auth/me", tags=["Authentication"])
async def get_current_user_info(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Récupère les informations complètes de l'utilisateur connecté (avec un aperçu allergies/antécédents)."""
    is_complete = compute_is_profile_complete(current_user)

    # (Optionnel) petit aperçu pour l'affichage; le front recharge via les routes dédiées.
    allergies = []
    antecedents = []
    try:
        allergies_rows = crud.get_allergies_par_utilisateur(db, current_user.id)
        allergies = [{"id": a.id, "nom": a.nom or ""} for a in allergies_rows]
        antecedent_rows = crud.get_antecedents_par_utilisateur(db, current_user.id)
        antecedents = [{"id": m.id, "nom": m.nom or ""} for m in antecedent_rows]
    except Exception:
        pass

    return {
        "id": current_user.id,
        "email": current_user.email,
        "nom": current_user.nom or "",
        "prenom": current_user.prenom or "",
        "date_naissance": current_user.date_naissance.isoformat() if current_user.date_naissance else None,
        "numero_telephone": current_user.numero_telephone,
        "role": current_user.role,
        "avatar": current_user.avatar or "normal",
        "isProfileComplete": is_complete,
        "sexe": current_user.sexe,
        "allergies": allergies,
        "antecedents": antecedents,
    }

@app.get("/auth/check", tags=["Authentication"])
async def check_auth(current_user = Depends(get_current_user_optional)):
    if not current_user:
        return {"authenticated": False, "user": None}

    is_complete = compute_is_profile_complete(current_user)
    return {
        "authenticated": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "nom": current_user.nom or "",
            "prenom": current_user.prenom or "",
            "date_naissance": current_user.date_naissance.isoformat() if current_user.date_naissance else None,
            "numero_telephone": current_user.numero_telephone,
            "role": current_user.role,
            "avatar": current_user.avatar or "normal",
            "isProfileComplete": is_complete,
            "sexe": current_user.sexe,
        }
    }



# --- Routes existantes (mises à jour pour l'authentification) ---

@app.post("/utilisateurs/", tags=["Utilisateurs"])
def create_utilisateur(
    utilisateur: schemas.UtilisateurCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Crée un nouvel utilisateur (admin seulement)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    db_utilisateur = crud.get_utilisateur_by_email(db, email=utilisateur.email)
    if db_utilisateur:
        raise HTTPException(status_code=400, detail="Cet email est déjà enregistré.")
    return crud.create_utilisateur(db=db, utilisateur=utilisateur)

@app.get("/utilisateurs/", tags=["Utilisateurs"])
def read_utilisateurs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Récupère une liste de tous les utilisateurs (admin seulement)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    utilisateurs = crud.get_utilisateurs(db, skip=skip, limit=limit)
    return utilisateurs

# Remplace la route PUT dans ton server.py

@app.put("/utilisateurs/{utilisateur_id}", tags=["Utilisateurs"])
def update_utilisateur(
    utilisateur_id: int,
    utilisateur: schemas.UtilisateurUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Met à jour un utilisateur."""
    # L'utilisateur peut modifier ses propres infos ou admin peut modifier tous
    if current_user.id != utilisateur_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    try:
        print(f"Mise à jour utilisateur {utilisateur_id} avec données: {utilisateur}")
        
        data = utilisateur.model_dump(exclude_unset=True)

        # 1) gérer le mot de passe si présent
        new_pw = data.pop("mot_de_passe", None)
        if new_pw:
            hashed = AuthService.get_password_hash(new_pw)
            crud.update_utilisateur_password(db, utilisateur_id=utilisateur_id, hashed_password=hashed)

        db_utilisateur = crud.update_utilisateur(db=db, utilisateur_id=utilisateur_id, utilisateur_data=data)
        if db_utilisateur is None:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Retourner les données complètes
        return {
            "id": db_utilisateur.id,
            "email": db_utilisateur.email,
            "nom": db_utilisateur.nom or "",
            "prenom": db_utilisateur.prenom or "",
            "date_naissance": db_utilisateur.date_naissance.isoformat() if db_utilisateur.date_naissance else None,
            "numero_telephone": db_utilisateur.numero_telephone,
            "role": db_utilisateur.role,
            "avatar": db_utilisateur.avatar,
            "sexe": db_utilisateur.sexe or ""
        }
    except Exception as e:
        print(f"Erreur mise à jour utilisateur: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

# Récupération d'un utilisateur spécifique
@app.get("/utilisateurs/{utilisateur_id}", tags=["Utilisateurs"])
def read_utilisateur(
    utilisateur_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Récupère un utilisateur par son ID."""
    # L'utilisateur peut voir ses propres infos ou admin peut voir tous
    if current_user.id != utilisateur_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    db_utilisateur = crud.get_utilisateur(db, utilisateur_id=utilisateur_id)
    if db_utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    
    return {
        "id": db_utilisateur.id,
        "email": db_utilisateur.email,
        "nom": db_utilisateur.nom or "",
        "prenom": db_utilisateur.prenom or "",
        "date_naissance": db_utilisateur.date_naissance.isoformat() if db_utilisateur.date_naissance else None,
        "numero_telephone": db_utilisateur.numero_telephone,
        "role": db_utilisateur.role,
        "sexe": db_utilisateur.sexe or "",
    }

# ----------------------
#   ALLERGIES (CRUD)
# ----------------------
@app.get("/utilisateurs/{utilisateur_id}/allergies", tags=["Allergies"])
def list_allergies(utilisateur_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.id != utilisateur_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission refusée")
    rows = crud.get_allergies_par_utilisateur(db, utilisateur_id)
    return [{"id": a.id, "nom": a.nom or "", "description": a.description_allergie or ""} for a in rows]

@app.post("/utilisateurs/{utilisateur_id}/allergies", tags=["Allergies"])
def add_allergie(utilisateur_id: int, payload: schemas.AllergieCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.id != utilisateur_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission refusée")
    row = crud.create_allergie_pour_utilisateur(db, payload, utilisateur_id)
    return {"id": row.id, "nom": row.nom or "", "description": row.description_allergie or ""}

@app.delete("/utilisateurs/{utilisateur_id}/allergies/{allergie_id}", tags=["Allergies"])
def delete_allergie(utilisateur_id: int, allergie_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.id != utilisateur_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission refusée")
    row = crud.get_allergie(db, allergie_id)
    if not row or row.utilisateur_id != utilisateur_id:
        raise HTTPException(status_code=404, detail="Allergie introuvable")
    crud.delete_allergie(db, allergie_id)
    return {"ok": True}

# -------------------------------
#   ANTECEDENTS MEDICAUX (CRUD)
# -------------------------------
@app.get("/utilisateurs/{utilisateur_id}/antecedents", tags=["Antecedents"])
def list_antecedents(utilisateur_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.id != utilisateur_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission refusée")
    rows = crud.get_antecedents_par_utilisateur(db, utilisateur_id)
    return [{
        "id": r.id, 
        "nom": r.nom or "", 
        "description": r.description or "", 
        "date_diagnostic": (r.date_diagnostic.isoformat() if r.date_diagnostic else None),
        "type": r.type or ""  # Ajouter ce champ dans la réponse
    } for r in rows]

@app.post("/utilisateurs/{utilisateur_id}/antecedents", tags=["Antecedents"])
def add_antecedent(utilisateur_id: int, payload: schemas.AntecedentMedicalCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.id != utilisateur_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission refusée")
    row = crud.create_antecedent_pour_utilisateur(db, payload, utilisateur_id)
    return {
        "id": row.id, 
        "nom": row.nom or "", 
        "description": row.description or "", 
        "date_diagnostic": (row.date_diagnostic.isoformat() if row.date_diagnostic else None),
        "type": "maladie"  # Valeur par défaut temporaire
    }

@app.delete("/utilisateurs/{utilisateur_id}/antecedents/{antecedent_id}", tags=["Antecedents"])
def delete_antecedent(utilisateur_id: int, antecedent_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.id != utilisateur_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission refusée")
    row = db.query(models.AntecedentMedical).filter(models.AntecedentMedical.id == antecedent_id).first()
    if not row or row.utilisateur_id != utilisateur_id:
        raise HTTPException(status_code=404, detail="Antécédent introuvable")
    db.delete(row); db.commit()
    return {"ok": True}

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenue sur l'API Sorrel"}

# --- Gestion WebSocket (code existant) ---

async def handle_client(websocket):
    """Gère les connexions client WebSocket."""
    client_id = id(websocket)
    # On ne stocke plus une simple liste, mais un dictionnaire avec l'historique
    conversations[client_id] = {"history": []}
    
    try:
        print(f"Client {client_id} connecté")
        
        async for message in websocket:
            try:
                data = json.loads(message)
                user_message = data.get("message", "")
                image_data_url = data.get("image")
                user_context = data.get("context") # <-- Récupération du contexte

                # Construire une instruction système personnalisée si le contexte est fourni
                current_system_instruction = system_instruction
                if user_context:
                    context_parts = ["Voici des informations sur l'utilisateur actuel que tu dois impérativement prendre en compte pour chaque réponse :"]
                    
                    if user_context.get("prenom"):
                        context_parts.append(f"- Prénom: {user_context['prenom']}")
                    if user_context.get("nom"):
                        context_parts.append(f"- Nom: {user_context['nom']}")
                    if user_context.get("sexe"):
                        context_parts.append(f"- Sexe: {user_context['sexe']}")
                    
                    if user_context.get("date_naissance"):
                        try:
                            birth_date = datetime.fromisoformat(user_context['date_naissance'].split('T')[0])
                            age = (datetime.now() - birth_date).days // 365
                            context_parts.append(f"- Âge: {age} ans (né(e) le {birth_date.strftime('%d/%m/%Y')})")
                        except (ValueError, TypeError):
                            pass # Ignorer si la date est invalide

                    if user_context.get("allergies"):
                        allergies_str = ", ".join([a.get('nom', '') for a in user_context['allergies'] if a.get('nom')])
                        if allergies_str:
                            context_parts.append(f"- Allergies connues: {allergies_str}")

                    if user_context.get("antecedents"):
                        antecedents_str = ", ".join([a.get('nom', '') for a in user_context['antecedents'] if a.get('nom')])
                        if antecedents_str:
                            context_parts.append(f"- Antécédents médicaux: {antecedents_str}")
                    
                    # Ajoute le contexte à l'instruction système de base
                    if len(context_parts) > 1:
                        current_system_instruction += "\n\n" + "\n".join(context_parts)
                        current_system_instruction += "\n\nBase tes réponses sur ces informations pour être plus pertinent et sécuritaire."

                # Prépare le contenu pour le modèle
                user_content = []
                if user_message:
                    user_content.append(user_message)

                if image_data_url:
                    try:
                        header, encoded = image_data_url.split(",", 1)
                        image_data = base64.b64decode(encoded)
                        image = Image.open(BytesIO(image_data))
                        user_content.append(image)
                    except Exception as e:
                        print(f"Erreur de décodage de l'image: {e}")

                if user_content:
                    # Ajoute le message de l'utilisateur à l'historique
                    conversations[client_id]["history"].append({"role": "user", "parts": user_content})

                # Prépare la conversation complète pour le modèle (SANS le rôle "system")
                full_conversation = conversations[client_id]["history"]

                response = generate_response(full_conversation, system_instruction_update=current_system_instruction)
                
                # Ajoute la réponse du modèle à l'historique
                conversations[client_id]["history"].append({"role": "model", "parts": [response]})
                
                await websocket.send(json.dumps({"response": response}))
                
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"error": "Format JSON invalide"}))
            except Exception as e:
                print(f"Erreur lors du traitement du message: {str(e)}")
                await websocket.send(json.dumps({"error": "Une erreur est survenue"}))
    
    finally:
        if client_id in conversations:
            del conversations[client_id]
        print(f"Client {client_id} déconnecté")

async def start_websocket_server():
    """Démarre le serveur WebSocket."""
    # Autorise explicitement l'origine de ton frontend Astro
    allowed_origins = ["http://localhost:4321"]
    async with websockets.serve(handle_client, HOST, WEBSOCKET_PORT, origins=allowed_origins):
        print(f"🚀 Serveur WebSocket démarré sur {HOST}:{WEBSOCKET_PORT}")
        await asyncio.Future()

def start_fastapi_server():
    """Démarre le serveur FastAPI."""
    uvicorn.run(app, host=HOST, port=FASTAPI_PORT, log_level="info")

async def main():
    """Démarre les deux serveurs."""
    try:
        print("🔧 Initialisation de la base de données...")
        init_db()
        print("✅ Base de données initialisée avec succès!")
        
        fastapi_thread = Thread(target=start_fastapi_server, daemon=True)
        fastapi_thread.start()
        
        print(f"🚀 Serveur FastAPI démarré sur {HOST}:{FASTAPI_PORT}")
        print(f"📖 Documentation API disponible sur http://{HOST}:{FASTAPI_PORT}/docs")
        
        await start_websocket_server()
        
    except Exception as e:
        logging.error(f"Erreur lors du démarrage du serveur: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        sys.exit(1)
