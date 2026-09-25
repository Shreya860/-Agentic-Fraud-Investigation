"""Test customer_network for a handful of customers."""
from tools.tigergraph_client import get_tigergraph_client

c = get_tigergraph_client()
c.connect()

QUERY = "customer_network"
for cid in ("C06075", "C07096"):
    print(f"\n=== {QUERY} for {cid} ===")
    try:
        r = c.run_query(QUERY, params={"customer": (cid,)})
        if not r or r == [{}]:
            print("  EMPTY")
            continue
        row = r[0]
        by_card   = row.get("CoCustomersByCard", [])
        by_device = row.get("CoCustomersByDevice", [])
        print(f"  co-customers by card:   {len(by_card)}")
        print(f"  co-customers by device: {len(by_device)}")
        if by_card:
            print(f"  sample card-co: {by_card[0]}")
        if by_device:
            print(f"  sample device-co: {by_device[0]}")
    except Exception as e:
        print("  failed:", str(e)[:400])