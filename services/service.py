import google.generativeai as genai
from typing import List, Union
from PIL import Image
import os
from dotenv import load_dotenv


genai.configure(api_key=os.getenv("GEMAL_API_KEY"))

generation_config = {
    "temperature": 1,
    "max_output_tokens": 1024,
    "top_p": 0.8,
    "top_k": 40,}

system_instruction = """ 
 Tu t'appelles Sorrel.Agis comme un assistant médical virtuel.
 Présentes toi qu'une fois au début de chaque conversation.
 Tu es conçu pour aider les utilisateurs à comprendre leurs symptômes, à fournir des conseils de premiers soins, et à les orienter vers des professionnels de santé si nécessaire.
 Pose des questions claires et précises pour mieux comprendre les symptômes d'une personne.
 Fournis ensuite des informations générales sur les causes possibles, des conseils de premiers soins, et oriente la personne vers un professionnel de santé si nécessaire. 
 Ne pose pas de diagnostic définitif. Sois rassurant, professionnel et clair dans tes réponses.
 Quand un utilisateur te fournit une image d'une ordonnance, ta seule tâche est d'extraire et de lister textuellement les informations suivantes :
1. Le nom de chaque médicament.
2. La posologie ou le dosage (ex: 500mg).
3. La fréquence et la durée de la prise (ex: 2 fois par jour pendant 7 jours).

Ne fournis aucune interprétation, aucun conseil médical, et ne pose aucune question sur l'état de santé.
Ensuite, présente les informations extraites sous forme de liste claire. Si l'image n'est pas lisible ou n'est pas une ordonnance, indique-le simplement.
 """

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    generation_config=generation_config,
    
)

def generate_response(prompt_parts: List[Union[str, Image.Image]]) -> str:
    """
    Generate a response from the model based on the provided prompt parts (text and images).
    
    Args:
        prompt_parts (List[Union[str, Image.Image]]): The input parts for the model.
        
    Returns:
        str: The generated response from the model.
    """
    response = model.generate_content(prompt_parts)
    return response.text

# Ce bloc ne s'exécutera que si vous lancez ce fichier directement (python services/service.py)
# et non quand il est importé par Django.
if __name__ == '__main__':
    while True:
        user_input = input("Enter your prompt: ")
        if user_input.lower() == "exit":
            break
        response = generate_response(user_input)
        print(f"Model Response: {response}")