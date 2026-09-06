import os
import asyncio

from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from app.state import ArchonState
from app.agents import (
    supervisor_node,
    requirements_architecture_node,
    technology_node,
    critic_node,
    finalizer_node,
    human_node,
)


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")


# ---------------------------------------------------------
# Build Archon graph
# ---------------------------------------------------------

graph = StateGraph(ArchonState)

graph.add_node(
    "supervisor",
    supervisor_node,
    destinations=(
        "requirements",
        "technology",
        "critic",
        "finalizer",
        "human",
    ),
)

graph.add_node(
    "requirements",
    requirements_architecture_node,
)

graph.add_node(
    "technology",
    technology_node,
)

graph.add_node(
    "critic",
    critic_node,
)

graph.add_node(
    "finalizer",
    finalizer_node,
)

graph.add_node(
    "human",
    human_node,
    destinations=(
        "requirements",
        "technology",
        "finalizer",
        END,
    ),
)

graph.add_edge(START, "supervisor")
graph.add_edge("finalizer", END)


# ---------------------------------------------------------
# PostgreSQL
# ---------------------------------------------------------

pool = AsyncConnectionPool(
    conninfo=DATABASE_URL,
    kwargs={
        "autocommit": True,
        "row_factory": dict_row,
    },
    open=False,
)



checkpointer = None
app = None


async def initialize_database():
    global checkpointer, app

    await pool.open()

    checkpointer = AsyncPostgresSaver(pool)

    # Creates LangGraph checkpoint tables if needed.
    await checkpointer.setup()

    app = graph.compile(
        checkpointer=checkpointer
    )


async def close_database():
    await pool.close()


# ---------------------------------------------------------
# Local test
# ---------------------------------------------------------

async def test_graph():

    await initialize_database()

    try:

        initial_state = ArchonState(
            user_goal="Build a simple personal expense tracker."
        )

        config = {
            "configurable": {
                "thread_id": "archon-test-1"
            }
        }

        # First run
        result = await app.ainvoke(
            initial_state,
            config=config,
        )

        print("Graph paused for human review")

        # Resume with human decision
        human_response = Command(
            resume={
                "decision": "revise",
                "feedback": (
                    "Add API operations for viewing, deleting, "
                    "filtering, and summarizing expenses."
                ),
            }
        )

        result = await app.ainvoke(
            human_response,
            config=config,
        )

        print(result)

    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(
        test_graph(),
        loop_factory=lambda: asyncio.SelectorEventLoop(),
    )