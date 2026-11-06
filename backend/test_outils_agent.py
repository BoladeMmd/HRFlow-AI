
from app.services.outils_agent_rh import outils_rh

for outil in outils_rh:
    print(f"- {outil.name} : {outil.description}")
