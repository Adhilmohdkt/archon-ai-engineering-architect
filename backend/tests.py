from app.llm import requirements_architecture_model

result = requirements_architecture_model.invoke(
    """
    Build an AI customer-support system.

    Identify:
    - functional requirements
    - non-functional requirements
    - constraints

    Then propose an appropriate architecture based on those requirements.
    """
)

print(result)