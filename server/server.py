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
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uvicorn
from threading import Thread

# Charger les variables d'environnement AVANT tout
load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.service import generate_response, system_instruction
from database.database import init_db, get_db
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

# --- Endpoints FastAPI (repris de database/routes.py) ---

@app.post("/utilisateurs/", response_model=schemas.Utilisateur, tags=["Utilisateurs"])
def create_utilisateur(utilisateur: schemas.UtilisateurCreate, db: Session = Depends(get_db)):
    """Crée un nouvel utilisateur."""
    db_utilisateur = crud.get_utilisateur_by_email(db, email=utilisateur.email)
    if db_utilisateur:
        raise HTTPException(status_code=400, detail="Cet email est déjà enregistré.")
    return crud.create_utilisateur(db=db, utilisateur=utilisateur)

@app.get("/utilisateurs/", response_model=List[schemas.Utilisateur], tags=["Utilisateurs"])
def read_utilisateurs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupère une liste de tous les utilisateurs."""
    utilisateurs = crud.get_utilisateurs(db, skip=skip, limit=limit)
    return utilisateurs

@app.get("/utilisateurs/{utilisateur_id}", response_model=schemas.Utilisateur, tags=["Utilisateurs"])
def read_utilisateur(utilisateur_id: int, db: Session = Depends(get_db)):
    """Récupère un utilisateur par son ID."""
    db_utilisateur = crud.get_utilisateur(db, utilisateur_id=utilisateur_id)
    if db_utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    return db_utilisateur

@app.put("/utilisateurs/{utilisateur_id}", response_model=schemas.Utilisateur, tags=["Utilisateurs"])
def update_utilisateur(utilisateur_id: int, utilisateur: schemas.UtilisateurUpdate, db: Session = Depends(get_db)):
    """Met à jour un utilisateur."""
    db_utilisateur = crud.update_utilisateur(db=db, utilisateur_id=utilisateur_id, utilisateur_data=utilisateur)
    if db_utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return db_utilisateur

@app.post("/ordonnances/{ordonnance_id}/medicaments/", response_model=schemas.Medicament, tags=["Médicaments"])
def create_medicament_pour_ordonnance(
    ordonnance_id: int, medicament: schemas.MedicamentCreate, db: Session = Depends(get_db)
):
    """Crée un nouveau médicament pour une ordonnance."""
    db_ordonnance = crud.get_ordonnance(db, ordonnance_id=ordonnance_id)
    if db_ordonnance is None:
        raise HTTPException(status_code=404, detail="Ordonnance non trouvée.")
    return crud.create_medicament_pour_ordonnance(db=db, medicament=medicament, ordonnance_id=ordonnance_id)

# --- Gestion WebSocket (code existant) ---

async def handle_client(websocket):
    """Gère les connexions client WebSocket."""
    client_id = id(websocket)
    # Initialiser l'historique. L'instruction système est maintenant passée au modèle, pas dans l'historique.
    conversations[client_id] = []
    
    try:
        print(f"Client {client_id} connecté")
        
        async for message in websocket:
            try:
                # Décoder le message JSON reçu du client
                data = json.loads(message)
                user_message = data.get("message", "")
                image_data_url = data.get("image")

                # Préparer le contenu pour l'utilisateur
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

                # Ajouter le message de l'utilisateur à l'historique
                if user_content:
                    conversations[client_id].append({"role": "user", "parts": user_content})

                # Générer la réponse en utilisant l'historique complet
                response = generate_response(conversations[client_id])
                
                # Stocker la réponse de l'assistant dans l'historique
                conversations[client_id].append({"role": "model", "parts": [response]})
                
                # Envoyer la réponse au client
                await websocket.send(json.dumps({"response": response}))
                
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"error": "Format JSON invalide"}))
            except Exception as e:
                print(f"Erreur lors du traitement du message: {str(e)}")
                await websocket.send(json.dumps({"error": "Une erreur est survenue"}))
    
    finally:
        # Nettoyer lors de la déconnexion du client
        if client_id in conversations:
            del conversations[client_id]
        print(f"Client {client_id} déconnecté")

async def start_websocket_server():
    """Démarre le serveur WebSocket."""
    async with websockets.serve(handle_client, HOST, WEBSOCKET_PORT, origins=None):
        print(f"🚀 Serveur WebSocket démarré sur {HOST}:{WEBSOCKET_PORT}")
        await asyncio.Future()  # run forever

def start_fastapi_server():
    """Démarre le serveur FastAPI."""
    uvicorn.run(app, host=HOST, port=FASTAPI_PORT, log_level="info")

async def main():
    """Démarre les deux serveurs."""
    try:
        # Initialiser la base de données
        print("🔧 Initialisation de la base de données...")
        init_db()
        print("✅ Base de données initialisée avec succès!")
        
        # Démarrer FastAPI dans un thread séparé
        fastapi_thread = Thread(target=start_fastapi_server, daemon=True)
        fastapi_thread.start()
        
        print(f"🚀 Serveur FastAPI démarré sur {HOST}:{FASTAPI_PORT}")
        print(f"📖 Documentation API disponible sur http://{HOST}:{FASTAPI_PORT}/docs")
        
        # Démarrer le serveur WebSocket
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