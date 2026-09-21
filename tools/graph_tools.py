from pathlib import Path
from typing import Any
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]

TRANSACTION_FILE = (
    ROOT / "data" / "processed" / "transactions" / "transactions.csv"
)

DEVICE_FILE = (
    ROOT / "data" / "processed" / "devices" / "devices.csv"
)

DEVICE_EDGE_FILE = (
    ROOT / "data" / "processed" / "edges" / "transaction_uses_device.csv"
)


class GraphTools:
    """
    Local graph-style investigation tools.

    These tools currently use the processed CSV files as a local
    graph representation. Later, the same interface can be connected
    to TigerGraph.
    """

    def __init__(
        self,
        transaction_file: Path = TRANSACTION_FILE,
        device_file: Path = DEVICE_FILE,
        device_edge_file: Path = DEVICE_EDGE_FILE,
    ):
        self.transaction_file = Path(transaction_file)
        self.device_file = Path(device_file)
        self.device_edge_file = Path(device_edge_file)

        self._transactions: pd.DataFrame | None = None
        self._devices: pd.DataFrame | None = None
        self._device_edges: pd.DataFrame | None = None

    # DATA LOADING
    
    def _load_transactions(self) -> pd.DataFrame:
        """Load processed transaction data lazily."""

        if self._transactions is None:
            if not self.transaction_file.exists():
                raise FileNotFoundError(
                    f"Transaction file not found: {self.transaction_file}"
                )

            self._transactions = pd.read_csv(
                self.transaction_file,
                low_memory=False,
            )

        return self._transactions

    def _load_devices(self) -> pd.DataFrame:
        """Load processed device data lazily."""

        if self._devices is None:
            if not self.device_file.exists():
                raise FileNotFoundError(
                    f"Device file not found: {self.device_file}"
                )

            self._devices = pd.read_csv(
                self.device_file,
                low_memory=False,
            )

        return self._devices

    def _load_device_edges(self) -> pd.DataFrame:
        """Load transaction -> device relationships lazily."""

        if self._device_edges is None:
            if not self.device_edge_file.exists():
                raise FileNotFoundError(
                    f"Device edge file not found: {self.device_edge_file}"
                )

            self._device_edges = pd.read_csv(
                self.device_edge_file,
                low_memory=False,
            )

        return self._device_edges

    # CUSTOMER NETWORK
    
    def get_customer_network(
        self,
        customer_id: str,
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        Build a network-style summary around a customer.

        Includes:
        - transaction count
        - cards
        - devices
        - email domains
        - channels
        - recent transactions
        """

        transactions = self._load_transactions()

        customer_transactions = transactions[
            transactions["customer_id"].astype(str)
            == str(customer_id)
        ].copy()

        if customer_transactions.empty:
            return {
                "customer_id": str(customer_id),
                "transaction_count": 0,
                "cards": [],
                "devices": [],
                "email_domains": [],
                "channels": [],
                "recent_transactions": [],
            }

        # Cards
       
        card_columns = [
            "card1",
            "card2",
            "card3",
            "card4",
            "card5",
            "card6",
        ]

        available_card_columns = [
            column
            for column in card_columns
            if column in customer_transactions.columns
        ]

        cards: list[str] = []

        if available_card_columns:
            card_values = (
                customer_transactions[available_card_columns]
                .astype(str)
                .fillna("")
            )

            for _, row in card_values.iterrows():
                values = []

                for column in available_card_columns:
                    value = row[column]

                    if value and value.lower() != "nan":
                        values.append(value)

                if values:
                    cards.append("|".join(values))

        cards = sorted(set(cards))

        # Devices
       
        transaction_ids = set(
            customer_transactions["TransactionID"]
            .dropna()
            .astype(str)
        )

        device_edges = self._load_device_edges()

        customer_device_edges = device_edges[
            device_edges["transaction_id"]
            .astype(str)
            .isin(transaction_ids)
        ]

        devices = sorted(
            set(
                customer_device_edges["device_key"]
                .dropna()
                .astype(str)
            )
        )

        # Email domains
       
        email_domains: set[str] = set()

        for column in [
            "P_emaildomain",
            "R_emaildomain",
        ]:
            if column not in customer_transactions.columns:
                continue

            values = (
                customer_transactions[column]
                .dropna()
                .astype(str)
            )

            email_domains.update(
                value
                for value in values
                if value and value.lower() != "nan"
            )

        # Channels
        
        channels: list[str] = []

        if "channel" in customer_transactions.columns:
            channels = sorted(
                set(
                    customer_transactions["channel"]
                    .dropna()
                    .astype(str)
                )
            )

        # Recent transactions
       
        recent_transactions = customer_transactions.copy()

        if "ts" in recent_transactions.columns:
            recent_transactions["ts"] = pd.to_datetime(
                recent_transactions["ts"],
                errors="coerce",
            )

            recent_transactions = recent_transactions.sort_values(
                "ts",
                ascending=False,
            )

        recent_transactions = recent_transactions.head(limit)

        recent_transactions_list = [
            {
                key: self._clean_value(value)
                for key, value in row.items()
            }
            for row in recent_transactions.to_dict(
                orient="records"
            )
        ]

        return {
            "customer_id": str(customer_id),
            "transaction_count": int(
                len(customer_transactions)
            ),
            "cards": cards,
            "devices": devices,
            "email_domains": sorted(email_domains),
            "channels": channels,
            "recent_transactions": recent_transactions_list,
        }

    # CARD NETWORK
    
    def get_card_network(
        self,
        card_key: str,
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        Find customers and transactions connected to a card key.
        """

        transactions = self._load_transactions()

        if "card_key" not in transactions.columns:
            return {
                "card_key": str(card_key),
                "transaction_count": 0,
                "customers": [],
                "transactions": [],
            }

        matches = transactions[
            transactions["card_key"].astype(str)
            == str(card_key)
        ].copy()

        if matches.empty:
            return {
                "card_key": str(card_key),
                "transaction_count": 0,
                "customers": [],
                "transactions": [],
            }

        customers = sorted(
            set(
                matches["customer_id"]
                .dropna()
                .astype(str)
            )
        )

        if "ts" in matches.columns:
            matches["ts"] = pd.to_datetime(
                matches["ts"],
                errors="coerce",
            )

            matches = matches.sort_values(
                "ts",
                ascending=False,
            )

        matches = matches.head(limit)

        transaction_list = [
            {
                key: self._clean_value(value)
                for key, value in row.items()
            }
            for row in matches.to_dict(
                orient="records"
            )
        ]

        return {
            "card_key": str(card_key),
            "transaction_count": int(
                len(
                    transactions[
                        transactions["card_key"].astype(str)
                        == str(card_key)
                    ]
                )
            ),
            "customers": customers,
            "transactions": transaction_list,
        }

    # DEVICE NETWORK
   
    def get_device_network(
        self,
        device_key: str,
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        Find transactions and customers connected to a device.

        Important:
        device_key represents a device fingerprint/signature
        from the processed dataset. It does not necessarily mean
        the same physical device.
        """

        transactions = self._load_transactions()
        device_edges = self._load_device_edges()

        matching_edges = device_edges[
            device_edges["device_key"].astype(str)
            == str(device_key)
        ].copy()

        if matching_edges.empty:
            return {
                "device_key": str(device_key),
                "transaction_count": 0,
                "customers": [],
                "transactions": [],
            }

        transaction_ids = set(
            matching_edges["transaction_id"]
            .dropna()
            .astype(str)
        )

        matches = transactions[
            transactions["TransactionID"]
            .astype(str)
            .isin(transaction_ids)
        ].copy()

        if matches.empty:
            return {
                "device_key": str(device_key),
                "transaction_count": 0,
                "customers": [],
                "transactions": [],
            }

        customers = sorted(
            set(
                matches["customer_id"]
                .dropna()
                .astype(str)
            )
        )

        if "ts" in matches.columns:
            matches["ts"] = pd.to_datetime(
                matches["ts"],
                errors="coerce",
            )

            matches = matches.sort_values(
                "ts",
                ascending=False,
            )

        matches = matches.head(limit)

        transaction_list = [
            {
                key: self._clean_value(value)
                for key, value in row.items()
            }
            for row in matches.to_dict(
                orient="records"
            )
        ]

        return {
            "device_key": str(device_key),
            "transaction_count": int(
                len(transaction_ids)
            ),
            "customers": customers,
            "transactions": transaction_list,
        }

    # SHARED CARD CONNECTIONS
    
    def find_connected_customers(
        self,
        customer_id: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Find other customers connected through shared card keys.

        Path:

        Customer
            -> Transaction
            -> Card
            -> Transaction
            -> Customer
        """

        transactions = self._load_transactions()

        customer_transactions = transactions[
            transactions["customer_id"].astype(str)
            == str(customer_id)
        ].copy()

        if customer_transactions.empty:
            return []

        if "card_key" not in customer_transactions.columns:
            return []

        customer_cards = set(
            customer_transactions["card_key"]
            .dropna()
            .astype(str)
        )

        # Ignore incomplete card keys.
        customer_cards = {
            card
            for card in customer_cards
            if card.count("|") == 5
            and all(part.strip() for part in card.split("|"))
        }

        if not customer_cards:
            return []

        connected_transactions = transactions[
            transactions["card_key"]
            .astype(str)
            .isin(customer_cards)
            & (
                transactions["customer_id"]
                .astype(str)
                != str(customer_id)
            )
        ].copy()

        if connected_transactions.empty:
            return []

        grouped = (
            connected_transactions
            .groupby("customer_id")
            .agg(
                shared_card_transactions=(
                    "TransactionID",
                    "count",
                ),
                maximum_risk_score=(
                    "risk_score",
                    "max",
                ),
                average_risk_score=(
                    "risk_score",
                    "mean",
                ),
                total_amount=(
                    "TransactionAmt",
                    "sum",
                ),
            )
            .reset_index()
        )

        grouped = grouped.sort_values(
            [
                "shared_card_transactions",
                "maximum_risk_score",
            ],
            ascending=False,
        ).head(limit)

        return [
            {
                key: self._clean_value(value)
                for key, value in row.items()
            }
            for row in grouped.to_dict(
                orient="records"
            )
        ]

    # SHARED DEVICE CONNECTIONS
   
    def find_connected_customers_by_device(
        self,
        customer_id: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Find other customers connected through shared devices.

        Path:

        Customer
            -> Transaction
            -> Device
            -> Transaction
            -> Customer

        Returns the specific device responsible for each
        customer-to-customer connection.

        The device is a fingerprint/signature from the dataset,
        so it should not automatically be interpreted as proof
        of the same physical device.
        """

        transactions = self._load_transactions()
        device_edges = self._load_device_edges()

        # Get transactions belonging to target customer
        
        customer_transactions = transactions[
            transactions["customer_id"].astype(str)
            == str(customer_id)
        ].copy()

        if customer_transactions.empty:
            return []

        customer_transaction_ids = set(
            customer_transactions["TransactionID"]
            .dropna()
            .astype(str)
        )

        # Find devices used by target customer
       
        customer_device_edges = device_edges[
            device_edges["transaction_id"]
            .astype(str)
            .isin(customer_transaction_ids)
        ].copy()

        if customer_device_edges.empty:
            return []

        customer_devices = set(
            customer_device_edges["device_key"]
            .dropna()
            .astype(str)
        )

        if not customer_devices:
            return []

        # Find all transactions using those devices
        
        connected_edges = device_edges[
            device_edges["device_key"]
            .astype(str)
            .isin(customer_devices)
        ].copy()

        if connected_edges.empty:
            return []

        connected_transaction_ids = set(
            connected_edges["transaction_id"]
            .dropna()
            .astype(str)
        )

        # Get transactions of OTHER customers
        
        connected_transactions = transactions[
            transactions["TransactionID"]
            .astype(str)
            .isin(connected_transaction_ids)
            & (
                transactions["customer_id"]
                .astype(str)
                != str(customer_id)
            )
        ].copy()

        if connected_transactions.empty:
            return []

        # Normalize transaction IDs for merge
       
        connected_transactions[
            "transaction_id_str"
        ] = (
            connected_transactions["TransactionID"]
            .astype(str)
        )

        connected_edges[
            "transaction_id_str"
        ] = (
            connected_edges["transaction_id"]
            .astype(str)
        )

        # Attach device_key to every connected transaction
       
        connected_transactions = connected_transactions.merge(
            connected_edges[
                [
                    "transaction_id_str",
                    "device_key",
                ]
            ].drop_duplicates(),
            on="transaction_id_str",
            how="inner",
        )

        if connected_transactions.empty:
            return []

        # Aggregate by customer + specific device
       
        grouped = (
            connected_transactions
            .groupby(
                [
                    "customer_id",
                    "device_key",
                ]
            )
            .agg(
                shared_transactions=(
                    "TransactionID",
                    "count",
                ),
                maximum_risk_score=(
                    "risk_score",
                    "max",
                ),
                average_risk_score=(
                    "risk_score",
                    "mean",
                ),
                total_amount=(
                    "TransactionAmt",
                    "sum",
                ),
            )
            .reset_index()
        )

        # Sort strongest connections first
      
        grouped = grouped.sort_values(
            [
                "shared_transactions",
                "maximum_risk_score",
            ],
            ascending=False,
        ).head(limit)

        # Return clean dictionaries
       
        return [
            {
                key: self._clean_value(value)
                for key, value in row.items()
            }
            for row in grouped.to_dict(
                orient="records"
            )
        ]

    # DEVICE RARITY
   
    def get_device_rarity(
        self,
        device_key: str,
    ) -> dict[str, Any]:
        """
        Determine how widely a device fingerprint is shared.

        This is useful because a common fingerprint such as
        'desktop|Windows' should not be treated as strong
        evidence of a fraud connection.
        """

        transactions = self._load_transactions()
        device_edges = self._load_device_edges()

        matching_edges = device_edges[
            device_edges["device_key"].astype(str)
            == str(device_key)
        ].copy()

        if matching_edges.empty:
            return {
                "device_key": str(device_key),
                "transaction_count": 0,
                "customer_count": 0,
                "customers": [],
                "rarity": "unknown",
            }

        transaction_ids = set(
            matching_edges["transaction_id"]
            .dropna()
            .astype(str)
        )

        matches = transactions[
            transactions["TransactionID"]
            .astype(str)
            .isin(transaction_ids)
        ]

        customers = sorted(
            set(
                matches["customer_id"]
                .dropna()
                .astype(str)
            )
        )

        customer_count = len(customers)

        # These thresholds are intentionally simple for the
        # current local investigation tool.
        if customer_count <= 1:
            rarity = "unique"
        elif customer_count <= 3:
            rarity = "rare"
        elif customer_count <= 10:
            rarity = "moderately_shared"
        else:
            rarity = "common"

        return {
            "device_key": str(device_key),
            "transaction_count": int(
                len(transaction_ids)
            ),
            "customer_count": int(customer_count),
            "customers": customers,
            "rarity": rarity,
        }

    # COMPLETE CUSTOMER INVESTIGATION NETWORK
   
    def get_investigation_network(
        self,
        customer_id: str,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Build a consolidated investigation network for a customer.

        This combines:

        - customer summary/network
        - shared-card customers
        - shared-device customers
        - device rarity
        - high-risk transactions

        This will later become one of the main tools used by
        the Fraud Investigation Agent.
        """

        transactions = self._load_transactions()

        customer_transactions = transactions[
            transactions["customer_id"].astype(str)
            == str(customer_id)
        ].copy()

        if customer_transactions.empty:
            return {
                "customer_id": str(customer_id),
                "found": False,
                "customer_network": {},
                "connected_by_card": [],
                "connected_by_device": [],
                "device_rarity": [],
                "high_risk_transactions": [],
            }

        customer_network = self.get_customer_network(
            customer_id=customer_id,
            limit=limit,
        )

        connected_by_card = self.find_connected_customers(
            customer_id=customer_id,
            limit=limit,
        )

        connected_by_device = (
            self.find_connected_customers_by_device(
                customer_id=customer_id,
                limit=limit,
            )
        )

        # Device rarity for devices used by this customer
       
        device_rarity = []

        for device_key in customer_network.get(
            "devices",
            [],
        )[:limit]:

            rarity = self.get_device_rarity(
                device_key
            )

            device_rarity.append(rarity)

        # High-risk customer transactions
      
        if "risk_score" in customer_transactions.columns:

            risk_values = pd.to_numeric(
                customer_transactions["risk_score"],
                errors="coerce",
            )

            high_risk = customer_transactions[
                risk_values >= 0.8
            ].copy()

            high_risk = high_risk.sort_values(
                "risk_score",
                ascending=False,
            ).head(limit)

        else:
            high_risk = customer_transactions.head(0)

        high_risk_transactions = [
            {
                key: self._clean_value(value)
                for key, value in row.items()
            }
            for row in high_risk.to_dict(
                orient="records"
            )
        ]

        return {
            "customer_id": str(customer_id),
            "found": True,
            "customer_network": customer_network,
            "connected_by_card": connected_by_card,
            "connected_by_device": connected_by_device,
            "device_rarity": device_rarity,
            "high_risk_transactions": high_risk_transactions,
        }

    # UTILITY
    
    @staticmethod
    def _clean_value(value: Any) -> Any:
        """
        Convert pandas/numpy values into JSON-friendly values.
        """

        if pd.isna(value):
            return None

        if hasattr(value, "item"):
            try:
                return value.item()
            except (ValueError, TypeError):
                pass

        if isinstance(value, pd.Timestamp):
            return value.isoformat()

        return value


# ================================================================
# FACTORY
# ================================================================

def get_graph_tools() -> GraphTools:
    """Return a GraphTools instance."""

    return GraphTools()