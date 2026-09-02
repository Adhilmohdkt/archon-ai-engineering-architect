import uuid

from langgraph.types import Command
from app.API.schemas import ArchonResponse

from app.graph import app


class ArchonService:

    def _build_response(self,thread_id: str,graph_result: dict) -> ArchonResponse:

         if "__interrupt__" in graph_result:
            status = "human_review_required"
         else:
            status = "completed"

         return ArchonResponse(
            thread_id=thread_id,
            status=status,
            user_goal=graph_result.get("user_goal"),

            requirements=(
                graph_result["requirements"].model_dump()
                if graph_result.get("requirements")
                else None
            ),

            architecture=(
                graph_result["architecture"].model_dump()
                if graph_result.get("architecture")
                else None
            ),

            technologyrecommendations=(
                graph_result["technologyrecommendations"].model_dump()
                if graph_result.get("technologyrecommendations")
                else None
            ),

            critique=(
                graph_result["critique"].model_dump()
                if graph_result.get("critique")
                else None
            ),

            human_feedback=graph_result.get("human_feedback"),
            final_blueprint=graph_result.get("final_blueprint"),
        )

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

        return self._build_response(
            thread_id,
            result
        )


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

        return self._build_response(thread_id, result)