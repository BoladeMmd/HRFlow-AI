
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os

# Charger les variables du fichier .env
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("GROQ_MODEL")

if not api_key:
    raise ValueError("Clé API Groq introuvable dans le fichier .env")

# Initialiser le modèle Groq
llm = ChatGroq(
    model=model_name,
    api_key=api_key,
    temperature=0.2
)

# Envoyer un premier message
reponse = llm.invoke(
    "Tu es l'assistant RH de HRFlow AI. Présente-toi en une phrase."
)

print("\nRéponse de Groq :")
print(reponse.content)
