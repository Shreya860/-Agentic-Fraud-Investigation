"""Test device_reuse — device footprint and co-customer count."""
from tools.tigergraph_client import get_tigergraph_client

c = get_tigergraph_client()
c.connect()

QUERY = "device_reuse"
for cid in ("C06075", "C10560"):
    print(f"\n=== {QUERY} for {cid} ===")
    try:
        r = c.run_query(QUERY, params={"customer": (cid,)})
        if not r or r == [{}]:
            print("  EMPTY"); continue
        row = r[0]
        devs    = row.get("@@my_devices", [])
        txns    = row.get("@@my_device_txns", [])
        co_cust = row.get("@@co_customers", [])
        print(f"  my devices:                          {len(devs)}")
        print(f"  global txns on any of my devices:    {len(txns)}")
        print(f"  co-customers sharing any device:     {len(co_cust)}")
    except Exception as e:
        print("  failed:", str(e)[:400])