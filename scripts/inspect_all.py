import os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("1. FILES IN graph/ (with sizes)")
print("=" * 70)
for p in sorted(glob.glob(os.path.join(ROOT, "graph", "**", "*"), recursive=True)):
    if os.path.isfile(p):
        print(f"  {os.path.getsize(p):>8} bytes  {os.path.relpath(p, ROOT)}")

print()
print("=" * 70)
print("2. CONTENTS OF EVERY .gsql FILE UNDER graph/")
print("=" * 70)
for p in sorted(glob.glob(os.path.join(ROOT, "graph", "**", "*.gsql"), recursive=True)):
    print(f"\n----- {os.path.relpath(p, ROOT)} ({os.path.getsize(p)} bytes) -----")
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    if not content.strip():
        print("  (EMPTY)")
    else:
        print(content)

print()
print("=" * 70)
print("3. CSV HEADERS (first 2 lines of each file under data/processed)")
print("=" * 70)
for csv in sorted(glob.glob(os.path.join(ROOT, "data", "processed", "**", "*.csv"), recursive=True)):
    print(f"\n----- {os.path.relpath(csv, ROOT)} -----")
    with open(csv, "r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            if i >= 2:
                break
            print("  " + line.rstrip())