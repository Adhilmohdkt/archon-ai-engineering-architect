from app.llm import supervisor_model
from app.state import ArchonState
from langgraph.types import Command

def supervisor_node(state : ArchonState):
    prompt = f""" You are an supervisor of Archon  which is an AI engineering architecture system.

    Your job is to decide which aregent should work next based on the current state

    Current state:

    User goal:
    {state.user_goal}

    Requirements:
    {state.requirements}

    Architecture:
    {state.architecture}

    Technology recommendations:
    {state.technologyrecommendations}

    Critique:
    {state.critique}

    Revision count:
    {state.revision_count}

    Routing rules:
    - If requirements or architecture are missing, choose "requirements".
    - If requirements and architecture are complete but technology
    recommendations are missing, choose "technology".
    - If technology recommendations are complete and there is no critique,
    choose "critic".
    - If the critic rejected the design, choose the agent specified by
    critique.target_agent.
    - If the critic approved the design, choose "finalizer".
    - If the revision limit has been reached, choose "human".

    Return the appropriate next agent and a concise reason.
    """
    decision = supervisor_model.invoke(prompt)

    return Command(goto=decision.next_agent)

def requirements_node(state: ArchonState):
    print("Requirements Agent")
    return {}


def technology_node(state: ArchonState):
    print("Technology Agent")
    return {}


def critic_node(state: ArchonState):
    print("Critic Agent")
    return {}


def finalizer_node(state: ArchonState):
    print("Finalizer Agent")
    return {}


def human_node(state: ArchonState):
    print("Human intervention required")
    return {}