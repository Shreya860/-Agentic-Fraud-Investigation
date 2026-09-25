from tools.tigergraph_client import get_tigergraph_client
import os, glob

c = get_tigergraph_client()
c.connect()
conn = c._connection

# --- 1. What other graphs exist on this TG instance? ---
print("=== Graphs on this TigerGraph instance ===")
try:
    print(conn.gsql("ls"))
except Exception as e:
    print("gsql ls failed:", repr(e))

# --- 2. Try listing each graph's vertex counts if we can switch ---
# (skip if not authorized; the ls output above is the main signal)

# --- 3. Look for data-loading scripts / CSVs in the repo ---
print("\n=== Repo files that look like data loaders or data ===")
root = os.getcwd()
patterns = [
    "**/*load*", "**/*ingest*", "**/*import*",
    "**/*.csv", "**/*.jsonl", "**/*.parquet",
    "**/data/**", "**/scripts/**",
]
seen = set()
for pat in patterns:
    for p in glob.glob(os.path.join(root, pat), recursive=True):
        if any(x in p for x in ("node_modules", ".venv", "venv", ".git", "site-packages")):
            continue
        if os.path.isdir(p):
            continue
        if p in seen:
            continue
        seen.add(p)
        print(" ", os.path.relpath(p, root))