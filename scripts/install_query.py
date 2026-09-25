"""Install (or replace) a GSQL query from a file."""
import os, sys
from tools.tigergraph_client import get_tigergraph_client

c = get_tigergraph_client()
c.connect()
conn = c._connection

REL = sys.argv[1] if len(sys.argv) > 1 else "graph/queries/transaction_history.gsql"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(ROOT, REL)

print(f"Reading {REL} ...")
with open(path, "r", encoding="utf-8") as f:
    body = f.read()

# Extract the query name so we can drop before recreating.
import re
m = re.search(r"CREATE\s+QUERY\s+(\w+)", body, re.IGNORECASE)
if not m:
    print("Could not find CREATE QUERY in file.")
    sys.exit(1)
qname = m.group(1)
print(f"Query name in file: {qname}")

# Rewrite CREATE QUERY -> CREATE OR REPLACE QUERY (idempotent).
graph_name = c.get_graph_name()   # FraudInvestigationGraph
body_install = re.sub(r"CREATE\s+QUERY", "CREATE OR REPLACE QUERY", body,
                      count=1, flags=re.IGNORECASE)
body_install = f"USE GRAPH {graph_name}\n\n{body_install}"
print(f"Prepending: USE GRAPH {graph_name}")
print("Installing ...")
try:
    out = conn.gsql(body_install)
    print(out)
except Exception as e:
    print("gsql failed:", e)
    sys.exit(1)

# Verify it's registered
try:
    meta = conn.getQueryMetadata(qname)
    print("Registered. Parameters:", meta.get("input"))
except Exception as e:
    print("Registered but metadata read failed:", e)

print("DONE.")