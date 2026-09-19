"""
Prepare HHGOA / IEEE fraud dataset for TigerGraph.

Input:
    data/raw/HHGOA_IEEE/

Output:
    data/processed/transactions/
    data/processed/customers/
    data/processed/cards/
    data/processed/devices/
    data/processed/identities/
    data/processed/cases/
    data/processed/edges/
"""

from pathlib import Path
import pandas as pd

# PATHS

ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = ROOT / "data" / "raw" / "HHGOA_IEEE"
OUT_DIR = ROOT / "data" / "processed"

TRANSACTION_DIR = OUT_DIR / "transactions"
CUSTOMER_DIR = OUT_DIR / "customers"
CARD_DIR = OUT_DIR / "cards"
DEVICE_DIR = OUT_DIR / "devices"
IDENTITY_DIR = OUT_DIR / "identities"
CASE_DIR = OUT_DIR / "cases"
EDGE_DIR = OUT_DIR / "edges"


def create_directories():
    """Create all processed-data directories."""

    for directory in [
        TRANSACTION_DIR,
        CUSTOMER_DIR,
        CARD_DIR,
        DEVICE_DIR,
        IDENTITY_DIR,
        CASE_DIR,
        EDGE_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)

# TRANSACTIONS

def prepare_transactions():
    print("Loading transactions...")

    columns = [
        "TransactionID",
        "TransactionDT",
        "TransactionAmt",
        "ProductCD",
        "card1",
        "card2",
        "card3",
        "card4",
        "card5",
        "card6",
        "addr1",
        "addr2",
        "dist1",
        "dist2",
        "P_emaildomain",
        "R_emaildomain",
        "customer_id",
        "ts",
        "channel",
        "risk_score",
    ]

    df = pd.read_csv(
        RAW_DIR / "transactions.csv",
        usecols=columns
    )

    # Make transaction ID a string.
    df["TransactionID"] = df["TransactionID"].astype(str)

    # Customer IDs are already present in the prepared dataset.
    df["customer_id"] = df["customer_id"].astype(str)

    # Transaction timestamp.
    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")

    # Create a stable transaction-card key.
    card_columns = [
        "card1",
        "card2",
        "card3",
        "card4",
        "card5",
        "card6",
    ]

    df["card_key"] = (
        df[card_columns]
        .fillna("")
        .astype(str)
        .agg("|".join, axis=1)
    )

    # Avoid creating a card vertex for completely missing card data.
    df.loc[
        df[card_columns].isna().all(axis=1),
        "card_key"
    ] = None

    output = TRANSACTION_DIR / "transactions.csv"

    df.to_csv(output, index=False)

    print(f"Transactions written: {len(df):,}")
    print(f"Output: {output}")

    return df

# CUSTOMERS

def prepare_customers(transactions):
    print("Preparing customers...")

    customers = (
        transactions[
            [
                "customer_id",
            ]
        ]
        .dropna()
        .drop_duplicates()
        .copy()
    )

    customers["customer_id"] = customers["customer_id"].astype(str)

    # Basic aggregate information useful to the investigation agent.
    stats = (
        transactions
        .groupby("customer_id")
        .agg(
            transaction_count=("TransactionID", "count"),
            total_amount=("TransactionAmt", "sum"),
            avg_amount=("TransactionAmt", "mean"),
            max_risk_score=("risk_score", "max"),
            avg_risk_score=("risk_score", "mean"),
        )
        .reset_index()
    )

    customers = customers.merge(
        stats,
        on="customer_id",
        how="left"
    )

    output = CUSTOMER_DIR / "customers.csv"

    customers.to_csv(output, index=False)

    print(f"Customers written: {len(customers):,}")

    return customers

# CARDS

def prepare_cards(transactions):
    print("Preparing cards...")

    card_columns = [
        "card1",
        "card2",
        "card3",
        "card4",
        "card5",
        "card6",
    ]

    cards = (
        transactions[
            ["card_key"] + card_columns
        ]
        .dropna(subset=["card_key"])
        .drop_duplicates(subset=["card_key"])
        .copy()
    )

    cards["card_key"] = cards["card_key"].astype(str)

    output = CARD_DIR / "cards.csv"

    cards.to_csv(output, index=False)

    print(f"Cards written: {len(cards):,}")

    return cards

# IDENTITY / DEVICE

def prepare_identity():
    print("Loading identity data...")

    columns = [
        "TransactionID",
        "id_01",
        "id_02",
        "id_03",
        "id_04",
        "id_05",
        "id_06",
        "id_12",
        "id_13",
        "id_14",
        "id_30",
        "id_31",
        "id_32",
        "id_33",
        "id_34",
        "id_35",
        "id_36",
        "id_37",
        "id_38",
        "DeviceType",
        "DeviceInfo",
    ]

    df = pd.read_csv(
        RAW_DIR / "identity.csv",
        usecols=columns
    )

    df["TransactionID"] = df["TransactionID"].astype(str)

    output = IDENTITY_DIR / "identities.csv"

    df.to_csv(output, index=False)

    print(f"Identity records written: {len(df):,}")

    return df


def prepare_devices(identity):
    print("Preparing devices...")

    devices = identity[
        [
            "DeviceType",
            "DeviceInfo",
        ]
    ].dropna(
        how="all"
    ).drop_duplicates().copy()

    # Create stable device ID.
    devices["device_key"] = (
        devices["DeviceType"]
        .fillna("UNKNOWN")
        .astype(str)
        + "|"
        + devices["DeviceInfo"]
        .fillna("UNKNOWN")
        .astype(str)
    )

    devices = devices[
        [
            "device_key",
            "DeviceType",
            "DeviceInfo",
        ]
    ]

    output = DEVICE_DIR / "devices.csv"

    devices.to_csv(output, index=False)

    print(f"Devices written: {len(devices):,}")

    return devices

# CASES

def prepare_cases():
    print("Preparing benchmark cases...")

    cases = pd.read_csv(
        RAW_DIR / "case_pack.csv"
    )

    cases["case_id"] = cases["case_id"].astype(str)
    cases["flagged_txn_id"] = cases["flagged_txn_id"].astype(str)
    cases["customer_id"] = cases["customer_id"].astype(str)

    output = CASE_DIR / "benchmark_cases.csv"

    cases.to_csv(output, index=False)

    print(f"Benchmark cases written: {len(cases):,}")

    return cases


def prepare_historical_cases():
    print("Preparing historical cases...")

    cases = pd.read_csv(
        RAW_DIR / "closed_cases_history.csv"
    )

    cases["case_id"] = cases["case_id"].astype(str)
    cases["customer_id"] = cases["customer_id"].astype(str)
    cases["card_id"] = cases["card_id"].astype(str)

    output = CASE_DIR / "historical_cases.csv"

    cases.to_csv(output, index=False)

    print(f"Historical cases written: {len(cases):,}")

    return cases

# EDGES

def prepare_edges(transactions, identity, cases, historical_cases):
    print("Preparing graph edges...")

    
    # Customer -> Transaction
   
    customer_transaction = transactions[
        [
            "customer_id",
            "TransactionID",
        ]
    ].dropna()

    customer_transaction.columns = [
        "customer_id",
        "transaction_id",
    ]

    customer_transaction.to_csv(
        EDGE_DIR / "customer_makes_transaction.csv",
        index=False
    )

    # Transaction -> Card
    
    transaction_card = transactions[
        [
            "TransactionID",
            "card_key",
        ]
    ].dropna()

    transaction_card.columns = [
        "transaction_id",
        "card_key",
    ]

    transaction_card.to_csv(
        EDGE_DIR / "transaction_uses_card.csv",
        index=False
    )

    # Transaction -> Identity
    
    transaction_identity = identity[
        ["TransactionID"]
    ].drop_duplicates()

    transaction_identity.columns = [
        "transaction_id"
    ]

    transaction_identity.to_csv(
        EDGE_DIR / "transaction_has_identity.csv",
        index=False
    )

    # Transaction -> Device

    transaction_device = identity[
        [
            "TransactionID",
            "DeviceType",
            "DeviceInfo",
        ]
    ].copy()

    transaction_device = transaction_device.dropna(
        subset=["DeviceType", "DeviceInfo"],
        how="all"
    )

    transaction_device["device_key"] = (
        transaction_device["DeviceType"]
        .fillna("UNKNOWN")
        .astype(str)
        + "|"
        + transaction_device["DeviceInfo"]
        .fillna("UNKNOWN")
        .astype(str)
    )

    transaction_device = transaction_device[
        [
            "TransactionID",
            "device_key",
        ]
    ].drop_duplicates()

    transaction_device.columns = [
        "transaction_id",
        "device_key",
    ]

    transaction_device.to_csv(
        EDGE_DIR / "transaction_uses_device.csv",
        index=False
    )

    # Benchmark Case -> Transaction

    case_transaction = cases[
        [
            "case_id",
            "flagged_txn_id",
        ]
    ].copy()

    case_transaction.columns = [
        "case_id",
        "transaction_id",
    ]

    case_transaction.to_csv(
        EDGE_DIR / "case_flags_transaction.csv",
        index=False
    )

    # Benchmark Case -> Customer

    case_customer = cases[
        [
            "case_id",
            "customer_id",
        ]
    ].dropna()

    case_customer.to_csv(
        EDGE_DIR / "case_involves_customer.csv",
        index=False
    )

    # --------------------------------------------------------
    # Historical Case -> Customer
    # --------------------------------------------------------

    historical_customer = historical_cases[
        [
            "case_id",
            "customer_id",
        ]
    ].dropna()

    historical_customer.to_csv(
        EDGE_DIR / "historical_case_customer.csv",
        index=False
    )

    print("Graph edge files created.")

# MAIN

def main():
    print("=" * 60)
    print("HHGOA DATA PREPARATION")
    print("=" * 60)

    create_directories()

    transactions = prepare_transactions()

    prepare_customers(transactions)

    prepare_cards(transactions)

    identity = prepare_identity()

    prepare_devices(identity)

    cases = prepare_cases()

    historical_cases = prepare_historical_cases()

    prepare_edges(
        transactions,
        identity,
        cases,
        historical_cases,
    )

    print()
    print("=" * 60)
    print("DATA PREPARATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()