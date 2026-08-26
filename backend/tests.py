from app.llm import supervisor_model

decision = supervisor_model.invoke(
    """
    You are the supervisor of an AI engineering architecture system.

    The user has provided a project goal, but no requirements or
    architecture have been created yet.

    Decide which agent should work next.
    """
)

print(decision)