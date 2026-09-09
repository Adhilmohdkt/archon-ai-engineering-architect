from app.llm import (supervisor_model,requirements_architecture_model,technologyrecommendations_model,
                     cloudfare_model,critic_model,groq_model,groq_tool_model,groq_structured_model,groq_diagram_model)
from app.state import ArchonState
from app.models import Critique, ArchitectureDiagram
from langgraph.types import (Command,interrupt)
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from mcp_server.mcp_tools import get_mcp_tools
from langgraph.graph import END
import asyncio
MAX_REVISION = 3

def supervisor_node(state: ArchonState):
    print("Starting supervisor")

   
    if state.requirements is None or state.architecture is None:
        print("Routing to requirements agent")
        return Command(goto="requirements")

    
    if state.technologyrecommendations is None:
        print("Routing to technology agent")
        return Command(goto="technology")

    # 3. Everything exists, but critic hasn't evaluated it yet
    if state.critique is None:
        print("Routing to critic")
        return Command(goto="critic")

    
    if state.critique.approved:
        print("Design approved → finalizer")
        return Command(goto="finalizer")

    
    if state.critique.revision_required:

       
        if state.revision_count >= MAX_REVISION:
            print("Revision limit reached → human intervention")
            return Command(goto="human")

        
        print(
            f"Revision allowed → {state.critique.target_agent}"
        )

        return Command(
            update={
                "revision_count": state.revision_count + 1
            },
            goto=state.critique.target_agent
        )

    
    print("Unexpected supervisor state → human intervention")
    return Command(goto="human")

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

Human feedback:
{state.human_feedback}


Your task is to produce the requirements and architecture for the
user's specific goal.

If Critic feedback is present, revise the previous design by
addressing the issues identified by the Critic.

If Human feedback is present, treat it as additional guidance
provided by a human reviewer.

The human may provide:
- A new requirement
- A clarification
- An architectural preference
- A constraint
- A concern about the existing design
- A suggestion for changing or improving the architecture

Carefully evaluate the human's feedback against the user's goal,
requirements, constraints, architecture, and Critic feedback.

Do not blindly accept the human's suggestion.

If the suggestion is appropriate and consistent with the system's
goals and constraints, incorporate it into the revised design.

If the suggestion conflicts with the requirements, constraints,
or technical consistency of the system, use your reasoning to
determine the appropriate approach.

If Critic feedback is None, create the initial design.

If Human feedback is None, continue normally without human guidance.


Identify:

1. Functional requirements
2. Non-functional requirements
3. Constraints
4. Appropriate architecture style
5. Major architecture components
6. Data flow between the components
7. A clear reason explaining why the proposed architecture is
   appropriate for the user's requirements and constraints.


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
- If Human feedback is present, address relevant human guidance.
- Preserve valid parts of the previous design when appropriate.
- Do not make unnecessary changes to a working design.

Return a complete result using the provided structured output schema.
Make sure every required field in the schema is populated.
"""

    result = requirements_architecture_model.invoke(prompt)

    print("Finished Requirements agent")

    return Command(
        update={
            "requirements": result.requirements,
            "architecture": result.architecture,
            "critique": None,
        },
        goto="supervisor"
    )


async def technology_node(state: ArchonState):

    print("START: Technology")

    tools = await get_mcp_tools()
    model_with_tools = groq_tool_model.bind_tools(tools)

    # Build only the context that is relevant to this run.
    context_parts = [
        f"User goal:\n{state.user_goal}",
        f"Requirements:\n{state.requirements}",
        f"Architecture:\n{state.architecture}",
    ]

    if state.technologyrecommendations:
        context_parts.append(
            f"Current technology recommendations:\n"
            f"{state.technologyrecommendations}"
        )

    if state.critique:
        context_parts.append(
            f"Critic feedback:\n{state.critique}"
        )

    if state.human_feedback:
        context_parts.append(
            f"Human feedback:\n{state.human_feedback}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are Archon's Technology Recommendation Agent.

{context}

Your task is to research and recommend technologies that best fit
the requirements and proposed architecture.

Evaluate:
- functional and non-functional requirements
- constraints
- cost and operational complexity
- scalability and maintainability
- security and compliance
- alternatives and important trade-offs

Revision rules:
- If critic feedback exists, address it.
- Preserve valid existing choices unless there is a reason to change them.
- If human feedback exists, evaluate it technically rather than
  accepting it blindly.
- Change only what is necessary during a revision.

Web research:
You MUST use the available web/MCP search tool before making
recommendations. Use current information about technologies,
capabilities, limitations, pricing, or trade-offs.

Keep the final analysis concise.
Focus on technology decisions and evidence needed to justify them.
Do not write a long general explanation.
"""

    messages = [HumanMessage(content=prompt)]

    response = await model_with_tools.ainvoke(messages)

    # Execute MCP/web tools when requested by the model.
    if response.tool_calls:

        tool_node = ToolNode(tools)

        messages.append(response)

        tool_result = await tool_node.ainvoke(
            {
                "messages": messages
            }
        )

        messages.extend(tool_result["messages"])

        # Produce the final research analysis using the tool results.
        response = await model_with_tools.ainvoke(messages)

    # Only the research result is needed by the formatter.
    structured_prompt = f"""
Convert the following technology research into the
TechnologyRecommendations schema.

Technology research:
{response.content}

Requirements for the output:

- recommendations: technology choices for the major architecture
  components.
- alternatives: provide up to 2 relevant alternatives for each
  important choice.
- trade_offs: give one concise sentence for each important trade-off.
- reason: give a concise overall justification in no more than
  3 sentences.
- Include all four fields.
- Do not invent technologies that are unsupported by the research,
  requirements, or architecture.

Return ONLY the structured TechnologyRecommendations object.
"""

    try:
     result = await technologyrecommendations_model.ainvoke(
            structured_prompt
        )
    except Exception as e:
        print("=== TECHNOLOGY FORMATTER FAILED ===")
        print(type(e).__name__)
        print(str(e))
        raise

    print("Technology recommendations generated")

    return Command(
        update={
            "technologyrecommendations": result,
            "critique": None,
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

Human feedback:
{state.human_feedback}


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


7. HUMAN FEEDBACK VERIFICATION

Human feedback:
{state.human_feedback}

If human feedback is None:

- No human intervention has occurred.
- Do not perform any human-feedback-specific evaluation.

If human feedback is present:

- Identify the specific change, preference, or concern requested
  by the human.
- Check whether the revised Requirements, Architecture, or
  Technology recommendations actually address that feedback.
- Check whether the requested change was implemented correctly.
- Check whether the change remains consistent with the user's
  requirements, constraints, and overall architecture.
- Do not automatically approve the design simply because it
  follows the human's request.
- Do not reject the design merely because the human's preferred
  technology differs from your own preference.
- If the human feedback has been properly addressed and the
  resulting design remains technically sound, consider the
  human feedback satisfied.
- If the human feedback was ignored, partially addressed,
  incorrectly implemented, or introduces a significant
  contradiction, create an issue describing the problem.

When human feedback is present, the Critic must explicitly verify
that the revised design reflects the human's requested change.


IMPORTANT APPROVAL RULES:

- Evaluate against THIS user's goal and identified requirements.
- Consider human feedback when it is present.
- Do not compare the design against an ideal or perfect production
  architecture.
- Do not reject the design merely because optional improvements
  are possible.
- Do not introduce requirements that were not identified or
  reasonably implied by the user's goal.
- Minor omissions should not cause rejection.
- Only reject when there is a significant issue that affects the
  correctness, feasibility, requirements coverage, consistency,
  or requested human change.
- Do not create an issue just to appear critical.
- The goal is to detect real problems, not to maximize the number
  of issues.


After completing all checks, decide whether a revision is actually
necessary.

If the design adequately satisfies the important requirements,
constraints, and any applicable human feedback:

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

When human feedback is present, do not approve the design unless
the requested change has been adequately addressed.

However, do not reject a technically sound design simply because
the human requested a preference that has been reasonably
implemented.

Return the result as valid JSON using the provided structured output schema.

The response must be a valid JSON object.
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

    human_response = interrupt({
        "message": "Human intervention required",
        "user_goal": state.user_goal,
        "requirements" : state.requirements.model_dump(),
        'Architecture' : state.architecture.model_dump(),
        'technologyrecommendations':(
            state.technologyrecommendations.model_dump()
        ),
        'critique':state.critique.model_dump(),
    })

    decision = human_response['decision']
    feedback = human_response.get('feedback')

    if decision == "approve":
     return Command(
        update={
            "human_decision": "approve",
            "human_feedback": feedback
        },
        goto="finalizer"
    )

    elif decision == "revise":
     return Command(
        update={
            "human_decision": "revise",
            "human_feedback": feedback
        },
        goto=state.critique.target_agent
    )

    elif decision == "reject":
      return Command(
        update={
            "human_decision": "reject",
            "human_feedback": feedback
        },
        goto=END
    )
    else:

        raise ValueError(
            "Invalid human decision. "
            "Expected 'approve', 'revise', or 'reject'."
        )

def diagram_node(state: ArchonState):

    print("Diagram Agent")

    prompt = f"""
You are a diagram extraction agent.

Convert the approved Final Blueprint below into an architecture
diagram represented by the provided structured output schema.

FINAL BLUEPRINT:
{state.final_blueprint}

RULES:

1. Extract only architecture components explicitly present in the
   Final Blueprint.

2. Do not invent new architecture components.

3. Every node must have:
   - id
   - label
   - type

4. Every edge must have:
   - source
   - target
   - label

5. Every edge source and target must exactly match an existing node id.

6. Do not create duplicate nodes.

7. Do not create self-referencing edges.

8. Represent the important data flows described in the blueprint.

9. Keep the diagram simple and readable.

10. Use the exact field names defined by the schema.
    For edges, the required fields are exactly:
    "source", "target", and "label".

11. Return ONLY the structured ArchitectureDiagram object.
"""

    result = groq_diagram_model.with_structured_output(
    ArchitectureDiagram,
    method="json_schema",
    strict=True,
        ).invoke(prompt) 

    print("Architecture Diagram generated")

    return {
        "diagram": result
    }