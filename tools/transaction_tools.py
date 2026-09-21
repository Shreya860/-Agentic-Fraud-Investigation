from pathlib import Path
from typing import Any
import pandas as pd

class TransactionTools:
    """
    Local transaction-data tools used by the fraud investigation agent.
    """

    def __init__(self, data_path: str | None = None):
        if data_path:
            self.data_path = Path(data_path)
        else:
            self.data_path = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "processed"
                / "transactions"
                / "transactions.csv"
            )

        self._transactions: pd.DataFrame | None = None

    def _load_transactions(self) -> pd.DataFrame:
        """
        Load processed transaction data lazily.
        """

        if self._transactions is not None:
            return self._transactions

        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Transaction data file not found: {self.data_path}"
            )

        self._transactions = pd.read_csv(self.data_path)

        return self._transactions

    @staticmethod
    def _clean_value(value: Any) -> Any:
        """
        Convert pandas-specific values into normal Python values.
        """

        if pd.isna(value):
            return None

        if isinstance(value, pd.Timestamp):
            return value.isoformat()

        if hasattr(value, "item"):
            try:
                return value.item()
            except (ValueError, TypeError):
                pass

        return value

    @classmethod
    def _clean_records(
        cls,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Clean pandas/numpy values from a list of records.
        """

        cleaned = []

        for record in records:
            cleaned.append(
                {
                    key: cls._clean_value(value)
                    for key, value in record.items()
                }
            )

        return cleaned

    def get_transaction(
        self,
        transaction_id: str,
    ) -> dict[str, Any] | None:
        """
        Get one transaction by transaction ID.
        """

        df = self._load_transactions()

        matches = df[
            df["TransactionID"].astype(str)
            == str(transaction_id)
        ]

        if matches.empty:
            return None

        record = matches.iloc[0].to_dict()

        return {
            key: self._clean_value(value)
            for key, value in record.items()
        }

    def get_customer_transactions(
        self,
        customer_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Get transactions belonging to a customer.
        """

        df = self._load_transactions()

        customer_df = df[
            df["customer_id"].astype(str)
            == str(customer_id)
        ].copy()

        if customer_df.empty:
            return []

        if "ts" in customer_df.columns:
            customer_df = customer_df.sort_values(
                by="ts",
                ascending=False,
            )

        return self._clean_records(
            customer_df.head(limit).to_dict(orient="records")
        )

    def get_high_risk_transactions(
        self,
        customer_id: str,
        limit: int = 10,
        threshold: float = 0.8,
    ) -> list[dict[str, Any]]:
        """
        Get high-risk transactions for a customer.

        Only transactions with risk_score >= threshold
        are returned.
        """

        threshold = float(threshold)

        df = self._load_transactions()

        customer_df = df[
            df["customer_id"].astype(str)
            == str(customer_id)
        ].copy()

        if customer_df.empty:
            return []

        customer_df["risk_score"] = pd.to_numeric(
            customer_df["risk_score"],
            errors="coerce",
        )

        customer_df = customer_df[
            customer_df["risk_score"] >= threshold
        ]

        customer_df = customer_df.sort_values(
            by="risk_score",
            ascending=False,
        )

        return self._clean_records(
            customer_df.head(limit).to_dict(orient="records")
        )

    def get_customer_summary(
        self,
        customer_id: str,
    ) -> dict[str, Any]:
        """
        Return a basic transaction summary for a customer.
        """

        df = self._load_transactions()

        customer_df = df[
            df["customer_id"].astype(str)
            == str(customer_id)
        ].copy()

        if customer_df.empty:
            return {
                "customer_id": str(customer_id),
                "transaction_count": 0,
                "total_amount": 0.0,
                "average_amount": 0.0,
                "max_amount": 0.0,
                "max_risk_score": 0.0,
                "high_risk_transaction_count": 0,
            }

        customer_df["TransactionAmt"] = pd.to_numeric(
            customer_df["TransactionAmt"],
            errors="coerce",
        )

        customer_df["risk_score"] = pd.to_numeric(
            customer_df["risk_score"],
            errors="coerce",
        )

        high_risk_count = int(
            (
                customer_df["risk_score"] >= 0.8
            ).sum()
        )

        return {
            "customer_id": str(customer_id),
            "transaction_count": int(len(customer_df)),
            "total_amount": float(
                customer_df["TransactionAmt"]
                .fillna(0)
                .sum()
            ),
            "average_amount": float(
                customer_df["TransactionAmt"]
                .mean()
                if customer_df["TransactionAmt"].notna().any()
                else 0.0
            ),
            "max_amount": float(
                customer_df["TransactionAmt"]
                .max()
                if customer_df["TransactionAmt"].notna().any()
                else 0.0
            ),
            "max_risk_score": float(
                customer_df["risk_score"]
                .max()
                if customer_df["risk_score"].notna().any()
                else 0.0
            ),
            "high_risk_transaction_count": high_risk_count,
        }