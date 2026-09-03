import asyncio
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

from app.graph import app


DATASET_PATH = Path("evaluation/datasets/archon_golden.jsonl")
RESULTS_DIR = Path("evaluation/results")


def load_dataset():
    cases = []

    with DATASET_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))

    return cases


async def run_case(case):
    print(f"\nRunning {case['id']}: {case['category']}")

    thread_id = str(uuid.uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = await app.ainvoke(
        {
            "user_goal": case["user_goal"]
        },
        config=config
    )

    return {
        "id": case["id"],
        "category": case["category"],
        "thread_id": thread_id,
        "result": result,
    }


async def main():
    cases = load_dataset()

    print(f"Loaded {len(cases)} evaluation cases")

    results = []

    for case in cases:
        result = await run_case(case)
        results.append(result)

    # Create results directory if it doesn't exist
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Create a timestamp for this evaluation run
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    output_path = RESULTS_DIR / f"run_{timestamp}.json"

    output = {
        "run_id": timestamp,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_cases": len(results),
        "results": results,
    }

    # Save results
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            output,
            f,
            indent=2,
            default=str
        )

    print("\nEvaluation run completed.")
    print(f"Cases completed: {len(results)}")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())