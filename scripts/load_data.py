"""Load all CSVs from data/processed into FraudInvestigationGraph."""
import csv, os, sys, time
from datetime import datetime
from tools.tigergraph_client import get_tigergraph_client

c = get_tigergraph_client()
c.connect()
conn = c._connection

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, "data", "processed")
BATCH = 5000

# ---- type converters (return None for empties so TG treats them as missing) ----
def s(v):
    v = (v or "").strip()
    return v if v else None

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
        try:
            return datetime.strptime(v, fmt).strftime("%Y-%m-%d %H:%M:%S")
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
            try:
                conn.upsertVertices(vtype, batch); total += len(batch)
            except Exception as e:
                errs += 1
                if errs <= 5: print(f"    batch error: {str(e)[:200]}")
            batch = []
    if batch:
        try:
            conn.upsertVertices(vtype, batch); total += len(batch)
        except Exception as e:
            errs += 1; print(f"    batch error: {str(e)[:200]}")
    return total, errs

def upsert_e(etype, src_t, tgt_t, rows):
    batch, total, errs = [], 0, 0
    for src, tgt, attrs in rows:
        clean = {k: v for k, v in attrs.items() if v is not None}
        batch.append((src, tgt, clean))
        if len(batch) >= BATCH:
            try:
                conn.upsertEdges(etype, src_t, tgt_t, batch); total += len(batch)
            except Exception as e:
                errs += 1
                if errs <= 5: print(f"    batch error: {str(e)[:200]}")
            batch = []
    if batch:
        try:
            conn.upsertEdges(etype, src_t, tgt_t, batch); total += len(batch)
        except Exception as e:
            errs += 1; print(f"    batch error: {str(e)[:200]}")
    return total, errs

def step(label, fn):
    print(f"\n--- {label} ---")
    t0 = time.time()
    total, errs = fn()
    print(f"  loaded {total}   ({errs} failed batches)   in {time.time()-t0:.1f}s")

# ---------- VERTICES ----------

step("Customer", lambda: upsert_v("Customer", (
    (r["customer_id"], {
        "transaction_count": i(r["transaction_count"]),
        "total_amount":      f(r["total_amount"]),
        "avg_amount":        f(r["avg_amount"]),
        "max_risk_score":    f(r["max_risk_score"]),
        "avg_risk_score":    f(r["avg_risk_score"]),
    }) for r in read_csv("customers/customers.csv")
)))

step("Transaction", lambda: upsert_v("Transaction", (
    (r["TransactionID"], {
        "transaction_dt":        i(r["TransactionDT"]),
        "transaction_amount":    f(r["TransactionAmt"]),
        "product_code":          s(r["ProductCD"]),
        "card1": s(r["card1"]), "card2": s(r["card2"]), "card3": s(r["card3"]),
        "card4": s(r["card4"]), "card5": s(r["card5"]), "card6": s(r["card6"]),
        "addr1": s(r["addr1"]), "addr2": s(r["addr2"]),
        "dist1": f(r["dist1"]), "dist2": f(r["dist2"]),
        "p_email_domain":        s(r["P_emaildomain"]),
        "r_email_domain":        s(r["R_emaildomain"]),
        "transaction_timestamp": dt(r["ts"]),
        "channel":               s(r["channel"]),
        "risk_score":            f(r["risk_score"]),
    }) for r in read_csv("transactions/transactions.csv")
)))

step("Card", lambda: upsert_v("Card", (
    (r["card_key"], {
        "card1": s(r["card1"]), "card2": s(r["card2"]), "card3": s(r["card3"]),
        "card4": s(r["card4"]), "card5": s(r["card5"]), "card6": s(r["card6"]),
    }) for r in read_csv("cards/cards.csv")
)))

ID_COLS = ["id_01","id_02","id_03","id_04","id_05","id_06",
           "id_12","id_13","id_14",
           "id_30","id_31","id_32","id_33","id_34","id_35","id_36","id_37","id_38"]

step("Identity", lambda: upsert_v("Identity", (
    (r["TransactionID"], {
        **{k: f(r.get(k)) for k in ID_COLS},
        "device_type": s(r.get("DeviceType")),
        "device_info": s(r.get("DeviceInfo")),
    }) for r in read_csv("identities/identities.csv")
)))

step("Device", lambda: upsert_v("Device", (
    (r["device_key"], {
        "device_type": s(r.get("DeviceType")),
        "device_info": s(r.get("DeviceInfo")),
    }) for r in read_csv("devices/devices.csv")
)))

step("HistoricalCase", lambda: upsert_v("HistoricalCase", (
    (r["case_id"], {
        "customer_id":         s(r["customer_id"]),
        "card_id":             s(r["card_id"]),
        "opened_at":           dt(r["opened_at"]),
        "closed_at":           dt(r["closed_at"]),
        "outcome":             s(r["outcome"]),
        "pattern":             s(r["pattern"]),
        "first_fraud_txn_id":  s(r["first_fraud_txn_id"]),
        "txn_ids":             s(r["txn_ids"]),
        "n_txns":              i(r["n_txns"]),
        "exposure_usd":        f(r["exposure_usd"]),
        "connected_card_ids":  s(r["connected_card_ids"]),
        "actions_taken":       s(r["actions_taken"]),
        "report_filed":        (r["report_filed"].strip().lower() == "yes"),
        "analyst_notes":       s(r["analyst_notes"]),
    }) for r in read_csv("cases/historical_cases.csv")
)))

step("Case", lambda: upsert_v("Case", (
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

# ---------- EDGES ----------

step("CustomerMakesTransaction", lambda: upsert_e(
    "CustomerMakesTransaction", "Customer", "Transaction",
    ((r["customer_id"], r["transaction_id"], {}) for r in read_csv("edges/customer_makes_transaction.csv"))
))

step("TransactionUsesCard", lambda: upsert_e(
    "TransactionUsesCard", "Transaction", "Card",
    ((r["transaction_id"], r["card_key"], {}) for r in read_csv("edges/transaction_uses_card.csv"))
))

step("TransactionHasIdentity", lambda: upsert_e(
    "TransactionHasIdentity", "Transaction", "Identity",
    ((r["transaction_id"], r["transaction_id"], {}) for r in read_csv("edges/transaction_has_identity.csv"))
))

step("TransactionUsesDevice", lambda: upsert_e(
    "TransactionUsesDevice", "Transaction", "Device",
    ((r["transaction_id"], r["device_key"], {}) for r in read_csv("edges/transaction_uses_device.csv"))
))

step("CaseFlagsTransaction", lambda: upsert_e(
    "CaseFlagsTransaction", "Case", "Transaction",
    ((r["case_id"], r["transaction_id"], {}) for r in read_csv("edges/case_flags_transaction.csv"))
))

step("CaseInvolvesCustomer", lambda: upsert_e(
    "CaseInvolvesCustomer", "Case", "Customer",
    ((r["case_id"], r["customer_id"], {}) for r in read_csv("edges/case_involves_customer.csv"))
))

step("HistoricalCaseInvolvesCustomer", lambda: upsert_e(
    "HistoricalCaseInvolvesCustomer", "HistoricalCase", "Customer",
    ((r["case_id"], r["customer_id"], {}) for r in read_csv("edges/historical_case_customer.csv"))
))

print("\n=== Final counts ===")
for vt in ("Customer","Transaction","Card","Identity","Device","Case","HistoricalCase"):
    try:
        print(f"  {vt}: {conn.getVertexCount(vt)}")
    except Exception as e:
        print(f"  {vt}: ERROR {e}")
print("\nDONE.")