import inspect
from tools.tigergraph_client import get_tigergraph_client

c = get_tigergraph_client()
c.connect()
conn = c._connection

print("=" * 60)
print("1. upsertEdges signature")
print("=" * 60)
try:
    print(inspect.signature(conn.upsertEdges))
except Exception as e:
    print("cannot introspect:", e)

print()
print("=" * 60)
print("2. Vertex types actually installed")
print("=" * 60)
schema = conn.getSchema()
vt_names = [v.get("Name") for v in schema.get("VertexTypes", [])]
print(" ", vt_names)

print()
print("=" * 60)
print("3. Try 3 upsertEdges call forms on a real edge")
print("=" * 60)

# pick a real customer and their real transaction from the graph
sample = conn.getEdges("Customer", "C06075", "CustomerMakesTransaction", limit=1)
print("sample existing edge (should be empty — edges not loaded yet):", sample)

# We know from the CSV that C06075 -> 3000001 is a real pair
SRC_ID, SRC_T = "C06075", "Customer"
TGT_ID, TGT_T = "3000001", "Transaction"

# Form A — (edgeType, sourceVertexType, targetVertexType, edges)
try:
    conn.upsertEdges("CustomerMakesTransaction", SRC_T, TGT_T,
                     [(SRC_ID, TGT_ID, {})])
    print("  Form A (edgeType, srcT, tgtT, [(srcId, tgtId, attrs)]) -> OK")
except Exception as e:
    print("  Form A -> FAIL:", str(e)[:200])

# Form B — (edgeType, [(srcT, srcId, tgtT, tgtId, attrs)])
try:
    conn.upsertEdges("CustomerMakesTransaction",
                     [(SRC_T, SRC_ID, TGT_T, TGT_ID, {})])
    print("  Form B (edgeType, [(srcT, srcId, tgtT, tgtId, attrs)]) -> OK")
except Exception as e:
    print("  Form B -> FAIL:", str(e)[:200])

# Form C — (edgeType, sourceVertexType, targetVertexType, [(srcId, tgtId)])
try:
    conn.upsertEdges("CustomerMakesTransaction", SRC_T, TGT_T, [(SRC_ID, TGT_ID)])
    print("  Form C (edgeType, srcT, tgtT, [(srcId, tgtId)]) -> OK")
except Exception as e:
    print("  Form C -> FAIL:", str(e)[:200])

print()
print("=" * 60)
print("4. Verify: did any of them actually write?")
print("=" * 60)
try:
    e = conn.getEdges("Customer", "C06075", "CustomerMakesTransaction")
    print(f"  CustomerMakesTransaction edges from C06075: {len(e)}")
    for x in e[:3]:
        print("   ", x)
except Exception as e:
    print("  read failed:", e)