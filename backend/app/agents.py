from app.llm import (supervisor_model,requirements_architecture_model,technologyrecommendations_model,
                     cloudfare_model,critic_model,groq_model)
from app.state import ArchonState
from langgraph.types import Command
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from mcp_server.mcp_tools import get_mcp_tools
import asyncio
MAX_REVISION = 3

def supervisor_node(state: ArchonState):
    print(" starting supervisor")

    if state.revision_count >= MAX_REVISION:
        print('Human intervention needed ')
        return Command(goto='human')
    
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

    Return ONLY a valid JSON object containing:

    - next_agent
    - reason

    The next_agent value MUST be exactly one of:
    "requirements", "technology", "critic", "finalizer", "human".

    Choose the next_agent dynamically based on the current state.
    """

    decision = supervisor_model.invoke(prompt)

    print("Supervisor finished")

    return Command(
        goto=decision.next_agent
    )

def requirements_architecture_node(state: ArchonState):

    print("Starting requirements agent")

    prompt = f"""
You are Archon's Requirements and Architecture Agent.

User goal:
{state.user_goal}

Previous requirements:
{state.requirements}

Previous architecture:
{state.architecture}

Critic feedback:
{state.critique}

Your task is to produce the requirements and architecture for the
user's specific goal.

If Critic feedback is present, revise the previous design by
addressing the issues identified by the Critic.

If Critic feedback is None, create the initial design.

Identify:

1. Functional requirements
2. Non-functional requirements
3. Constraints
4. Appropriate architecture style
5. Major architecture components
6. Data flow between the components
7. A clear reason explaining why the proposed architecture is appropriate
   for the user's requirements and constraints.

The architecture output MUST contain all four fields:
- architecture_style
- components
- data_flow
- reason

Important:

- Derive requirements from the user's specific goal.
- Do not assume requirements from a previous example or domain.
- Do not introduce unnecessary components.
- Keep the architecture proportional to the user's goal.
- Ensure the architecture addresses the identified requirements
  and constraints.
- Ensure every major component has a purpose.
- Ensure the data flow actually uses the proposed components.
- If Critic feedback is present, address all relevant issues.
- Preserve valid parts of the previous design when appropriate.

Return a complete result using the provided structured output schema.
Make sure every required field in the schema is populated.
"""

    result = requirements_architecture_model.invoke(prompt)

    print("Finished Requirements agent")
   
    return Command(update={
        "requirements": result.requirements,
        "architecture": result.architecture,
        'critique':None
    },goto = 'supervisor')



async def technology_node(state: ArchonState):

    print("START: Technology")

    tools = await get_mcp_tools()

    model_with_tools = cloudfare_model.bind_tools(tools)

    prompt = f"""
You are Archon's Technology Recommendation Agent.

The user's goal is:

{state.user_goal}

The identified requirements are:

{state.requirements}

The proposed architecture is:

{state.architecture}

Current technology recommendations:

{state.technologyrecommendations}

Critic feedback from the previous iteration:

{state.critique}


Your job is to recommend appropriate technologies for this system.

Consider:

- The functional requirements
- The non-functional requirements
- The constraints
- The proposed architecture
- Cost and operational complexity
- Scalability and maintainability
- Security and compliance
- Suitable alternatives and their trade-offs


Revision handling:

If Critic feedback is provided, this is a revision of the
previous technology recommendations.

Carefully analyze the Critic's feedback and address the issues
identified by the Critic.

Preserve valid technology choices where appropriate.
Do not replace technologies unnecessarily.

If no Critic feedback is provided, this is the initial technology
recommendation.


Web research:

Before making technology recommendations, you MUST use the
websearch tool to research current technology options,
capabilities, limitations, or trade-offs.

You must perform at least one web search before producing
your recommendations.

Do not recommend technologies simply because they are popular.

Choose technologies based on the specific requirements,
architecture, constraints, and current information.
"""

    messages = [HumanMessage(content=prompt)]

    response = await model_with_tools.ainvoke(messages)

    if response.tool_calls:

        tool_node = ToolNode(tools)

        messages.append(response)

        tool_result = await tool_node.ainvoke({
            "messages": messages
        })

        messages.extend(tool_result["messages"])

        # Give the search results back to the LLM
        response = await model_with_tools.ainvoke(messages)

    # Convert only the final technology response into our schema
    structured_prompt = f"""
Convert the following technology recommendation into the
TechnologyRecommendations schema.

User goal:
{state.user_goal}

Requirements:
{state.requirements}

Architecture:
{state.architecture}

Critic feedback:
{state.critique}

Technology recommendation produced after research:
{response.content}

Make sure ALL required fields are populated:

- recommendations
- alternatives
- trade_offs
- reason

The recommendations must be appropriate for the user's specific
requirements and architecture.

If Critic feedback is present, ensure the revised recommendations
address the relevant issues identified by the Critic.

Return the complete structured result.
"""

    result = await technologyrecommendations_model.ainvoke(
        structured_prompt
    )

    print("Technology recommendations generated")

    return Command(
        update={
            "technologyrecommendations": result,
            "critique": None
        },
        goto="supervisor",
    )

def critic_node(state: ArchonState):

    print("Critic Agent")

    prompt = f"""
You are Archon's Critic Agent.

Your job is to evaluate whether the proposed system design
adequately satisfies the user's specific goal.

User goal:
{state.user_goal}

Requirements:
{state.requirements}

Architecture:
{state.architecture}

Technology recommendations:
{state.technologyrecommendations}


Before deciding whether to approve the design, perform the following
verification checks.

1. FUNCTIONAL REQUIREMENT COVERAGE

For each important functional requirement:

- Identify whether the architecture provides a component,
  mechanism, or workflow that satisfies it.
- Identify any important requirement that is not actually supported.

Do not consider a requirement satisfied merely because it is
mentioned. Verify that the architecture and data flow actually
support it.


2. NON-FUNCTIONAL REQUIREMENT COVERAGE

Check the identified non-functional requirements such as:

- latency
- availability
- scalability
- security
- privacy
- reliability
- maintainability
- cost

Only evaluate requirements that are actually relevant to this
specific system.

Identify significant gaps that could prevent the system from
meeting its stated requirements.


3. CONSTRAINT VERIFICATION

Check every stated constraint.

Verify that the architecture and technology choices respect
those constraints.

Do not invent additional constraints.


4. ARCHITECTURE CONSISTENCY

Check:

- Are the major components appropriate?
- Does every important component have a clear responsibility?
- Are any essential components missing?
- Are unnecessary components introducing excessive complexity?
- Does the data flow actually use the proposed components?
- Are there contradictions between components and the data flow?


5. TECHNOLOGY VERIFICATION

Check whether the recommended technologies:

- fit the architecture
- satisfy the requirements
- respect the constraints
- are technically appropriate for their assigned responsibilities

Do not reject a technology simply because another technology
could also be used.

Only identify a technology issue when the choice creates a
meaningful problem for the proposed system.


6. CROSS-LAYER CONSISTENCY

Verify that:

Requirements
      ↓
Architecture
      ↓
Technology

form one coherent design.

Look specifically for cases where:

- a requirement exists but has no architectural support
- an architectural component has no corresponding purpose
- a technology does not support the component it was selected for
- the data flow contradicts the architecture
- an important constraint is ignored


IMPORTANT APPROVAL RULES:

- Evaluate against THIS user's goal and identified requirements.
- Do not compare the design against an ideal or perfect production
  architecture.
- Do not reject the design merely because optional improvements
  are possible.
- Do not introduce requirements that were not identified or
  reasonably implied by the user's goal.
- Minor omissions should not cause rejection.
- Only reject when there is a significant issue that affects the
  correctness, feasibility, requirements coverage, or consistency
  of the design.


After completing all checks, decide whether a revision is actually
necessary.

If the design adequately satisfies the important requirements
and constraints:

approved = true
revision_required = false
target_agent = null
issues = []

If the design has one or more significant problems:

approved = false
revision_required = true

issues must clearly explain the specific problems.

target_agent must identify the agent primarily responsible for
fixing the problem:

"requirements"
or
"technology"


IMPORTANT:

Do not create an issue just to appear critical.

The goal is to detect real problems, not to maximize the number
of issues.

Return the result using the provided structured output schema.
"""

    result = critic_model.invoke(prompt)

    print("Critique generated")

    if result.revision_required:

        return Command(
            update={
                "critique": result,
                "revision_count": state.revision_count + 1,
            },
            goto="supervisor",
        )

    return Command(
        update={
            "critique": result,
        },
        goto="supervisor",
    )

def finalizer_node(state: ArchonState):

    print("Finalizer Agent")

    prompt = f"""
You are Archon's Finalizer Agent.

The proposed system design has passed the Critic's evaluation.

Your job is to produce the final software architecture blueprint
by consolidating the decisions made by the previous agents.

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


Create a clear, professional, implementation-oriented final blueprint.

The blueprint should include:

1. System overview
2. Requirements summary
3. Architecture and major components
4. Technology stack
5. End-to-end data flow
6. Security and compliance considerations
7. Scalability and reliability considerations
8. Important implementation considerations
9. Assumptions or open decisions, if any


IMPORTANT:

- The Requirements, Architecture, and Technology recommendations
  are the source of truth.
- Consolidate the decisions made by the previous agents.
- Do not introduce new requirements.
- Do not introduce major technologies that were not recommended.
- Do not introduce major architectural components that were not
  part of the approved architecture.
- Do not change the architecture or technology choices.
- Do not invent specific implementation details that were not
  established by the previous agents.
- If an important detail is missing, clearly label it as an
  assumption or open decision.
- Ensure the data flow is consistent with the architecture.
- Ensure the technology stack is consistent with the architecture.
- Keep the final blueprint proportional to the user's goal.
- Do not perform another critique or revision.


Write the final blueprint in clear Markdown.
"""

    result = groq_model.invoke(prompt)

    print("Final Blueprint generated")

    return {
        "final_blueprint": result.content
    }


def human_node(state: ArchonState):
    print("Human intervention required")
    return {}