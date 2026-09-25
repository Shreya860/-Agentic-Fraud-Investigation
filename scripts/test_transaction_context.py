"""Test transaction_context against a couple of known transaction IDs."""
from tools.tigergraph_client import get_tigergraph_client

c = get_tigergraph_client()
c.connect()

QUERY = "transaction_context"
for txn_id in ("3000001", "3064523"):
    print(f"\n=== {QUERY} for txn {txn_id} ===")
    try:
        r = c.run_query(QUERY, params={"txn": (txn_id,)})
        if not r or r == [{}]:
            print("  EMPTY")
            continue
        row = r[0]
        print(f"  seed:        {len(row.get('seed', []))} vertex")
        print(f"  cards:       {len(row.get('cards', []))}")
        print(f"  identities:  {len(row.get('identities', []))}")
        print(f"  devices:     {len(row.get('devices', []))}")
        if row.get("cards"):
            print(f"  card sample: {row['cards'][0]}")
        if row.get("devices"):
            print(f"  device sample: {row['devices'][0]}")
    except Exception as e:
        print("  failed:", str(e)[:300])