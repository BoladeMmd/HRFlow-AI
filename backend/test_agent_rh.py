
from app.agents.agent_rh import interroger_agent

question = (
    "Analyse les absences approuvées par département. "
    "Présente les résultats et donne-moi une interprétation."
)

reponse = interroger_agent(question)

print("\n========== RÉPONSE DE HRFLOW AI ==========\n")
print(reponse)
