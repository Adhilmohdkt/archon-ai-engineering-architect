from langgraph.graph import StateGraph,START,END
from app.state import Requirements,ArchonState

def requirements_node(state: ArchonState):
    requirements = Requirements(
        functional_requirements=["Answer customer questions"],
        non_functional_requirements=["Low latency"],
        constraints=["Limited budget"],
    )

    return {"requirements": requirements}

graph = StateGraph(ArchonState)

graph.add_node("requirements", requirements_node)

graph.add_edge(START, "requirements")
graph.add_edge("requirements", END)

app = graph.compile()

if __name__ == "__main__":
    initial_state = ArchonState(
        user_goal="Build an AI customer-support system"
    )

    result = app.invoke(initial_state)

    print(result)
 