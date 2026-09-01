import uuid

from langgraph.types import Command

from app.graph import app


class ArchonService:

    async def start(self, user_goal: str):

        thread_id = str(uuid.uuid4())

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        result = await app.ainvoke(
            {
                "user_goal": user_goal
            },
            config=config
        )

        if "__interrupt__" in result:
            status = "human_review_required"
        else:
            status = "completed"

        return {
            "thread_id": thread_id,
            "status": status,
            "result": result
        }


    async def resume(
        self,
        thread_id: str,
        decision: str,
        feedback: str | None = None
    ):

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        human_response = Command(
            resume={
                "decision": decision,
                "feedback": feedback
            }
        )

        result = await app.ainvoke(
            human_response,
            config=config
        )

        return result