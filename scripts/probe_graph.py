from tools.tigergraph_client import get_tigergraph_client

c = get_tigergraph_client()
c.connect()
conn = c._connection  # confirmed from prior run

# --- 1. Schema: what vertex & edge types are actually defined? ---
print("=== Vertex types (schema) ===")
try:
    schema = conn.getSchema()
    for vt in schema.get("VertexTypes", []):
        print(" ", vt.get("Name"))
    print("\n=== Edge types (schema) ===")
    for et in schema.get("EdgeTypes", []):
        frm = et.get("FromVertexType") or et.get("FromVertexTypeName")
        to  = et.get("ToVertexType")   or et.get("ToVertexTypeName")
        print(f"  {et.get('Name')}: {frm} -> {to}")
except Exception as e:
    print("getSchema failed:", repr(e))

# --- 2. Row counts for the two vertices we care about ---
print("\n=== Vertex counts ===")
for vt in ["Customer", "Transaction"]:
    try:
        print(f"  {vt}: {conn.getVertexCount(vt)}")
    except Exception as e:
        print(f"  {vt} count failed:", repr(e))

# --- 3. Try a known customer ID directly ---
print("\n=== Try customer_transaction_history_v2 with C05031 ===")
for label, params in [
    ("tuple form", {"customer": ("Customer", "C05031")}),
    ("string form", {"customer": "C05031"}),
    ("dict form",   {"customer": {"Customer": "C05031"}}),
]:
    print(f"\n-- {label}: {params}")
    try:
        r = conn.runInstalledQuery("customer_transaction_history_v2", params=params)
        print("   result:", r)
        if r and r != [{}]:
            print("   ^^^ NON-EMPTY — this is the working call format.")
            break
    except Exception as e:
        print("   failed:", repr(e))