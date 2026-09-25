"""Test card_reuse — card footprint and co-customer count."""
from tools.tigergraph_client import get_tigergraph_client

c = get_tigergraph_client()
c.connect()

QUERY = "card_reuse"
for cid in ("C06075", "C07096", "C00259"):
    print(f"\n=== {QUERY} for {cid} ===")
    try:
        r = c.run_query(QUERY, params={"customer": (cid,)})
        if not r or r == [{}]:
            print("  EMPTY"); continue
        row = r[0]
        cards   = row.get("@@my_cards", [])
        txns    = row.get("@@my_card_txns", [])
        co_cust = row.get("@@co_customers", [])
        print(f"  my cards:                        {len(cards)}")
        print(f"  global txns on my cards:         {len(txns)}")
        print(f"  co-customers sharing a card:     {len(co_cust)}")
    except Exception as e:
        print("  failed:", str(e)[:400])