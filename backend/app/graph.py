from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import MemorySaver
from app.state import ArchonState
from app.agents import (supervisor_node,requirements_architecture_node,technology_node,critic_node,finalizer_node,human_node)
import asyncio
from langgraph.types import Command
graph = StateGraph(ArchonState)

graph.add_node('supervisor',supervisor_node,destinations=("requirements",
        "technology",
        "critic",
        "finalizer",
        "human",))

graph.add_node('requirements',requirements_architecture_node)
graph.add_node('technology',technology_node)
graph.add_node('critic',critic_node)
graph.add_node('finalizer',finalizer_node)
graph.add_node('human',human_node,destinations = ('requirements','technology',
                                                  'finalizer',END))

graph.add_edge(START,'supervisor')
graph.add_edge('finalizer',END)

checkpointer =  MemorySaver()

app = graph.compile(checkpointer=checkpointer)


if __name__ == "__main__":

    initial_state = ArchonState(
        user_goal="Build a simple personal expense tracker."
    )

    config = {
        "configurable": {
            "thread_id": "archon-test-1"
        }
    }

    # First run — graph will pause at human_node
    result = asyncio.run(
        app.ainvoke(
            initial_state,
            config=config
        )
    )

    print("Graph paused for human review")

    # Simulate the human's response
    human_response = Command(
        resume={
            "decision": "revise",
            "feedback": (
                "Add API operations for viewing, deleting, "
                "filtering, and summarizing expenses."
            )
        }
    )

    # Resume the same graph execution
    result = asyncio.run(
        app.ainvoke(
            human_response,
            config=config
        )
    )

    print(result)