import json
from pathlib import Path

import pandas as pd

from agent.orchestrator import InvestigationOrchestrator


CASE_PACK = Path("data/raw/HHGOA_IEEE/case_pack.csv")
OUTPUT = Path("evaluation/benchmark_results.json")
CASES_DIR = Path("cases")


def main():
    df = pd.read_csv(CASE_PACK)

    results = []

    # Make sure the required submission folder exists.
    CASES_DIR.mkdir(parents=True, exist_ok=True)

    for row in df.itertuples(index=False):
        case_id = str(row.case_id)

        print(f"Running {case_id}...")

        orchestrator = InvestigationOrchestrator()

        result = orchestrator.investigate_customer(
            customer_id=str(row.customer_id),
            trigger_type=str(row.trigger_type),
            trigger_text=str(row.trigger_text),
            flagged_txn_id=str(row.flagged_txn_id),
        )

        # Complete benchmark record.
        benchmark_result = {
            "benchmark_case_id": case_id,
            "customer_id": str(row.customer_id),
            "flagged_txn_id": str(row.flagged_txn_id),
            "trigger_type": str(row.trigger_type),
            "trigger_text": str(row.trigger_text),
            "result": result,
        }

        results.append(benchmark_result)

        # Required HHGOA submission file:
        # cases/HHG-001.json ... cases/HHG-020.json
        case_output = CASES_DIR / f"{case_id}.json"

        with case_output.open("w", encoding="utf-8") as f:
            json.dump(
                benchmark_result,
                f,
                indent=2,
                ensure_ascii=False,
                default=str,
            )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    print()
    print(f"Completed: {len(results)} cases")
    print(f"Saved: {OUTPUT}")
    print(f"Case files: {CASES_DIR}")


if __name__ == "__main__":
    main()