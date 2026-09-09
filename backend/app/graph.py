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
    diagram_node,
    human_node,
)


load_dotenv()


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
    "diagram",
    diagram_node,
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

# Finalizer now passes its output to the Diagram Agent
graph.add_edge("finalizer", "diagram")

# Diagram Agent is the final step
graph.add_edge("diagram", END)


# ---------------------------------------------------------
# PostgreSQL
# ---------------------------------------------------------

pool = None
checkpointer = None
app = None


async def initialize_database():
    global pool, checkpointer, app

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL not found in environment")

    pool = AsyncConnectionPool(
        conninfo=database_url,
        kwargs={
            "autocommit": True,
            "row_factory": dict_row,
        },
        open=False,
        check=AsyncConnectionPool.check_connection,
        max_idle=300,
        max_lifetime=1800,
    )

    await pool.open()

    checkpointer = AsyncPostgresSaver(pool)

    
    await checkpointer.setup()

    app = graph.compile(
        checkpointer=checkpointer
    )


async def close_database():
    global pool

    if pool is not None:
        await pool.close()
        pool = None


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
                "thread_id": "archon-test-2"
            }
        }

        result = await app.ainvoke(
            initial_state,
            config=config,
        )

        print("Graph paused for human review")

        print(result)

    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(
        test_graph(),
        loop_factory=lambda: asyncio.SelectorEventLoop(),
    )