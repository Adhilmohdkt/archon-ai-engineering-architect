from langgraph.graph import StateGraph,START,END
from app.state import ArchonState
from app.agents import (supervisor_node,requirements_architecture_node,technology_node,critic_node,finalizer_node,human_node)
import asyncio
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
graph.add_node('human',human_node)

graph.add_edge(START,'supervisor')
graph.add_edge('finalizer',END)


app = graph.compile()


if __name__ == '__main__':
    initial_state = ArchonState(user_goal='Build AN AI customer care system')

    result = asyncio.run(app.ainvoke(initial_state))
    print(result)