
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.routes.auth import require_roles
from app.agents.agent_rh import interroger_agent


router = APIRouter(
    prefix="/assistant-rh",
    tags=["Assistant IA RH"]
)


class QuestionAgent(BaseModel):
    question: str = Field(
        min_length=2,
        max_length=2000,
        description="Question posée à l'assistant RH"
    )


class ReponseAgent(BaseModel):
    reponse: str
    graphique: dict | None = None

@router.post("/question", response_model=ReponseAgent)
def poser_question(
    donnees: QuestionAgent,
    utilisateur=Depends(require_roles("responsable"))
):
    try:
        reponse = interroger_agent(donnees.question)

        return reponse

    except Exception as e:
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Une erreur est survenue lors du traitement de la question."
        )
