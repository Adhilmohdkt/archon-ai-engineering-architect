import uuid

from langgraph.types import Command

from app.API.schemas import ArchonResponse
from app import graph


class ArchonService:

    def _build_response(
        self,
        thread_id: str,
        graph_result: dict,
    ) -> ArchonResponse:

        if "__interrupt__" in graph_result:
            status = "human_review_required"

        elif (
            graph_result.get("final_blueprint")
            and graph_result.get("diagram")
        ):
            status = "completed"

        elif graph_result.get("final_blueprint"):
            status = "running"

        else:
            status = "running"

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

            diagram=(
                graph_result["diagram"].model_dump()
                if graph_result.get("diagram")
                else None
            ),
        )

    async def start(self, user_goal: str):

        thread_id = str(uuid.uuid4())

        return ArchonResponse(
            thread_id=thread_id,
            status="running",
            user_goal=user_goal,
        )

    async def run(
        self,
        thread_id: str,
        user_goal: str,
    ):

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        try:
            await graph.app.ainvoke(
                {
                    "user_goal": user_goal
                },
                config=config,
            )

        except Exception as e:
            print(
                f"Archon run failed for {thread_id}: {e}"
            )

    async def resume(
        self,
        thread_id: str,
        decision: str,
        feedback: str | None = None,
    ):

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        human_response = Command(
            resume={
                "decision": decision,
                "feedback": feedback,
            }
        )

        result = await graph.app.ainvoke(
            human_response,
            config=config,
        )

        return self._build_response(
            thread_id,
            result,
        )

    async def get_run(self, thread_id: str):

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        snapshot = await graph.app.aget_state(
            config
        )

        if not snapshot.values:
            return None

        graph_result = snapshot.values

        if "human" in snapshot.next:
            status = "human_review_required"

        elif (
            graph_result.get("final_blueprint")
            and graph_result.get("diagram")
        ):
            status = "completed"

        elif graph_result.get("final_blueprint"):
            status = "running"

        else:
            status = "running"

        response = self._build_response(
            thread_id,
            graph_result,
        )

        response.status = status

        return response