import json
from pathlib import Path

import pandas as pd

from agent.orchestrator import InvestigationOrchestrator


CASE_PACK = Path("data/raw/HHGOA_IEEE/case_pack.csv")
OUTPUT = Path("evaluation/benchmark_results.json")


def main():
    df = pd.read_csv(CASE_PACK)

    results = []

    for row in df.itertuples(index=False):
        print(f"Running {row.case_id}...")

        orchestrator = InvestigationOrchestrator()

        result = orchestrator.investigate_customer(
            customer_id=str(row.customer_id),
            trigger_type=str(row.trigger_type),
            trigger_text=str(row.trigger_text),
            flagged_txn_id=str(row.flagged_txn_id),
        )

        results.append(
            {
                "benchmark_case_id": str(row.case_id),
                "customer_id": str(row.customer_id),
                "flagged_txn_id": str(row.flagged_txn_id),
                "trigger_type": str(row.trigger_type),
                "result": result,
            }
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)

    print()
    print(f"Completed: {len(results)} cases")
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()