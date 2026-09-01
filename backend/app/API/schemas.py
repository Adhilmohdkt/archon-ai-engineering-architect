from pydantic import BaseModel,Field
from typing import Literal,Any



class  ArchonRequest(BaseModel):
    user_goal : str = Field(...,
                            min_length=1,
                            description = 'The users goal for the system')


class HumanResumeRequest(BaseModel):

    decision : Literal['approve','revise','reject']
    feedback : str | None


class ArchonResponse(BaseModel):

    thread_id : str
    status : Literal['running',
                     '"human_review_required"',
                     'rejected',
                     'completed']
    user_goal: str | None = None

    requirements: Any | None = None
    architecture: Any | None = None
    technologyrecommendations: Any | None = None
    critique: Any | None = None

    human_feedback: str | None = None

    final_blueprint: str | None = None

