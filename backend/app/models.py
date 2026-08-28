from typing import Literal
from pydantic import BaseModel


# ------------------------- Requirements --------------------

class Requirements(BaseModel):
    functional_requirements: list[str]
    non_functional_requirements: list[str]
    constraints: list[str]


# ------------------------- Architecture --------------------

class Architecture(BaseModel):
    architecture_style: str
    components: list[str]
    data_flow: list[str]
    reason: str


# ------------------------- Supervisor --------------------

class SupervisorDecision(BaseModel):

    next_agent: Literal[
        "requirements",
        "technology",
        "critic",
        "finalizer",
        "human",
    ]

    reason: str


# ------------------------- Requirements + Architecture --------------------

class RequirementsArchitectureOutput(BaseModel):
    requirements: Requirements
    architecture: Architecture


# ------------------------- Technology --------------------

class TechnologyRecommendations(BaseModel):
    recommendations: dict[str, str]
    alternatives: dict[str, list[str]]
    trade_offs: dict[str, str]
    reason: str


# ------------------------- Critic --------------------

class Critique(BaseModel):
    approved: bool
    issues: list[str]
    target_agent: Literal["requirements", "technology"] | None
    revision_required: bool