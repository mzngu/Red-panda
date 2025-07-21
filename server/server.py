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
from fastapi import FastAPI, Depends, HTTPException, Response, Cookie, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from threading import Thread
from datetime import timedelta

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
    allow_origins=["http://localhost:4321", "http://localhost:3000"],  # Ports Astro
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

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

# Remplace la route /auth/me dans ton server.py

@app.get("/auth/me", tags=["Authentication"])
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Récupère les informations complètes de l'utilisateur connecté."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nom": current_user.nom or "",
        "prenom": current_user.prenom or "",
        "date_naissance": current_user.date_naissance.isoformat() if current_user.date_naissance else None,
        "numero_telephone": current_user.numero_telephone,
        "role": current_user.role
    }

# Remplace la route /auth/check dans ton server.py

@app.get("/auth/check", tags=["Authentication"])
async def check_auth(current_user = Depends(get_current_user_optional)):
    """Vérifie si l'utilisateur est connecté et retourne ses informations complètes."""
    return {
        "authenticated": current_user is not None,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "nom": current_user.nom or "",
            "prenom": current_user.prenom or "",
            "date_naissance": current_user.date_naissance.isoformat() if current_user.date_naissance else None,
            "numero_telephone": current_user.numero_telephone,
            "role": current_user.role
        } if current_user else None
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
        
        db_utilisateur = crud.update_utilisateur(db=db, utilisateur_id=utilisateur_id, utilisateur_data=utilisateur)
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
            "role": db_utilisateur.role
        }
    except Exception as e:
        print(f"Erreur mise à jour utilisateur: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

# Ajoute aussi cette route pour récupérer un utilisateur spécifique
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
        "role": db_utilisateur.role
    }

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenue sur l'API Sorrel"}

# --- Gestion WebSocket (code existant) ---

async def handle_client(websocket):
    """Gère les connexions client WebSocket."""
    client_id = id(websocket)
    conversations[client_id] = []
    
    try:
        print(f"Client {client_id} connecté")
        
        async for message in websocket:
            try:
                data = json.loads(message)
                user_message = data.get("message", "")
                image_data_url = data.get("image")

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
                    conversations[client_id].append({"role": "user", "parts": user_content})

                response = generate_response(conversations[client_id])
                conversations[client_id].append({"role": "model", "parts": [response]})
                
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
    async with websockets.serve(handle_client, HOST, WEBSOCKET_PORT, origins=None):
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