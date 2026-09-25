from tools.tigergraph_client import get_tigergraph_client

c = get_tigergraph_client()
c.connect()
conn = c._connection

print("=" * 70)
print("FULL INSTALLED SCHEMA")
print("=" * 70)

schema = conn.getSchema()

for vt in schema.get("VertexTypes", []):
    pid = vt.get("PrimaryId", {})
    print(f"\nVERTEX {vt.get('Name')}")
    print(f"  primary_id: {pid.get('AttributeName')} ({pid.get('AttributeType')})")
    for a in vt.get("Attributes", []):
        print(f"    {a['AttributeName']}: {a['AttributeType']}")

for et in schema.get("EdgeTypes", []):
    print(f"\nEDGE {et.get('Name')}")
    print(f"  {et.get('FromVertexType')} -> {et.get('ToVertexType')}")
    for a in et.get("Attributes", []):
        print(f"    {a['AttributeName']}: {a['AttributeType']}")

print("\nDONE.")