import json
from pathlib import Path
from datetime import datetime, timezone


DATASET_PATH = Path("evaluation/datasets/archon_golden.jsonl")
RESULTS_DIR = Path("evaluation/results")

# Change this to the baseline run you already generated.
RUN_PATH = Path(
    "evaluation/results/run_20260904_034744.json"
)


def load_dataset():
    cases = []

    with DATASET_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))

    return cases


def load_run():
    with RUN_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def score_case(case, result):
    """
    Deterministic structural evaluation.

    This does NOT judge whether the architecture is good.
    That will be handled later by DeepEval / LLM judges.
    """

    output = result.get("result", {})

    requirements = output.get("requirements")
    architecture = output.get("architecture")
    technology = output.get("technologyrecommendations")
    critique = output.get("critique")
    final_blueprint = output.get("final_blueprint")

    interrupt = output.get("__interrupt__")

    checks = {
        "requirements_produced": requirements is not None,
        "architecture_produced": architecture is not None,
        "technology_recommendations_produced": technology is not None,
        "critique_produced": critique is not None,
        "final_blueprint_produced": final_blueprint is not None,
        "human_review_triggered": interrupt is not None,
    }

    # Basic structural score.
    passed_checks = sum(checks.values())
    total_checks = len(checks)

    structural_score = (
        passed_checks / total_checks * 100
        if total_checks
        else 0
    )

    # Determine high-level outcome.
    if interrupt is not None:
        status = "human_review_required"
    elif final_blueprint is not None:
        status = "completed"
    else:
        status = "incomplete"

    return {
        "id": case["id"],
        "category": case["category"],
        "difficulty": case.get("difficulty"),
        "status": status,
        "checks": checks,
        "passed_checks": passed_checks,
        "total_checks": total_checks,
        "structural_score": round(structural_score, 2),
        "revision_count": output.get("revision_count", 0),
        "thread_id": result.get("thread_id"),
    }


def print_summary(scored_results):
    total = len(scored_results)

    completed = sum(
        r["status"] == "completed"
        for r in scored_results
    )

    human_review = sum(
        r["status"] == "human_review_required"
        for r in scored_results
    )

    incomplete = sum(
        r["status"] == "incomplete"
        for r in scored_results
    )

    average_score = (
        sum(r["structural_score"] for r in scored_results) / total
        if total
        else 0
    )

    print("\n" + "=" * 50)
    print("ARCHON DETERMINISTIC EVALUATION")
    print("=" * 50)

    print(f"Total cases:       {total}")
    print(f"Completed:         {completed}")
    print(f"Human review:      {human_review}")
    print(f"Incomplete:        {incomplete}")
    print(f"Average structure: {average_score:.2f}%")

    print("\nPer-case results:")
    print("-" * 50)

    for result in scored_results:
        print(
            f"{result['id']} | "
            f"{result['category']:<25} | "
            f"{result['status']:<22} | "
            f"{result['structural_score']:>6.2f}%"
        )


def main():
    cases = load_dataset()
    run = load_run()

    run_results = {
        result["id"]: result
        for result in run["results"]
    }

    scored_results = []

    for case in cases:
        result = run_results.get(case["id"])

        if result is None:
            print(f"Warning: no result found for {case['id']}")
            continue

        scored_results.append(
            score_case(case, result)
        )

    print_summary(scored_results)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S"
    )

    output_path = (
        RESULTS_DIR / f"scored_run_{timestamp}.json"
    )

    output = {
        "run_id": run.get("run_id"),
        "scored_at": datetime.now(timezone.utc).isoformat(),
        "total_cases": len(scored_results),
        "results": scored_results,
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            output,
            f,
            indent=2
        )

    print("\nScoring completed.")
    print(f"Scores saved to: {output_path}")


if __name__ == "__main__":
    main()