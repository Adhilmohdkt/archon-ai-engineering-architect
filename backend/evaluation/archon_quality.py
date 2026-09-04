import json
import time
from pathlib import Path

from deepeval import evaluate
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

from evaluation.judge import judge


# ============================================================
# FILE PATHS
# ============================================================

DATASET_PATH = Path(
    "evaluation/datasets/archon_golden.jsonl"
)

RUN_PATH = Path(
    "evaluation/results/run_20260904_034744.json"
)

RESULTS_PATH = Path(
    "evaluation/results/archon_quality_results.json"
)


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    cases = []

    with DATASET_PATH.open(
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            if line.strip():

                cases.append(
                    json.loads(line)
                )

    return cases


# ============================================================
# LOAD ARCHON RUN
# ============================================================

def load_run():

    with RUN_PATH.open(
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# FIND CASE RESULT
# ============================================================

def find_result(run, case_id):

    for result in run["results"]:

        if result["id"] == case_id:

            return result

    raise ValueError(
        f"Run result not found: {case_id}"
    )


# ============================================================
# COMMON SCORING SCALE
# ============================================================

SCORING_SCALE = """
Use this scoring scale:

1.0 = Exceptional.
      Fully satisfies the criterion with strong technical depth,
      excellent consistency, and no meaningful omissions.

0.8 = Strong.
      Clearly satisfies the criterion with only minor weaknesses
      or omissions that do not materially affect the design.

0.6 = Adequate.
      Satisfies the main requirement but has noticeable gaps,
      limited justification, or areas needing improvement.

0.4 = Weak.
      Partially satisfies the criterion but contains significant
      omissions, questionable decisions, or insufficient detail.

0.2 = Very weak.
      Only superficial coverage or major technical problems.

0.0 = Fails.
      The criterion is essentially not addressed or fundamentally
      contradicts the user's requirements.

IMPORTANT:

Do not give 1.0 simply because something is mentioned.

Use 1.0 only for genuinely exceptional and comprehensive work.

Use intermediate scores when meaningful weaknesses exist.

Do not inflate scores because the answer is long, well formatted,
or contains many technologies.
"""


# ============================================================
# CREATE GEVAL METRICS
# ============================================================

def create_metrics(golden_case):

    user_goal = golden_case["user_goal"]

    must_address = json.dumps(
        golden_case["must_address"],
        indent=2
    )

    # --------------------------------------------------------
    # REQUIREMENTS COVERAGE
    # --------------------------------------------------------

    requirements_metric = GEval(

        name="Requirements Coverage",

        criteria=f"""
Evaluate how completely the final architecture blueprint
addresses the user's requirements.

USER GOAL:

{user_goal}

REQUIREMENTS THAT MUST BE ADDRESSED:

{must_address}

Evaluate:

1. Important requirements are explicitly addressed.
2. The architecture explains how the requirements are satisfied.
3. Architectural decisions meaningfully address the requirements.
4. Important requirements are not ignored or contradicted.
5. The blueprint provides enough detail to demonstrate that
   the requirements were actually considered.

Do not award a perfect score merely because requirements
are mentioned.

Check whether the architecture actually explains how the
requirements are satisfied.

{SCORING_SCALE}
""",

        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],

        threshold=0.5,

        model=judge,
    )


    # --------------------------------------------------------
    # ARCHITECTURE QUALITY
    # --------------------------------------------------------

    architecture_metric = GEval(

        name="Architecture Quality",

        criteria=f"""
Evaluate the quality of the architecture proposed by Archon.

USER GOAL:

{user_goal}

Evaluate:

1. Whether the architecture style is appropriate.
2. Whether responsibilities are clearly separated.
3. Whether component interactions and data flow are logical.
4. Whether the design can scale according to the requirements.
5. Whether reliability and fault tolerance are appropriate.
6. Whether unnecessary complexity is avoided.
7. Whether the architecture is consistent with the requirements.

Do not reward the answer simply for listing many components.

Evaluate whether the components form a coherent architecture.

An unnecessarily complicated architecture should lose points
even if all of its components are individually valid.

{SCORING_SCALE}
""",

        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],

        threshold=0.5,

        model=judge,
    )


    # --------------------------------------------------------
    # TECHNOLOGY DECISIONS
    # --------------------------------------------------------

    technology_metric = GEval(

        name="Technology Decisions",

        criteria=f"""
Evaluate the quality of the technology recommendations.

USER GOAL:

{user_goal}

Evaluate:

1. Whether technologies fit the requirements.
2. Whether major technology choices have meaningful reasons.
3. Whether alternatives are reasonable where provided.
4. Whether important trade-offs are considered.
5. Whether technology choices are consistent with the architecture.
6. Whether the technologies form a coherent stack.
7. Whether choices are based on requirements rather than popularity.

Penalize:

- unnecessary technologies
- unjustified choices
- contradictory choices
- excessive complexity
- technologies that do not fit the requirements

Do not award a perfect score merely because every component
has a technology assigned to it.

{SCORING_SCALE}
""",

        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],

        threshold=0.5,

        model=judge,
    )


    # --------------------------------------------------------
    # RELIABILITY AND SECURITY
    # --------------------------------------------------------

    reliability_security_metric = GEval(

        name="Reliability and Security",

        criteria=f"""
Evaluate how well the architecture addresses reliability,
security, and operational risks.

USER GOAL:

{user_goal}

Evaluate where relevant:

1. Authentication and authorization.
2. Data protection and privacy.
3. Secure handling of secrets and credentials.
4. Failure handling and fault tolerance.
5. Retry, timeout, and recovery strategies.
6. Scalability and resilience.
7. Monitoring and observability.
8. Backup and disaster recovery.

Do not require every possible security mechanism.

Judge according to the actual risks of the user's system.

Penalize important omissions when they create meaningful
security or reliability risks.

Do not award a perfect score merely because the blueprint
contains a generic security checklist.

{SCORING_SCALE}
""",

        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],

        threshold=0.5,

        model=judge,
    )


    # --------------------------------------------------------
    # FINAL BLUEPRINT QUALITY
    # --------------------------------------------------------

    blueprint_metric = GEval(

        name="Final Blueprint Quality",

        criteria=f"""
Evaluate the overall quality and usefulness of the final
architecture blueprint.

USER GOAL:

{user_goal}

Evaluate whether the blueprint:

1. Is clear and well organized.
2. Provides sufficient technical detail.
3. Presents a coherent end-to-end design.
4. Is consistent across requirements, architecture,
   technologies, and implementation details.
5. Explains important architectural decisions.
6. Identifies assumptions and open decisions where appropriate.
7. Could realistically serve as a starting point for implementation.
8. Avoids unnecessary verbosity and irrelevant information.

Judge the blueprint as an architecture deliverable,
not merely as a well-written document.

Do not equate length with quality.

{SCORING_SCALE}
""",

        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],

        threshold=0.5,

        model=judge,
    )


    return [
        requirements_metric,
        architecture_metric,
        technology_metric,
        reliability_security_metric,
        blueprint_metric,
    ]


# ============================================================
# EVALUATE ONE CASE
# ============================================================

def evaluate_case(golden_case, run_result):

    archon_output = run_result["result"]

    final_blueprint = archon_output.get(
        "final_blueprint"
    )

    # --------------------------------------------------------
    # INCOMPLETE OUTPUT
    # --------------------------------------------------------

    if not final_blueprint:

        return {
            "id": golden_case["id"],
            "category": golden_case["category"],
            "status": "incomplete",
            "scores": {},
            "overall_score": 0.0,
        }


    # --------------------------------------------------------
    # DEEPEVAL TEST CASE
    # --------------------------------------------------------

    test_case = LLMTestCase(

        input=golden_case["user_goal"],

        actual_output=final_blueprint,
    )


    metrics = create_metrics(
        golden_case
    )


    metric_results = []


    # --------------------------------------------------------
    # SEQUENTIAL EVALUATION
    # --------------------------------------------------------

    for index, metric in enumerate(metrics):

        print(
            f"\n    → {metric.name}"
        )


        try:

            result = evaluate(

                test_cases=[
                    test_case
                ],

                metrics=[
                    metric
                ],
            )


            metric_result = (
                result
                .test_results[0]
                .metrics_data[0]
            )


            metric_results.append(
                metric_result
            )


            if metric_result.score is not None:

                print(
                    f"      Score: "
                    f"{metric_result.score:.2f}"
                )

            else:

                print(
                    "      Score: unavailable"
                )


        except Exception as error:

            print(
                f"      ERROR: {error}"
            )


        # ----------------------------------------------------
        # SMALL DELAY BETWEEN REQUESTS
        #
        # Helps avoid provider burst/rate-limit problems.
        # ----------------------------------------------------

        if index < len(metrics) - 1:

            time.sleep(3)


    # ========================================================
    # COLLECT RESULTS
    # ========================================================

    scores = {}


    for metric_result in metric_results:

        scores[
            metric_result.name
        ] = {

            "score": metric_result.score,

            "success": metric_result.success,

            "reason": metric_result.reason,
        }


    # ========================================================
    # OVERALL SCORE
    # ========================================================

    numeric_scores = [

        metric_result.score

        for metric_result in metric_results

        if metric_result.score is not None
    ]


    if numeric_scores:

        overall_score = (
            sum(numeric_scores)
            / len(numeric_scores)
        )

    else:

        overall_score = 0.0


    # ========================================================
    # STATUS
    # ========================================================

    if len(metric_results) == len(metrics):

        status = "evaluated"

    else:

        status = "partially_evaluated"


    return {

        "id": golden_case["id"],

        "category": golden_case["category"],

        "status": status,

        "scores": scores,

        "overall_score": overall_score,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    dataset = load_dataset()

    run = load_run()


    print(
        f"Loaded {len(dataset)} golden cases"
    )

    print(
        "Judge: Gemini 2.5 Flash"
    )

    print(
        "Metrics per case: 5"
    )

    print(
        f"Total metric evaluations: "
        f"{len(dataset) * 5}"
    )


    results = []


    # ========================================================
    # RUN ALL 10 CASES
    # ========================================================

    for case_number, golden_case in enumerate(
        dataset,
        start=1
    ):

        case_id = golden_case["id"]

        print(
            "\n" + "=" * 60
        )

        print(
            f"CASE {case_number}/{len(dataset)}"
        )

        print(
            f"{case_id}: "
            f"{golden_case['category']}"
        )

        print(
            "=" * 60
        )


        try:

            run_result = find_result(
                run,
                case_id
            )


            result = evaluate_case(
                golden_case,
                run_result
            )


            results.append(
                result
            )


            print(
                f"\n    Overall: "
                f"{result['overall_score']:.2f}"
            )


        except Exception as error:

            print(
                f"\n    CASE ERROR: {error}"
            )


            results.append({

                "id": case_id,

                "category": golden_case["category"],

                "status": "error",

                "scores": {},

                "overall_score": 0.0,

                "error": str(error),
            })


    # ========================================================
    # OUTPUT
    # ========================================================

    output = {

        "run_id": run["run_id"],

        "evaluation_type": "DeepEval GEval",

        "judge_model": "Gemini 2.5 Flash",

        "total_cases": len(results),

        "total_metrics": len(results) * 5,

        "results": results,
    }


    # ========================================================
    # SAVE
    # ========================================================

    RESULTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    with RESULTS_PATH.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False
        )


    # ========================================================
    # SUMMARY
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "ARCHON QUALITY EVALUATION COMPLETE"
    )

    print(
        "=" * 70
    )


    evaluated_scores = []


    for result in results:

        score = result["overall_score"]

        if result["status"] in (
            "evaluated",
            "partially_evaluated",
        ):

            evaluated_scores.append(
                score
            )


        print(

            f"{result['id']:15} | "
            f"{result['category']:25} | "
            f"{result['status']:20} | "
            f"{score:.2f}"

        )


    # ========================================================
    # GLOBAL SCORE
    # ========================================================

    if evaluated_scores:

        global_score = (
            sum(evaluated_scores)
            / len(evaluated_scores)
        )

    else:

        global_score = 0.0


    print(
        "\n" + "-" * 70
    )

    print(
        f"GLOBAL QUALITY SCORE: "
        f"{global_score:.2f}"
    )

    print(
        f"GLOBAL QUALITY PERCENTAGE: "
        f"{global_score * 100:.1f}%"
    )

    print(
        "-" * 70
    )


    print(
        "\nResults saved to:"
    )

    print(
        RESULTS_PATH
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()