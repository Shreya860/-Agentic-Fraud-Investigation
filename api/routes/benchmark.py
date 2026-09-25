from fastapi import APIRouter, HTTPException
import json, os

router = APIRouter(prefix="/api/benchmark", tags=["benchmark"])

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BENCH_DIR = os.path.join(ROOT, "benchmark_outputs")


@router.get("/summary")
def benchmark_summary():
    path = os.path.join(BENCH_DIR, "_summary.json")
    if not os.path.exists(path):
        raise HTTPException(404, "No benchmark summary yet. Run scripts.run_benchmark first.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/case/{case_id}")
def benchmark_case(case_id: str):
    path = os.path.join(BENCH_DIR, f"{case_id}.json")
    if not os.path.exists(path):
        raise HTTPException(404, f"No output file for {case_id}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)