from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


class FraudPatternAnalyzer:
    """
    HHGOA fraud-pattern analyzer.

    Uses:
      - processed transactions.csv
      - identity.csv joined on TransactionID

    The analyzer is deterministic and provides pattern/evidence
    information to the existing investigation pipeline.
    """

    PATTERNS = {
        "card_testing",
        "card_not_present_fraud",
        "card_not_present_new_device",
        "out_of_region_use",
        "account_takeover",
        "undocumented",
        "none",
    }

    def __init__(
        self,
        transactions_path: str | Path = (
            "data/processed/transactions/transactions.csv"
        ),
        identity_path: str | Path = (
            "data/raw/HHGOA_IEEE/identity.csv"
        ),
    ):
        self.transactions_path = Path(transactions_path)
        self.identity_path = Path(identity_path)
        self._merged: pd.DataFrame | None = None

    # ================================================================
    # DATA
    # ================================================================

    def _load_data(self) -> pd.DataFrame:
        if self._merged is not None:
            return self._merged

        transactions = pd.read_csv(self.transactions_path)
        identity = pd.read_csv(self.identity_path)

        identity_columns = [
            "TransactionID",
            "DeviceType",
            "DeviceInfo",
        ]

        identity_columns = [
            column
            for column in identity_columns
            if column in identity.columns
        ]

        identity = identity[identity_columns].copy()

        df = transactions.merge(
            identity,
            on="TransactionID",
            how="left",
        )

        df["ts"] = pd.to_datetime(
            df["ts"],
            errors="coerce",
        )

        df["DeviceType"] = (
            df["DeviceType"]
            .fillna("Unknown")
            .astype(str)
        )

        df["DeviceInfo"] = (
            df["DeviceInfo"]
            .fillna("Unknown")
            .astype(str)
        )

        self._merged = df

        return df

    # ================================================================
    # PUBLIC API
    # ================================================================

    def analyze_transaction(
        self,
        transaction_id: str | int,
    ) -> dict[str, Any]:

        df = self._load_data()

        transaction_id = str(transaction_id)

        rows = df[
            df["TransactionID"].astype(str)
            == transaction_id
        ]

        if rows.empty:
            return {
                "status": "not_found",
                "transaction_id": transaction_id,
                "customer_id": None,
                "primary_pattern": "none",
                "confidence": "low",
                "patterns": [],
                "evidence": [],
            }

        transaction = rows.iloc[0]

        customer_id = transaction.get("customer_id")

        if pd.isna(customer_id):
            customer_rows = rows.copy()
        else:
            customer_rows = df[
                df["customer_id"].astype(str)
                == str(customer_id)
            ].copy()

        patterns: list[dict[str, Any]] = []

        detectors = [
            self._detect_card_testing,
            self._detect_card_not_present_fraud,
            self._detect_card_not_present_new_device,
            self._detect_out_of_region_use,
            self._detect_account_takeover,
        ]

        for detector in detectors:
            result = detector(
                transaction,
                customer_rows,
            )

            if result is not None:
                patterns.append(result)

        # ------------------------------------------------------------
        # HHGOA fallback
        # ------------------------------------------------------------

        if not patterns:

            risk = self._number(
                transaction.get("risk_score")
            )

            amount = self._number(
                transaction.get("TransactionAmt")
            )

            if risk >= 0.80:

                patterns.append(
                    {
                        "pattern": "card_not_present_fraud",
                        "confidence": "medium",
                        "description": (
                            "Elevated transaction risk indicates "
                            "possible card-not-present fraud."
                        ),
                        "evidence": [
                            {
                                "claim": (
                                    f"Transaction risk score is "
                                    f"{risk:.2f}."
                                ),
                                "source": "graph",
                                "ref": str(
                                    transaction["TransactionID"]
                                ),
                                "entity_ids": [
                                    str(
                                        transaction["TransactionID"]
                                    )
                                ],
                            }
                        ],
                    }
                )

            elif risk >= 0.50:

                patterns.append(
                    {
                        "pattern": "undocumented",
                        "confidence": "low",
                        "description": (
                            "Suspicious transaction activity was "
                            "detected, but available evidence does "
                            "not establish one of the documented "
                            "HHGOA patterns."
                        ),
                        "evidence": [
                            {
                                "claim": (
                                    f"Transaction risk score is "
                                    f"{risk:.2f} and amount is "
                                    f"${amount:.2f}."
                                ),
                                "source": "graph",
                                "ref": str(
                                    transaction["TransactionID"]
                                ),
                                "entity_ids": [
                                    str(
                                        transaction["TransactionID"]
                                    )
                                ],
                            }
                        ],
                    }
                )

        # ------------------------------------------------------------
        # Final result
        # ------------------------------------------------------------

        if not patterns:

            primary_pattern = "none"
            confidence = "low"

        else:

            confidence_order = {
                "high": 3,
                "medium": 2,
                "low": 1,
            }

            patterns.sort(
                key=lambda item: confidence_order.get(
                    item.get("confidence", "low"),
                    0,
                ),
                reverse=True,
            )

            primary_pattern = patterns[0]["pattern"]
            confidence = patterns[0]["confidence"]

        evidence = [
            evidence
            for pattern in patterns
            for evidence in pattern.get(
                "evidence",
                [],
            )
        ]

        return {
            "status": "analyzed",
            "transaction_id": transaction_id,
            "customer_id": (
                None
                if pd.isna(customer_id)
                else str(customer_id)
            ),
            "primary_pattern": primary_pattern,
            "confidence": confidence,
            "patterns": patterns,
            "evidence": evidence,
        }

    # ================================================================
    # CARD TESTING
    # ================================================================

    def _detect_card_testing(
        self,
        transaction: pd.Series,
        customer_rows: pd.DataFrame,
    ) -> dict[str, Any] | None:

        if str(transaction.get("channel", "")).lower() != "online":
            return None

        timestamp = transaction.get("ts")

        if pd.isna(timestamp):
            return None

        card_key = transaction.get("card_key")

        if pd.isna(card_key):
            return None

        card_rows = customer_rows[
            customer_rows["card_key"].astype(str)
            == str(card_key)
        ].copy()

        card_rows = card_rows[
            card_rows["channel"].astype(str).str.lower()
            == "online"
        ]

        card_rows = card_rows[
            card_rows["ts"].notna()
        ]

        if card_rows.empty:
            return None

        start = timestamp - pd.Timedelta(hours=1)
        end = timestamp + pd.Timedelta(hours=1)

        window = card_rows[
            (card_rows["ts"] >= start)
            & (card_rows["ts"] <= end)
        ]

        small_transactions = window[
            window["TransactionAmt"] <= 20
        ]

        larger_transactions = window[
            window["TransactionAmt"] > 20
        ]

        if (
            len(small_transactions) >= 3
            and not larger_transactions.empty
        ):

            return {
                "pattern": "card_testing",
                "confidence": "high",
                "description": (
                    "Multiple small online authorizations "
                    "occurred around a larger transaction."
                ),
                "evidence": [
                    {
                        "claim": (
                            f"{len(small_transactions)} small "
                            "online transactions occurred within "
                            "one hour of the flagged transaction."
                        ),
                        "source": "graph",
                        "ref": str(
                            transaction["TransactionID"]
                        ),
                        "entity_ids": [
                            str(x)
                            for x in small_transactions[
                                "TransactionID"
                            ].tolist()
                        ],
                    }
                ],
            }

        return None

    # ================================================================
    # CARD NOT PRESENT FRAUD
    # ================================================================

    def _detect_card_not_present_fraud(
        self,
        transaction: pd.Series,
        customer_rows: pd.DataFrame,
    ) -> dict[str, Any] | None:

        channel = str(
            transaction.get("channel", "")
        ).lower()

        if channel != "online":
            return None

        risk = self._number(
            transaction.get("risk_score")
        )

        amount = self._number(
            transaction.get("TransactionAmt")
        )

        if risk >= 0.80 and amount >= 100:

            return {
                "pattern": "card_not_present_fraud",
                "confidence": "high",
                "description": (
                    "A high-risk online transaction has "
                    "material transaction exposure."
                ),
                "evidence": [
                    {
                        "claim": (
                            f"Online transaction has risk score "
                            f"{risk:.2f} and amount "
                            f"${amount:.2f}."
                        ),
                        "source": "graph",
                        "ref": str(
                            transaction["TransactionID"]
                        ),
                        "entity_ids": [
                            str(
                                transaction["TransactionID"]
                            )
                        ],
                    }
                ],
            }

        if risk >= 0.70:

            return {
                "pattern": "card_not_present_fraud",
                "confidence": "medium",
                "description": (
                    "An online transaction has elevated "
                    "fraud risk."
                ),
                "evidence": [
                    {
                        "claim": (
                            f"Online transaction has risk "
                            f"score {risk:.2f}."
                        ),
                        "source": "graph",
                        "ref": str(
                            transaction["TransactionID"]
                        ),
                        "entity_ids": [
                            str(
                                transaction["TransactionID"]
                            )
                        ],
                    }
                ],
            }

        return None

    # ================================================================
    # NEW DEVICE
    # ================================================================

    def _detect_card_not_present_new_device(
        self,
        transaction: pd.Series,
        customer_rows: pd.DataFrame,
    ) -> dict[str, Any] | None:

        if str(
            transaction.get("channel", "")
        ).lower() != "online":
            return None

        timestamp = transaction.get("ts")

        if pd.isna(timestamp):
            return None

        device = str(
            transaction.get(
                "DeviceInfo",
                "Unknown",
            )
        )

        if device == "Unknown":
            return None

        previous = customer_rows[
            customer_rows["ts"] < timestamp
        ].copy()

        if previous.empty:
            return None

        previous_devices = set(
            previous["DeviceInfo"]
            .dropna()
            .astype(str)
        )

        if device not in previous_devices:

            risk = self._number(
                transaction.get("risk_score")
            )

            confidence = (
                "high"
                if risk >= 0.70
                else "medium"
            )

            return {
                "pattern": "card_not_present_new_device",
                "confidence": confidence,
                "description": (
                    "The online transaction originated "
                    "from a device not previously observed "
                    "for this customer."
                ),
                "evidence": [
                    {
                        "claim": (
                            f"Device '{device}' was not previously "
                            "observed for this customer."
                        ),
                        "source": "graph",
                        "ref": str(
                            transaction["TransactionID"]
                        ),
                        "entity_ids": [
                            str(
                                transaction["TransactionID"]
                            )
                        ],
                    }
                ],
            }

        return None

    # ================================================================
    # OUT OF REGION
    # ================================================================

    def _detect_out_of_region_use(
        self,
        transaction: pd.Series,
        customer_rows: pd.DataFrame,
    ) -> dict[str, Any] | None:

        timestamp = transaction.get("ts")

        if pd.isna(timestamp):
            return None

        region = transaction.get("addr1")

        if pd.isna(region):
            return None

        previous = customer_rows[
            customer_rows["ts"] < timestamp
        ].copy()

        previous = previous[
            previous["addr1"].notna()
        ]

        if len(previous) < 3:
            return None

        known_regions = set(
            previous["addr1"]
            .astype(str)
        )

        current_region = str(region)

        if current_region not in known_regions:

            risk = self._number(
                transaction.get("risk_score")
            )

            confidence = (
                "high"
                if risk >= 0.70
                else "medium"
            )

            return {
                "pattern": "out_of_region_use",
                "confidence": confidence,
                "description": (
                    "The transaction uses a billing region "
                    "not previously observed for the customer."
                ),
                "evidence": [
                    {
                        "claim": (
                            f"Billing region {current_region} "
                            "is new relative to prior activity."
                        ),
                        "source": "graph",
                        "ref": str(
                            transaction["TransactionID"]
                        ),
                        "entity_ids": [
                            str(
                                transaction["TransactionID"]
                            )
                        ],
                    }
                ],
            }

        return None

    # ================================================================
    # ACCOUNT TAKEOVER
    # ================================================================

    def _detect_account_takeover(
        self,
        transaction: pd.Series,
        customer_rows: pd.DataFrame,
    ) -> dict[str, Any] | None:

        timestamp = transaction.get("ts")

        if pd.isna(timestamp):
            return None

        previous = customer_rows[
            customer_rows["ts"] < timestamp
        ].copy()

        if len(previous) < 3:
            return None

        current_device = str(
            transaction.get(
                "DeviceInfo",
                "Unknown",
            )
        )

        current_email = str(
            transaction.get(
                "P_emaildomain",
                "Unknown",
            )
        )

        previous_devices = set(
            previous["DeviceInfo"]
            .dropna()
            .astype(str)
        )

        previous_emails = set(
            previous["P_emaildomain"]
            .dropna()
            .astype(str)
        )

        new_device = (
            current_device != "Unknown"
            and current_device not in previous_devices
        )

        new_email = (
            current_email != "Unknown"
            and current_email not in previous_emails
        )

        risk = self._number(
            transaction.get("risk_score")
        )

        if (
            new_device
            and new_email
            and risk >= 0.70
        ):

            return {
                "pattern": "account_takeover",
                "confidence": "high",
                "description": (
                    "A new device and new purchaser email "
                    "domain appeared together with elevated risk."
                ),
                "evidence": [
                    {
                        "claim": (
                            "New device and purchaser email "
                            "domain were observed together "
                            "with elevated transaction risk."
                        ),
                        "source": "graph",
                        "ref": str(
                            transaction["TransactionID"]
                        ),
                        "entity_ids": [
                            str(
                                transaction["TransactionID"]
                            )
                        ],
                    }
                ],
            }

        if new_device and risk >= 0.85:

            return {
                "pattern": "account_takeover",
                "confidence": "medium",
                "description": (
                    "A high-risk transaction originated "
                    "from a previously unseen device."
                ),
                "evidence": [
                    {
                        "claim": (
                            "A previously unseen device was "
                            "combined with high transaction risk."
                        ),
                        "source": "graph",
                        "ref": str(
                            transaction["TransactionID"]
                        ),
                        "entity_ids": [
                            str(
                                transaction["TransactionID"]
                            )
                        ],
                    }
                ],
            }

        return None

    # ================================================================
    # HELPERS
    # ================================================================

    @staticmethod
    def _number(value: Any) -> float:
        try:
            value = float(value)

            if pd.isna(value):
                return 0.0

            return value

        except (TypeError, ValueError):
            return 0.0


def get_pattern_analyzer() -> FraudPatternAnalyzer:
    return FraudPatternAnalyzer()