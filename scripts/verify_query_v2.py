"""Step 1: Execute customer_transaction_history_v2 and verify it returns
real Customer -> CustomerMakesTransaction -> Transaction rows."""
from tools.tigergraph_client import get_tigergraph_client

c = get_tigergraph_client()
c.connect()
conn = c._connection
QUERY = "customer_transaction_history_v2"
CUSTOMER_ID = "C06075"   # from the CSV and confirmed to have 15 edges

# --- 1. Confirm metadata ---
meta = conn.getQueryMetadata(QUERY)
print("=== Query metadata ===")
print(" input:", meta.get("input"))
if meta.get("input"):
    param_name = next(iter(meta["input"][0].keys()))
else:
    param_name = "customer"
print(f"[info] parameter name: {param_name!r}")

# --- 2. Try every VERTEX param shape pyTigerGraph accepts ---
forms = [
    ("1-tuple (id,)",        {param_name: (CUSTOMER_ID,)}),
    ("2-tuple (id, type)",   {param_name: (CUSTOMER_ID, "Customer")}),
    ("2-tuple (type, id)",   {param_name: ("Customer", CUSTOMER_ID)}),
    ("plain string",         {param_name: CUSTOMER_ID}),
]

result = None
for label, params in forms:
    print(f"\n=== {label}: {params} ===")
    try:
        r = conn.runInstalledQuery(QUERY, params=params)
        print("  result:", r)
        if r and r != [{}]:
            result = r
            print(f"  ^^^ WORKING FORM = {label}")
            break
    except Exception as e:
        print("  failed:", str(e)[:220])

# --- 3. Verdict ---
print("\n=== VERDICT ===")
if result is None:
    print("Query returned empty for every param form.")
else:
    txs = result[0].get("Transactions", []) if isinstance(result[0], dict) else []
    print(f"Query returned {len(txs)} transactions for {CUSTOMER_ID}.")
    if txs:
        print("Sample transaction:", txs[0])
        print("\nPASS — Customer -> CustomerMakesTransaction -> Transaction confirmed.")
    else:
        print("Query ran but transaction list is empty.")