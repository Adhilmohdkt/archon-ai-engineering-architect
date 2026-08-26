from typing import Literal
from pydantic import BaseModel

class SupervisorDecision(BaseModel):

    next_agent: Literal[
        "requirements",
        "technology",
        "critic",
        "finalizer",
        "human",
    ]
    reason: str