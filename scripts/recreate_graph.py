"""Drop FraudInvestigationGraph and reinstall from graph/schema/schema.gsql."""
import os, sys
from tools.tigergraph_client import get_tigergraph_client

c = get_tigergraph_client()
c.connect()
conn = c._connection
GRAPH = c.get_graph_name()
print(f"Target graph: {GRAPH}")

# ---------- sanity: confirm it really is empty before we nuke it ----------
for vt in ("Customer", "Transaction", "Card", "Identity", "Device"):
    try:
        n = conn.getVertexCount(vt)
        print(f"  pre-drop {vt}: {n} rows")
    except Exception as e:
        print(f"  pre-drop {vt}: (cannot read) {e}")

DROPS = [
    f"DROP GRAPH {GRAPH}",
    "DROP EDGE CustomerMakesTransaction",
    "DROP EDGE TransactionUsesCard",
    "DROP EDGE TransactionHasIdentity",
    "DROP EDGE TransactionUsesDevice",
    "DROP EDGE FraudCaseFlagsTransaction",
    "DROP EDGE FraudCaseInvolvesCustomer",
    "DROP EDGE HistoricalCaseInvolvesCustomer",
    "DROP VERTEX Customer",
    "DROP VERTEX Transaction",
    "DROP VERTEX Card",
    "DROP VERTEX Identity",
    "DROP VERTEX Device",
    "DROP VERTEX FraudCase",
    "DROP VERTEX HistoricalCase",
    "DROP VERTEX Case",
    "DROP EDGE CaseFlagsTransaction",
    "DROP EDGE CaseInvolvesCustomer",
]

print("\n=== Dropping old schema ===")
for stmt in DROPS:
    try:
        conn.gsql(stmt)
        print(f"  ok   : {stmt}")
    except Exception as e:
        print(f"  skip : {stmt}   ({str(e)[:90]})")

print("\n=== Installing schema from graph/schema/schema.gsql ===")
schema_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "graph", "schema", "schema.gsql",
)
with open(schema_path, "r", encoding="utf-8") as f:
    schema = f.read()

try:
    conn.gsql(schema)
    print("  schema installed")
except Exception as e:
    print(f"  schema install FAILED: {e}")
    sys.exit(1)

print("\n=== Post-recreate counts (should all be 0) ===")
for vt in ("Customer", "Transaction", "Card", "Identity", "Device", "Case", "HistoricalCase"):
    try:
        print(f"  {vt}: {conn.getVertexCount(vt)}")
    except Exception as e:
        print(f"  {vt}: ERROR {e}")

print("\nDONE.")