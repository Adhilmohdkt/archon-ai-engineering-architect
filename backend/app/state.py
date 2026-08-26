from pydantic import BaseModel
from typing import Literal

class Requirements(BaseModel):

    functional_requirements : list[str]
    non_functional_requirements : list[str]
    constraints : list[str]

class Architecture(BaseModel):

    architecture_style : str 
    components : list[str]
    data_flow : list[str]
    reason : str

class TechnologyRecommendations(BaseModel):
    recommendations: dict[str, str]
    alternatives: dict[str, list[str]]
    trade_offs: dict[str, str]
    reason: str

class Critique(BaseModel):
    approved : bool
    issues : list[str]
    target_agent: Literal["requirements", "technology"] | None
    revision_required : bool

#==================== Main State ==============================


class ArchonState(BaseModel):

    user_goal : str 
    requirements : Requirements | None = None
    architecture : Architecture  | None = None
    technologyrecommendations : TechnologyRecommendations | None = None
    critique : Critique | None = None
    revision_count : int = 0
    final_blueprint : str | None = None

