from app.llm import (supervisor_model,requirements_architecture_model,technologyrecommendations_model,cloudfare_model)
from app.state import ArchonState
from langgraph.types import Command
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from mcp_server.mcp_tools import get_mcp_tools
import asyncio

def supervisor_node(state: ArchonState):
    prompt = f"""
You are the Supervisor of Archon, an AI engineering architecture system.

Your job is to decide which agent should work next based on the current state.

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

1. If requirements or architecture are missing, choose "requirements".

2. If requirements and architecture are complete but
   technology recommendations are missing, choose "technology".

3. If requirements, architecture, and technology recommendations
   are complete and there is no critique, choose "critic".

4. If the critic rejected the design, choose the agent specified by
   critique.target_agent.

5. If the critic approved the design, choose "finalizer".

6. If the revision limit has been reached, choose "human".


Return ONLY a valid JSON object containing:

- next_agent
- reason

The next_agent value MUST be exactly one of:
"requirements", "technology", "critic", "finalizer", "human".

Choose the next_agent dynamically based on the current state and
the routing rules. Do not always choose the same agent.
"""

    

    decision = supervisor_model.invoke(prompt)

    return Command(
        goto=decision.next_agent
    )

def requirements_architecture_node(state: ArchonState):
    
    prompt = f"""
        You are Archon's Requirements and Architecture Agent.

        The user's goal is:

        {state.user_goal}

        Your job is to:

        1. Identify the functional requirements.
        2. Identify the non-functional requirements.
        3. Identify the constraints.
        4. Design an appropriate software architecture based on those requirements,
        including the major components and how data flows between them.
        5. Explain why the proposed architecture is appropriate.
        Important:
        - Do not blindly assume unnecessary features.
        - Keep the architecture proportional to the user's goal.
        - If important information is missing, make reasonable assumptions.
        - Ensure the architecture addresses the identified requirements and constraints.
        - Return the result using the provided structured output schema.
        """
    
    result = requirements_architecture_model.invoke(prompt)
   
    return Command(update={
        "requirements": result.requirements,
        "architecture": result.architecture,
    },goto = 'supervisor')



async def technology_node(state: ArchonState):
    print("START: Technology")

    # Load MCP tools
    tools = await get_mcp_tools()

    # Give the tools to Gemma
    model_with_tools = cloudfare_model.bind_tools(tools)

    prompt = f"""
    You are Archon's Technology Recommendation Agent.

    The user's goal is:

    {state.user_goal}

    The identified requirements are:

    {state.requirements}

    The proposed architecture is:

    {state.architecture}

    Your job is to recommend appropriate technologies for this system.

    Consider:
    - The functional requirements
    - The non-functional requirements
    - The constraints
    - The proposed architecture
    - Cost and operational complexity
    - Scalability and maintainability
    - Suitable alternatives and their trade-offs

    Before making your technology recommendations, you MUST
    use the websearch tool to research current technology options
    and trade-offs.

    You must perform at least one web search before producing
    your recommendations.

    Do not recommend technologies simply because they are popular.
    Choose technologies that are appropriate for this specific system.
    """

    messages = [HumanMessage(content=prompt)]

    # Ask the LLM whether it needs to use a tool
    response = await model_with_tools.ainvoke(messages)
    

    # If the LLM requested a tool, execute it
    if response.tool_calls:

        tool_node = ToolNode(tools)

        messages.append(response)

        tool_result = await tool_node.ainvoke({
            "messages": messages
        })

        messages.extend(tool_result["messages"])

        # Give the search results back to the LLM
        response = await model_with_tools.ainvoke(messages)
        

    # Convert the final response into our structured schema
    result = await technologyrecommendations_model.ainvoke(
        messages
    )

    print("Technology recommendations generated")

    return Command(
        update={
            "technologyrecommendations": result
        },
        goto="supervisor",
    )


def critic_node(state: ArchonState):
    print("Critic Agent")
    return {}


def finalizer_node(state: ArchonState):
    print("Finalizer Agent")
    return {}


def human_node(state: ArchonState):
    print("Human intervention required")
    return {}