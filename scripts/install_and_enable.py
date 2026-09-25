"""Install a query AND explicitly enable it (needed on TG Cloud after REPLACE)."""
import os, re, sys
from tools.tigergraph_client import get_tigergraph_client

c = get_tigergraph_client()
c.connect()
conn = c._connection
graph = c.get_graph_name()

REL = sys.argv[1] if len(sys.argv) > 1 else "graph/queries/transaction_history.gsql"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, REL), "r", encoding="utf-8") as f:
    body = f.read()

m = re.search(r"CREATE\s+QUERY\s+(\w+)", body, re.IGNORECASE)
qname = m.group(1)
print(f"Query: {qname}    Graph: {graph}")

body_install = re.sub(r"CREATE\s+QUERY", "CREATE OR REPLACE QUERY", body,
                      count=1, flags=re.IGNORECASE)
body_install = f"USE GRAPH {graph}\n{body_install}\nINSTALL QUERY {qname}"

print("Running CREATE OR REPLACE + INSTALL ...")
out = conn.gsql(body_install)
print(out)

meta = conn.getQueryMetadata(qname)
print("Registered params:", meta.get("input"))
print("DONE.")