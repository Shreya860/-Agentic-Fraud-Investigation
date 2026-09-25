"""Test risk_context against a few customers."""
from tools.tigergraph_client import get_tigergraph_client

c = get_tigergraph_client()
c.connect()

QUERY = "risk_context"
for cid in ("C06075", "C07096", "C10560"):
    print(f"\n=== {QUERY} for {cid} ===")
    try:
        r = c.run_query(QUERY, params={"customer": (cid,)})
        if not r or r == [{}]:
            print("  EMPTY")
            continue
        row = r[0]
        for k, v in row.items():
            print(f"  {k}: {v}")
    except Exception as e:
        print("  failed:", str(e)[:400])