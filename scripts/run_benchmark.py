"""Run the agent on all 20 benchmark cases and dump JSON per case."""
import csv, json, os, time, traceback
from agent.orchestrator import InvestigationOrchestrator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = os.path.join(ROOT, "data", "processed", "cases", "benchmark_cases.csv")
OUT = os.path.join(ROOT, "benchmark_outputs")
os.makedirs(OUT, exist_ok=True)

print(f"Reading {BENCH}")
with open(BENCH, "r", encoding="utf-8") as f:
    cases = list(csv.DictReader(f))

print(f"Running {len(cases)} cases ...\n")
orch = InvestigationOrchestrator()
summary = []

for i, row in enumerate(cases, 1):
    cid = row["case_id"]
    customer_id = row["customer_id"]
    flagged_txn = row.get("flagged_txn_id") or None
    trigger_type = row.get("trigger_type", "risk_signal")
    trigger_text = row.get("trigger_text", "")
    out_path = os.path.join(OUT, f"{cid}.json")

    print(f"[{i:>2}/{len(cases)}] {cid}  customer={customer_id}  txn={flagged_txn}")
    t0 = time.time()
    try:
        result = orch.investigate_customer(
            customer_id=customer_id,
            limit=50,
            trigger_type=trigger_type,
            trigger_text=trigger_text,
            flagged_txn_id=flagged_txn,
        )
        elapsed = round(time.time() - t0, 2)

        # add the original benchmark row so output is self-describing
        result["benchmark_input"] = row
        result["elapsed_seconds"] = elapsed

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)

        a = result.get("assessment", {}) or {}
        d = result.get("decision", {}) or {}
        summary.append({
            "case_id": cid,
            "customer_id": customer_id,
            "risk_level": a.get("risk_level"),
            "risk_score": a.get("risk_score"),
            "recommended_action": d.get("action") or d.get("recommended_action"),
            "elapsed_s": elapsed,
            "status": "ok",
        })
        print(f"    -> risk={a.get('risk_level')} score={a.get('risk_score')} action={d.get('action')}  ({elapsed}s)")

    except Exception as e:
        traceback.print_exc()
        summary.append({
            "case_id": cid,
            "customer_id": customer_id,
            "status": f"ERROR: {e}",
        })

# write the summary table
summary_path = os.path.join(OUT, "_summary.json")
with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

print(f"\nDONE. Outputs in {OUT}")
print(f"Summary: {summary_path}")

# print a compact table
print("\n=== SUMMARY ===")
print(f"{'case':<10} {'customer':<10} {'risk':<12} {'action':<30} {'status'}")
for s in summary:
    print(f"{s['case_id']:<10} {s['customer_id']:<10} "
          f"{str(s.get('risk_level') or '-'):<12} "
          f"{str(s.get('recommended_action') or '-'):<30} {s['status']}")