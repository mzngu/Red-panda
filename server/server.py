import asyncio
import json
import websockets
import sys
import os
import base64
from io import BytesIO
from PIL import Image

# Add the parent directory to the Python path to allow sibling imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.service import generate_response, system_instruction

# Configuration du serveur WebSocket
HOST = "localhost"
PORT = 8000

# Stockage des conversations par client
conversations = {}

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

async def main():
    """Démarre le serveur WebSocket."""
    # Allow all origins for development purposes
    async with websockets.serve(handle_client, HOST, PORT, origins=None):
        print(f"Serveur WebSocket démarré sur {HOST}:{PORT}")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Serveur arrêté")