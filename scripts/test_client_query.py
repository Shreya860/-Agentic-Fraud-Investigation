"""Step 4: Prove the wrapper (tools.tigergraph_client) can run the query."""
from tools.tigergraph_client import get_tigergraph_client

c = get_tigergraph_client()
c.connect()
QUERY = "customer_transaction_history_v2"
CID = "C06075"

# The wrapper accepts different signatures in different pyTigerGraph versions.
# Try them all; stop at first non-empty return.
attempts = [
    ("kwargs params= 1-tuple", lambda: c.run_query(QUERY, params={"customer": (CID,)})),
    ("kwargs params= dict",    lambda: c.run_query(QUERY, params={"customer": {"Customer": CID}})),
    ("kwargs params= str",     lambda: c.run_query(QUERY, params={"customer": CID})),
    ("positional list",        lambda: c.run_query(QUERY, [("customer", (CID,))])),
    ("bare",                   lambda: c.run_query(QUERY)),
]

working = None
for label, fn in attempts:
    print(f"\n=== {label} ===")
    try:
        r = fn()
        print("  result:", r if not isinstance(r, list) or len(str(r)) < 400 else str(r)[:400] + " …")
        if r and r != [{}]:
            working = label
            txns = r[0].get("transactions") if isinstance(r[0], dict) else None
            print(f"  ✓ transactions: {len(txns) if txns else 0}")
            break
    except Exception as e:
        print("  failed:", str(e)[:250])

print("\n=== VERDICT ===")
if working:
    print(f"Working wrapper call: {working}")
    print("Step 4 PASSED — investigator can call this query through tools.tigergraph_client.")
else:
    print("No wrapper form worked.")
    print("Next action: inspect tools/tigergraph_client.py run_query() and add")
    print("VERTEX-param passthrough (1-tuple) exactly like raw runInstalledQuery.")