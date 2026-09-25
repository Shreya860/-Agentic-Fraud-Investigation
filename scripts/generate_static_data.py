import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
PUBLIC = ROOT / "frontend" / "public" / "api"


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_json(name, value):
    target = PUBLIC / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, separators=(",", ":")), encoding="utf-8")


def parse_date(value):
    try:
        return datetime.fromisoformat(value.replace(" ", "T"))
    except (AttributeError, ValueError):
        return None


def build_graph():
    seed = "C06075"
    transactions = read_csv(DATA / "transactions" / "transactions.csv")
    customer_edges = read_csv(DATA / "edges" / "customer_makes_transaction.csv")
    card_edges = read_csv(DATA / "edges" / "transaction_uses_card.csv")
    device_edges = read_csv(DATA / "edges" / "transaction_uses_device.csv")
    history_edges = read_csv(DATA / "edges" / "historical_case_customer.csv")
    history = read_csv(DATA / "cases" / "historical_cases.csv")

    seed_txn_ids = {
        row["transaction_id"]
        for row in customer_edges
        if row["customer_id"] == seed
    }
    transactions_by_id = {row["TransactionID"]: row for row in transactions}
    seed_transactions = sorted(
        (transactions_by_id[txn_id] for txn_id in seed_txn_ids if txn_id in transactions_by_id),
        key=lambda row: float(row.get("risk_score") or 0),
        reverse=True,
    )[:30]
    selected_txn_ids = {row["TransactionID"] for row in seed_transactions}

    cards_by_txn = {
        row["transaction_id"]: row["card_key"]
        for row in card_edges
        if row["transaction_id"] in selected_txn_ids
    }
    devices_by_txn = {
        row["transaction_id"]: row["device_key"]
        for row in device_edges
        if row["transaction_id"] in selected_txn_ids and row.get("device_key")
    }

    all_txns_by_card = defaultdict(set)
    all_txns_by_device = defaultdict(set)
    for row in card_edges:
        all_txns_by_card[row["card_key"]].add(row["transaction_id"])
    for row in device_edges:
        if row.get("device_key"):
            all_txns_by_device[row["device_key"]].add(row["transaction_id"])
    txn_to_customer = {
        row["transaction_id"]: row["customer_id"] for row in customer_edges
    }

    co_customers = set()
    for card_key in set(cards_by_txn.values()):
        co_customers.update(
            txn_to_customer[txn_id]
            for txn_id in all_txns_by_card[card_key]
            if txn_id in txn_to_customer and txn_to_customer[txn_id] != seed
        )
    for device_key in set(devices_by_txn.values()):
        co_customers.update(
            txn_to_customer[txn_id]
            for txn_id in all_txns_by_device[device_key]
            if txn_id in txn_to_customer and txn_to_customer[txn_id] != seed
        )
    co_customers = sorted(co_customers)[:5]

    historical_ids = [
        row["case_id"] for row in history_edges if row["customer_id"] == seed
    ][:5]
    historical_by_id = {row["case_id"]: row for row in history}

    node_specs = [(f"customer:{seed}", seed, "customer")]
    node_specs += [
        (f"transaction:{row['TransactionID']}", row["TransactionID"], "transaction")
        for row in seed_transactions
    ]
    node_specs += [
        (f"card:{key}", key, "card") for key in sorted(set(cards_by_txn.values()))
    ]
    node_specs += [
        (f"device:{key}", key, "device") for key in sorted(set(devices_by_txn.values()))
    ]
    node_specs += [
        (f"customer:{customer_id}", customer_id, "customer")
        for customer_id in co_customers
    ]
    node_specs += [
        (f"case:{case_id}", case_id, "case")
        for case_id in historical_ids
        if case_id in historical_by_id
    ]

    nodes = []
    total = max(1, len(node_specs))
    for index, (node_id, label, node_type) in enumerate(node_specs):
        if node_type == "customer" and label == seed:
            x, y = 0.5, 0.5
        else:
            angle = (index / total) * 6.283185307179586
            x = 0.5 + 0.38 * __import__("math").cos(angle)
            y = 0.5 + 0.38 * __import__("math").sin(angle)
        nodes.append({"id": node_id, "label": label, "type": node_type, "x": round(x, 4), "y": round(y, 4)})

    edges = []
    edge_index = 0

    def add_edge(from_id, to_id, label):
        nonlocal edge_index
        edge_index += 1
        edges.append({"id": f"graph-edge-{edge_index}", "from": from_id, "to": to_id, "label": label})

    for row in seed_transactions:
        txn_id = row["TransactionID"]
        txn_node = f"transaction:{txn_id}"
        add_edge(f"customer:{seed}", txn_node, "makes transaction")
        if txn_id in cards_by_txn:
            add_edge(txn_node, f"card:{cards_by_txn[txn_id]}", "uses card")
        if txn_id in devices_by_txn:
            add_edge(txn_node, f"device:{devices_by_txn[txn_id]}", "uses device")
    for case_id in historical_ids:
        if case_id in historical_by_id:
            add_edge(f"case:{case_id}", f"customer:{seed}", "involves customer")
    for customer_id in co_customers:
        shared = any(
            customer_id in {
                txn_to_customer.get(txn_id)
                for txn_id in all_txns_by_card[card_key]
            }
            for card_key in set(cards_by_txn.values())
        ) or any(
            customer_id in {
                txn_to_customer.get(txn_id)
                for txn_id in all_txns_by_device[device_key]
            }
            for device_key in set(devices_by_txn.values())
        )
        if shared:
            add_edge(f"customer:{seed}", f"customer:{customer_id}", "shares device/card with")

    return {"nodes": nodes, "edges": edges}


def build_customers():
    customers = read_csv(DATA / "customers" / "customers.csv")
    transactions = read_csv(DATA / "transactions" / "transactions.csv")
    devices = read_csv(DATA / "edges" / "transaction_uses_device.csv")
    cards = read_csv(DATA / "edges" / "transaction_uses_card.csv")
    benchmark = read_csv(DATA / "edges" / "case_involves_customer.csv")

    txns_by_customer = defaultdict(list)
    customer_by_transaction = {}
    for row in transactions:
        txns_by_customer[row["customer_id"]].append(row)
        customer_by_transaction[row["TransactionID"]] = row["customer_id"]
    devices_by_customer = defaultdict(set)
    for edge in devices:
        customer_id = customer_by_transaction.get(edge["transaction_id"])
        if customer_id and edge.get("device_key"):
            devices_by_customer[customer_id].add(edge["device_key"])
    cards_by_customer = defaultdict(set)
    for edge in cards:
        customer_id = customer_by_transaction.get(edge["transaction_id"])
        if customer_id:
            cards_by_customer[customer_id].add(edge["card_key"])
    open_cases = defaultdict(int)
    for row in benchmark:
        open_cases[row["customer_id"]] += 1

    result = []
    for row in customers:
        customer_id = row["customer_id"]
        customer_txns = txns_by_customer[customer_id]
        activity_dates = [parse_date(txn.get("ts")) for txn in customer_txns]
        activity_dates = [value for value in activity_dates if value]
        first_activity = min(activity_dates) if activity_dates else None
        last_activity = max(activity_dates) if activity_dates else None
        account_age = (
            max(0, (last_activity - first_activity).days / 365.25)
            if first_activity and last_activity
            else 0
        )
        risk_score = float(row.get("max_risk_score") or 0)
        result.append(
            {
                "customerId": customer_id,
                "name": customer_id,
                "email": "",
                "riskLevel": risk_level(risk_score),
                "riskScore": risk_score,
                "transactionCount": int(row.get("transaction_count") or 0),
                "deviceCount": len(devices_by_customer[customer_id]),
                "cardCount": len(cards_by_customer[customer_id]),
                "openCases": open_cases[customer_id],
                "lastActivity": last_activity.isoformat() if last_activity else "",
                "country": "",
                "accountAgeYears": round(account_age, 2),
            }
        )
    return result


def risk_level(score):
    if score >= 0.9:
        return "very_high"
    if score >= 0.7:
        return "high"
    if score >= 0.4:
        return "moderate"
    return "low"


def build_transactions():
    transactions = read_csv(DATA / "transactions" / "transactions.csv")
    card_edges = {
        row["transaction_id"]: row["card_key"]
        for row in read_csv(DATA / "edges" / "transaction_uses_card.csv")
    }
    device_edges = {
        row["transaction_id"]: row.get("device_key", "")
        for row in read_csv(DATA / "edges" / "transaction_uses_device.csv")
    }
    ranked = sorted(transactions, key=lambda row: float(row.get("risk_score") or 0), reverse=True)[:2000]
    result = []
    for row in ranked:
        score = float(row.get("risk_score") or 0)
        address = ":".join(
            value for value in (row.get("addr1", ""), row.get("addr2", "")) if value
        )
        result.append(
            {
                "transactionId": row["TransactionID"],
                "customerId": row["customer_id"],
                "customerName": row["customer_id"],
                "amount": float(row.get("TransactionAmt") or 0),
                "currency": "USD",
                "channel": row.get("channel") or "",
                "timestamp": row.get("ts") or "",
                "riskScore": score,
                "riskLevel": risk_level(score),
                "status": "flagged" if score >= 0.8 else "approved",
                "cardId": card_edges.get(row["TransactionID"], ""),
                "deviceId": device_edges.get(row["TransactionID"], ""),
                "merchant": row.get("ProductCD") or "",
                "location": address,
            }
        )
    return result


def build_historical_cases():
    history = read_csv(DATA / "cases" / "historical_cases.csv")[:500]
    customers = {
        row["customer_id"]: float(row.get("max_risk_score") or 0)
        for row in read_csv(DATA / "customers" / "customers.csv")
    }
    seen_by_customer = defaultdict(int)
    result = []
    for row in history:
        customer_id = row["customer_id"]
        seen_by_customer[customer_id] += 1
        outcome = "false_positive" if row["outcome"] == "cleared" else "confirmed_fraud"
        result.append(
            {
                "caseId": row["case_id"],
                "pattern": row.get("pattern") or "",
                "customerId": customer_id,
                "customerName": customer_id,
                "riskLevel": risk_level(customers.get(customer_id, 0)),
                "similarity": round(1 / seen_by_customer[customer_id], 4),
                "outcome": outcome,
                "date": row.get("opened_at") or "",
                "summary": row.get("analyst_notes") or "",
            }
        )
    return result


def build_analytics():
    with (ROOT / "benchmark_outputs" / "_summary.json").open(encoding="utf-8") as handle:
        summary = json.load(handle)
    trigger_by_case = {}
    for path in sorted((ROOT / "benchmark_outputs").glob("HHG-*.json")):
        with path.open(encoding="utf-8") as handle:
            case = json.load(handle)
        benchmark_input = case.get("benchmark_input", {})
        trigger_by_case[benchmark_input.get("case_id", case["case_id"])] = (
            benchmark_input.get("trigger_type", "unknown")
        )
    risk_distribution = defaultdict(int)
    action_distribution = defaultdict(int)
    customer_distribution = defaultdict(int)
    trigger_distribution = defaultdict(int)
    scores = []
    for row in summary:
        risk_distribution[row.get("risk_level", "low")] += 1
        action_distribution[row.get("recommended_action", "monitor_transaction")] += 1
        customer_distribution[row.get("customer_id", "")] += 1
        trigger_distribution[trigger_by_case.get(row.get("case_id"), "unknown")] += 1
        scores.append(float(row.get("risk_score") or 0))
    return {
        "riskDistribution": dict(risk_distribution),
        "recommendedActionDistribution": dict(action_distribution),
        "averageRiskScore": sum(scores) / len(scores) if scores else 0,
        "totalCases": len(summary),
        "casesPerCustomer": dict(customer_distribution),
        "casesPerTriggerType": dict(trigger_distribution),
    }


def main():
    write_json("graph.json", build_graph())
    write_json("customers.json", build_customers())
    write_json("transactions.json", build_transactions())
    write_json("historical-cases.json", build_historical_cases())
    write_json("analytics.json", build_analytics())


if __name__ == "__main__":
    main()
