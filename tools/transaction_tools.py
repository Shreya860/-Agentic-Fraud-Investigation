from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TRANSACTION_FILE = (
    ROOT / "data" / "processed" / "transactions" / "transactions.csv"
)


class TransactionTools:
    """Tools for investigating transactions from the local dataset."""

    def __init__(self, transaction_file: Path = TRANSACTION_FILE):
        self.transaction_file = Path(transaction_file)
        self._transactions: pd.DataFrame | None = None

    def _load_data(self) -> pd.DataFrame:
        """Load the transaction dataset lazily."""
        if self._transactions is None:
            if not self.transaction_file.exists():
                raise FileNotFoundError(
                    f"Transaction file not found: {self.transaction_file}"
                )

            self._transactions = pd.read_csv(self.transaction_file)

        return self._transactions

    def get_transaction(
        self,
        transaction_id: str,
    ) -> dict[str, Any] | None:
        """Return one transaction by TransactionID."""
        df = self._load_data()

        matches = df[
            df["TransactionID"].astype(str) == str(transaction_id)
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
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Return recent transactions for a customer."""
        df = self._load_data()

        matches = df[
            df["customer_id"].astype(str) == str(customer_id)
        ].copy()

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

        return [
            {
                key: self._clean_value(value)
                for key, value in row.items()
            }
            for row in matches.to_dict(orient="records")
        ]

    def get_high_risk_transactions(
        self,
        threshold: float = 0.8,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Return transactions whose risk score exceeds a threshold."""
        df = self._load_data()

        matches = df[
            pd.to_numeric(
                df["risk_score"],
                errors="coerce",
            ) >= threshold
        ].copy()

        matches = matches.sort_values(
            "risk_score",
            ascending=False,
        ).head(limit)

        return [
            {
                key: self._clean_value(value)
                for key, value in row.items()
            }
            for row in matches.to_dict(orient="records")
        ]

    def get_customer_summary(
        self,
        customer_id: str,
    ) -> dict[str, Any]:
        """Return basic behavioral statistics for a customer."""
        df = self._load_data()

        matches = df[
            df["customer_id"].astype(str) == str(customer_id)
        ].copy()

        if matches.empty:
            return {
                "customer_id": str(customer_id),
                "transaction_count": 0,
                "total_amount": 0.0,
                "average_amount": 0.0,
                "maximum_amount": 0.0,
                "average_risk_score": None,
                "maximum_risk_score": None,
            }

        amounts = pd.to_numeric(
            matches["TransactionAmt"],
            errors="coerce",
        )

        risks = pd.to_numeric(
            matches["risk_score"],
            errors="coerce",
        )

        return {
            "customer_id": str(customer_id),
            "transaction_count": int(len(matches)),
            "total_amount": self._clean_value(amounts.sum()),
            "average_amount": self._clean_value(amounts.mean()),
            "maximum_amount": self._clean_value(amounts.max()),
            "average_risk_score": self._clean_value(risks.mean()),
            "maximum_risk_score": self._clean_value(risks.max()),
        }

    @staticmethod
    def _clean_value(value: Any) -> Any:
        """Convert pandas/NumPy values into JSON-friendly values."""
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


def get_transaction_tools() -> TransactionTools:
    """Return a TransactionTools instance."""
    return TransactionTools()