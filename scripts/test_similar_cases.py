"""Test similar_cases for customers with and without their own cases."""
from tools.tigergraph_client import get_tigergraph_client

c = get_tigergraph_client()
c.connect()

QUERY = "similar_cases"
for cid in ("C00259", "C06075"):     # C00259 exists in historical_cases.csv
    print(f"\n=== {QUERY} for {cid} ===")
    try:
        r = c.run_query(QUERY, params={"customer": (cid,)})
        if not r or r == [{}]:
            print("  EMPTY")
            continue
        row = r[0]
        own  = row.get("OwnCases", [])
        same = row.get("SamePatternCases", [])
        print(f"  own cases:          {len(own)}")
        print(f"  same-pattern cases: {len(same)}")
        if own:
            a = own[0].get("attributes", {})
            print(f"  own sample:  case_id={own[0].get('v_id')}  pattern={a.get('pattern')}  outcome={a.get('outcome')}")
        if same:
            a = same[0].get("attributes", {})
            print(f"  same sample: case_id={same[0].get('v_id')}  pattern={a.get('pattern')}")
    except Exception as e:
        print("  failed:", str(e)[:400])