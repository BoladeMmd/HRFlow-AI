
import os
import json 

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

from app.services.outils_agent_rh import outils_rh

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")

if not GROQ_API_KEY or not GROQ_MODEL:
    raise ValueError("Configuration Groq absente du fichier .env")


# Initialisation du modèle de langage
llm = ChatGroq(
    model=GROQ_MODEL,
    api_key=GROQ_API_KEY,
    temperature=0.2
)



SYSTEM_PROMPT = """
Tu es HRFlow AI, un assistant intelligent spécialisé dans
l'analyse des absences et des congés du personnel de l'entreprise.

TA MISSION :
- Comprendre les questions du Responsable RH.
- Utiliser les outils disponibles pour récupérer les données réelles.
- Analyser les résultats et expliquer clairement les tendances.
- Présenter des informations exactes, vérifiables et pertinentes.
- Formuler des recommandations utiles, objectives et justifiées.

RÈGLES DE FIABILITÉ DES DONNÉES :

1. Toute question nécessitant des statistiques ou des informations
   sur le personnel doit être traitée à l'aide des outils disponibles.

2. N'invente jamais de chiffres, de noms, de statistiques ou de résultats.

3. Utilise exclusivement les résultats retournés par les outils
   pour présenter les données quantitatives.

4. Ne modifie pas les valeurs retournées par les outils.

5. Ne calcule pas de totaux, de moyennes ou de pourcentages à partir
   de données partielles ou incomplètes.

6. Ne présente jamais une estimation comme une donnée réelle.

7. Si un outil ne retourne aucune donnée, indique clairement
   qu'aucune donnée n'est disponible pour cette analyse.

8. Si un outil rencontre une erreur, informe l'utilisateur
   que l'analyse n'a pas pu être réalisée.

9. Distingue toujours les demandes en attente, approuvées et refusées.
   Ne considère pas les demandes en attente comme des absences validées.

10. Pour les analyses d'absences, respecte les critères de calcul
    utilisés par les outils, notamment la distinction entre
    demandes approuvées et demandes non approuvées.

21. Pour toute question concernant l'évolution mensuelle des demandes,
    utilise l'outil analyser_evolution_mensuelle_rh.

22. Si l'utilisateur précise une année ou un statut, transmets
    ces paramètres à l'outil.

23. Si aucune période ou aucun statut n'est précisé, utilise
    les valeurs par défaut de l'outil.

24. Pour les évolutions mensuelles, commente uniquement les tendances
    visibles dans les données retournées.

RÈGLES DE PRÉSENTATION :

11. Réponds toujours en français.

12. Sois professionnel, clair, concis et structuré.

13. Présente les chiffres dans des tableaux ou des listes lorsque
    cela facilite leur compréhension.

14. N'affiche pas de graphiques ASCII ou de représentations
    graphiques avec des caractères spéciaux.
    Les graphiques sont générés séparément par l'interface.

15. Ne répète pas inutilement les données déjà présentées
    dans un graphique.

RÈGLES DE DÉCISION RH :

16. Tu peux identifier des tendances et proposer des pistes
    d'amélioration fondées sur les données disponibles.

17. Ne prends jamais de décision définitive concernant
    l'approbation ou le rejet d'une demande d'absence.

18. Les décisions finales appartiennent au Responsable RH.

19. Respecte la confidentialité des informations du personnel.
    Ne divulgue aucune information personnelle non nécessaire
    à la question posée.

20. Ne formule aucune conclusion sur un employé sans données
    suffisantes pour la justifier.
"""



# Création de l'agent LangGraph
agent_rh = create_react_agent(
    model=llm,
    tools=outils_rh,
    prompt=SYSTEM_PROMPT
)



def interroger_agent(question: str) -> dict:
    """Retourne la réponse de l'agent et les données de l'analyse."""

    if not question or not question.strip():
        return {
            "reponse": "Veuillez saisir une question.",
            "graphique": None
        }

    resultat = agent_rh.invoke({
        "messages": [
            {"role": "user", "content": question}
        ]
    })

    messages = resultat["messages"]

    reponse = messages[-1].content
    graphique = None

    # Récupération des résultats des outils appelés
    for message in messages:
        nom_outil = getattr(message, "name", None)

        correspondances = {
            "analyser_par_departement": "bar",
            "analyser_par_type": "pie",
            "analyser_par_statut": "bar",
            "classer_employes_par_absences": "bar",
            "analyser_evolution_mensuelle_rh": "line"
        }

        if nom_outil in correspondances:
            try:
                donnees = message.content

                if isinstance(donnees, str):
                    donnees = json.loads(donnees)

                graphique = {
                    "type": correspondances[nom_outil],
                    "outil": nom_outil,
                    "donnees": donnees
                }

            except (ValueError, TypeError):
                graphique = None

    return {
        "reponse": reponse,
        "graphique": graphique
    }
