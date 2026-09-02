from pydantic import BaseModel
from typing import Literal
from app.models import (TechnologyRecommendations,Critique,Requirements,Architecture)

#==================== Main State ==============================


class ArchonState(BaseModel):

    user_goal : str 
    requirements : Requirements | None = None
    architecture : Architecture  | None = None
    technologyrecommendations : TechnologyRecommendations | None = None
    critique : Critique | None = None
    revision_count : int = 0
    human_decision: str | None = None
    human_feedback : str | None = None
    final_blueprint : str | None = None

