"""Load FraudCase vertex + all edges (resume after partial load)."""
import csv, os, time
from datetime import datetime
from tools.tigergraph_client import get_tigergraph_client

c = get_tigergraph_client()
c.connect()
conn = c._connection
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, "data", "processed")
BATCH = 5000

def s(v):
    v = (v or "").strip(); return v if v else None
def i(v):
    v = (v or "").strip()
    if not v: return None
    try: return int(float(v))
    except: return None
def f(v):
    v = (v or "").strip()
    if not v: return None
    try: return float(v)
    except: return None
def dt(v):
    v = (v or "").strip()
    if not v: return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try: return datetime.strptime(v, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except: pass
    return None

def read_csv(rel):
    with open(os.path.join(DP, rel), "r", encoding="utf-8", errors="replace") as fh:
        return list(csv.DictReader(fh))

def upsert_v(vtype, rows):
    batch, total, errs = [], 0, 0
    for v_id, attrs in rows:
        clean = {k: v for k, v in attrs.items() if v is not None}
        batch.append((v_id, clean))
        if len(batch) >= BATCH:
            try: conn.upsertVertices(vtype, batch); total += len(batch)
            except Exception as e:
                errs += 1
                if errs <= 3: print(f"    batch error: {str(e)[:200]}")
            batch = []
    if batch:
        try: conn.upsertVertices(vtype, batch); total += len(batch)
        except Exception as e:
            errs += 1; print(f"    batch error: {str(e)[:200]}")
    return total, errs

def upsert_e(src_t, etype, tgt_t, rows):
    """NOTE: pyTigerGraph order is (sourceVertexType, edgeType, targetVertexType, edges)."""
    batch, total, errs = [], 0, 0
    for src, tgt, attrs in rows:
        clean = {k: v for k, v in attrs.items() if v is not None}
        batch.append((src, tgt, clean))
        if len(batch) >= BATCH:
            try: conn.upsertEdges(src_t, etype, tgt_t, batch); total += len(batch)
            except Exception as e:
                errs += 1
                if errs <= 3: print(f"    batch error: {str(e)[:200]}")
            batch = []
            if total and total % 100000 == 0:
                print(f"    ... {total} edges")
    if batch:
        try: conn.upsertEdges(src_t, etype, tgt_t, batch); total += len(batch)
        except Exception as e:
            errs += 1; print(f"    batch error: {str(e)[:200]}")
    return total, errs

def step(label, fn):
    print(f"\n--- {label} ---")
    t0 = time.time(); total, errs = fn()
    print(f"  loaded {total}   ({errs} failed batches)   in {time.time()-t0:.1f}s")

# --- schema peek so we can see what FraudCase actually expects ---
print("=== Installed FraudCase vertex schema ===")
for vt in conn.getSchema().get("VertexTypes", []):
    if vt.get("Name") == "FraudCase":
        pid = vt.get("PrimaryId", {})
        print(f"  primary_id: {pid.get('AttributeName')} ({pid.get('AttributeType')})")
        for a in vt.get("Attributes", []):
            print(f"    {a['AttributeName']}: {a['AttributeType']}")
print("\n=== Installed FraudCase-related edges ===")
for et in conn.getSchema().get("EdgeTypes", []):
    if "FraudCase" in et.get("Name", ""):
        print(f"  {et.get('Name')}: {et.get('FromVertexType')} -> {et.get('ToVertexType')}")

# --- 1. FraudCase vertex ---
step("FraudCase", lambda: upsert_v("FraudCase", (
    (r["case_id"], {
        "opened_at":      dt(r["opened_at"]),
        "trigger_type":   s(r["trigger_type"]),
        "trigger_text":   s(r["trigger_text"]),
        "flagged_txn_id": s(r["flagged_txn_id"]),
        "card_id":        s(r["card_id"]),
        "customer_id":    s(r["customer_id"]),
        "risk_score":     f(r["risk_score"]),
    }) for r in read_csv("cases/benchmark_cases.csv")
)))

# --- 2. All edges ---
step("CustomerMakesTransaction", lambda: upsert_e(
    "Customer", "CustomerMakesTransaction", "Transaction",
    ((r["customer_id"], r["transaction_id"], {}) for r in read_csv("edges/customer_makes_transaction.csv"))
))
step("TransactionUsesCard", lambda: upsert_e(
    "Transaction", "TransactionUsesCard", "Card",
    ((r["transaction_id"], r["card_key"], {}) for r in read_csv("edges/transaction_uses_card.csv"))
))
step("TransactionHasIdentity", lambda: upsert_e(
    "Transaction", "TransactionHasIdentity", "Identity",
    ((r["transaction_id"], r["transaction_id"], {}) for r in read_csv("edges/transaction_has_identity.csv"))
))
step("TransactionUsesDevice", lambda: upsert_e(
    "Transaction", "TransactionUsesDevice", "Device",
    ((r["transaction_id"], r["device_key"], {}) for r in read_csv("edges/transaction_uses_device.csv"))
))
step("FraudCaseFlagsTransaction", lambda: upsert_e(
    "FraudCase", "FraudCaseFlagsTransaction", "Transaction",
    ((r["case_id"], r["transaction_id"], {}) for r in read_csv("edges/case_flags_transaction.csv"))
))
step("FraudCaseInvolvesCustomer", lambda: upsert_e(
    "FraudCase", "FraudCaseInvolvesCustomer", "Customer",
    ((r["case_id"], r["customer_id"], {}) for r in read_csv("edges/case_involves_customer.csv"))
))
step("HistoricalCaseInvolvesCustomer", lambda: upsert_e(
    "HistoricalCase", "HistoricalCaseInvolvesCustomer", "Customer",
    ((r["case_id"], r["customer_id"], {}) for r in read_csv("edges/historical_case_customer.csv"))
))

print("\n=== Final counts ===")
for vt in ("Customer", "Transaction", "Card", "Identity", "Device", "FraudCase", "HistoricalCase"):
    try: print(f"  {vt}: {conn.getVertexCount(vt)}")
    except Exception as e: print(f"  {vt}: ERROR {e}")

print("\n=== Edge sample: C06075 -> CustomerMakesTransaction ===")
try:
    e = conn.getEdges("Customer", "C06075", "CustomerMakesTransaction")
    print(f"  edges: {len(e)}")
    for x in e[:3]: print("   ", x)
except Exception as e:
    print("  read failed:", e)

print("\nDONE.")