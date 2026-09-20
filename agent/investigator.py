from typing import Any

from tools.graph_tools import GraphTools


class FraudInvestigator:
    """
    Performs the evidence-gathering stage of a fraud investigation.

    The investigator does not make the final fraud decision.
    Its job is to collect and organize evidence that can later
    be evaluated by the assessor and decision layers.
    """

    def __init__(self, graph_tools: GraphTools | None = None):
        self.graph_tools = graph_tools or GraphTools()

    # ============================================================
    # CUSTOMER INVESTIGATION
    # ============================================================

    def investigate_customer(
        self,
        customer_id: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        """
        Investigate a customer using the available graph-style tools.

        Evidence collected:

        - customer transaction history
        - cards
        - devices
        - email domains
        - connected customers through cards
        - connected customers through devices
        - device rarity
        - high-risk transactions
        """

        network = self.graph_tools.get_investigation_network(
            customer_id=customer_id,
            limit=limit,
        )

        if not network.get("found"):
            return {
                "customer_id": str(customer_id),
                "status": "not_found",
                "evidence": [],
                "findings": [],
                "investigation_summary": {
                    "customer_found": False,
                },
            }

        evidence = self._build_evidence(network)

        findings = self._build_findings(network)

        summary = self._build_summary(
            network=network,
            findings=findings,
        )

        return {
            "customer_id": str(customer_id),
            "status": "investigated",
            "evidence": evidence,
            "findings": findings,
            "investigation_summary": summary,
            "raw_network": network,
        }

    # ============================================================
    # EVIDENCE
    # ============================================================

    def _build_evidence(
        self,
        network: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Convert raw graph-tool output into explicit evidence items.
        """

        evidence: list[dict[str, Any]] = []

        customer_network = network.get(
            "customer_network",
            {},
        )

        # --------------------------------------------------------
        # Customer transaction volume
        # --------------------------------------------------------

        transaction_count = customer_network.get(
            "transaction_count",
            0,
        )

        evidence.append(
            {
                "type": "transaction_history",
                "severity": "informational",
                "description": (
                    f"Customer has {transaction_count} "
                    "recorded transactions."
                ),
                "data": {
                    "transaction_count": transaction_count,
                },
            }
        )

        # --------------------------------------------------------
        # High-risk transactions
        # --------------------------------------------------------

        high_risk_transactions = network.get(
            "high_risk_transactions",
            [],
        )

        if high_risk_transactions:

            maximum_risk = max(
                float(txn.get("risk_score") or 0)
                for txn in high_risk_transactions
            )

            evidence.append(
                {
                    "type": "high_risk_transactions",
                    "severity": self._risk_severity(
                        maximum_risk
                    ),
                    "description": (
                        f"{len(high_risk_transactions)} "
                        "recent/high-risk transactions were "
                        f"identified, with maximum risk score "
                        f"{maximum_risk:.2f}."
                    ),
                    "data": {
                        "count": len(
                            high_risk_transactions
                        ),
                        "maximum_risk_score": maximum_risk,
                        "transactions": high_risk_transactions,
                    },
                }
            )
        else:
            evidence.append(
                {
                    "type": "high_risk_transactions",
                    "severity": "informational",
                    "description": (
                        "No transactions meeting the "
                        "current high-risk threshold were found."
                    ),
                    "data": {
                        "count": 0,
                    },
                }
            )

        # --------------------------------------------------------
        # Card connections
        # --------------------------------------------------------

        connected_by_card = network.get(
            "connected_by_card",
            [],
        )

        if connected_by_card:

            evidence.append(
                {
                    "type": "shared_card_network",
                    "severity": "suspicious",
                    "description": (
                        f"{len(connected_by_card)} "
                        "customer connections were found "
                        "through shared card information."
                    ),
                    "data": {
                        "connections": connected_by_card,
                    },
                }
            )
        else:
            evidence.append(
                {
                    "type": "shared_card_network",
                    "severity": "informational",
                    "description": (
                        "No other customers were connected "
                        "through a sufficiently complete shared "
                        "card key."
                    ),
                    "data": {
                        "connections": [],
                    },
                }
            )

        # --------------------------------------------------------
        # Device connections
        # --------------------------------------------------------

        connected_by_device = network.get(
            "connected_by_device",
            [],
        )

        meaningful_device_connections = [
            connection
            for connection in connected_by_device
            if connection.get("device_key")
            not in {
                "desktop|Windows",
                "desktop|UNKNOWN",
                "mobile|UNKNOWN",
            }
        ]

        if meaningful_device_connections:

            evidence.append(
                {
                    "type": "shared_device_network",
                    "severity": "suspicious",
                    "description": (
                        f"{len(meaningful_device_connections)} "
                        "customer connections were found "
                        "through device fingerprints that are "
                        "not among the common generic fingerprints."
                    ),
                    "data": {
                        "connections": (
                            meaningful_device_connections
                        ),
                    },
                }
            )

        elif connected_by_device:

            evidence.append(
                {
                    "type": "shared_device_network",
                    "severity": "informational",
                    "description": (
                        "Device connections were found, but the "
                        "highest-volume connections use common "
                        "or unknown device fingerprints. These "
                        "are not treated as strong evidence by "
                        "the investigator."
                    ),
                    "data": {
                        "connections": connected_by_device,
                    },
                }
            )

        else:

            evidence.append(
                {
                    "type": "shared_device_network",
                    "severity": "informational",
                    "description": (
                        "No connected customers were identified "
                        "through device fingerprints."
                    ),
                    "data": {
                        "connections": [],
                    },
                }
            )

        # --------------------------------------------------------
        # Device rarity
        # --------------------------------------------------------

        device_rarity = network.get(
            "device_rarity",
            [],
        )

        rare_devices = [
            device
            for device in device_rarity
            if device.get("rarity")
            in {
                "unique",
                "rare",
            }
        ]

        if rare_devices:

            evidence.append(
                {
                    "type": "rare_device_fingerprint",
                    "severity": "suspicious",
                    "description": (
                        f"{len(rare_devices)} relatively rare "
                        "device fingerprints were identified."
                    ),
                    "data": {
                        "devices": rare_devices,
                    },
                }
            )

        # --------------------------------------------------------
        # Email domains
        # --------------------------------------------------------

        email_domains = customer_network.get(
            "email_domains",
            [],
        )

        evidence.append(
            {
                "type": "email_domains",
                "severity": "informational",
                "description": (
                    f"Customer is associated with "
                    f"{len(email_domains)} email domains."
                ),
                "data": {
                    "email_domains": email_domains,
                },
            }
        )

        # --------------------------------------------------------
        # Channels
        # --------------------------------------------------------

        channels = customer_network.get(
            "channels",
            [],
        )

        evidence.append(
            {
                "type": "transaction_channels",
                "severity": "informational",
                "description": (
                    "Observed transaction channels were "
                    f"{', '.join(channels) if channels else 'none'}."
                ),
                "data": {
                    "channels": channels,
                },
            }
        )

        return evidence

    # ============================================================
    # FINDINGS
    # ============================================================

    def _build_findings(
        self,
        network: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Convert evidence into preliminary investigation findings.

        These are NOT final fraud decisions.
        """

        findings: list[dict[str, Any]] = []

        high_risk_transactions = network.get(
            "high_risk_transactions",
            [],
        )

        # --------------------------------------------------------
        # High risk finding
        # --------------------------------------------------------

        if high_risk_transactions:

            maximum_risk = max(
                float(txn.get("risk_score") or 0)
                for txn in high_risk_transactions
            )

            if maximum_risk >= 0.95:

                findings.append(
                    {
                        "finding": "very_high_risk_activity",
                        "confidence": "high",
                        "description": (
                            "The customer has transaction activity "
                            "with a risk score of at least 0.95."
                        ),
                        "supporting_evidence": [
                            "high_risk_transactions"
                        ],
                    }
                )

            elif maximum_risk >= 0.80:

                findings.append(
                    {
                        "finding": "high_risk_activity",
                        "confidence": "medium",
                        "description": (
                            "The customer has transaction activity "
                            "with a risk score of at least 0.80."
                        ),
                        "supporting_evidence": [
                            "high_risk_transactions"
                        ],
                    }
                )

        # --------------------------------------------------------
        # Shared card finding
        # --------------------------------------------------------

        connected_by_card = network.get(
            "connected_by_card",
            [],
        )

        if connected_by_card:

            findings.append(
                {
                    "finding": "shared_card_connection",
                    "confidence": "medium",
                    "description": (
                        "The customer has transaction "
                        "connections with other customers "
                        "through shared card information."
                    ),
                    "supporting_evidence": [
                        "shared_card_network"
                    ],
                }
            )

        # --------------------------------------------------------
        # Rare device finding
        # --------------------------------------------------------

        device_rarity = network.get(
            "device_rarity",
            [],
        )

        rare_devices = [
            device
            for device in device_rarity
            if device.get("rarity")
            in {
                "unique",
                "rare",
            }
        ]

        if rare_devices:

            findings.append(
                {
                    "finding": "rare_device_connection",
                    "confidence": "medium",
                    "description": (
                        "The customer uses one or more relatively "
                        "rare device fingerprints."
                    ),
                    "supporting_evidence": [
                        "rare_device_fingerprint"
                    ],
                }
            )

        # --------------------------------------------------------
        # Generic device connections are NOT elevated
        # --------------------------------------------------------

        connected_by_device = network.get(
            "connected_by_device",
            [],
        )

        generic_connections = [
            connection
            for connection in connected_by_device
            if connection.get("device_key")
            in {
                "desktop|Windows",
                "desktop|UNKNOWN",
                "mobile|UNKNOWN",
            }
        ]

        if generic_connections:

            findings.append(
                {
                    "finding": "common_device_signal",
                    "confidence": "low",
                    "description": (
                        "Some customer connections use common "
                        "device fingerprints. These connections "
                        "should not be treated as strong evidence "
                        "without additional corroborating signals."
                    ),
                    "supporting_evidence": [
                        "shared_device_network"
                    ],
                }
            )

        # --------------------------------------------------------
        # No strong evidence
        # --------------------------------------------------------

        if not findings:

            findings.append(
                {
                    "finding": "insufficient_current_evidence",
                    "confidence": "low",
                    "description": (
                        "The current investigation data does not "
                        "contain enough evidence for a strong "
                        "preliminary finding."
                    ),
                    "supporting_evidence": [],
                }
            )

        return findings

    # ============================================================
    # SUMMARY
    # ============================================================

    def _build_summary(
        self,
        network: dict[str, Any],
        findings: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Produce a concise machine-readable investigation summary.
        """

        customer_network = network.get(
            "customer_network",
            {},
        )

        high_risk_transactions = network.get(
            "high_risk_transactions",
            [],
        )

        maximum_risk = None

        if high_risk_transactions:
            maximum_risk = max(
                float(txn.get("risk_score") or 0)
                for txn in high_risk_transactions
            )

        rare_devices = [
            device
            for device in network.get(
                "device_rarity",
                [],
            )
            if device.get("rarity")
            in {
                "unique",
                "rare",
            }
        ]

        return {
            "customer_found": True,
            "transaction_count": customer_network.get(
                "transaction_count",
                0,
            ),
            "card_count": len(
                customer_network.get(
                    "cards",
                    [],
                )
            ),
            "device_count": len(
                customer_network.get(
                    "devices",
                    [],
                )
            ),
            "connected_customer_count_card": len(
                network.get(
                    "connected_by_card",
                    [],
                )
            ),
            "connected_customer_count_device": len(
                network.get(
                    "connected_by_device",
                    [],
                )
            ),
            "rare_device_count": len(
                rare_devices
            ),
            "high_risk_transaction_count": len(
                high_risk_transactions
            ),
            "maximum_observed_risk": maximum_risk,
            "finding_count": len(findings),
        }

    # ============================================================
    # HELPERS
    # ============================================================

    @staticmethod
    def _risk_severity(
        risk_score: float,
    ) -> str:
        """
        Convert the dataset risk score into a descriptive
        evidence severity.
        """

        if risk_score >= 0.95:
            return "very_high"

        if risk_score >= 0.80:
            return "high"

        if risk_score >= 0.60:
            return "moderate"

        return "low"


# ================================================================
# FACTORY
# ================================================================

def get_investigator(
    graph_tools: GraphTools | None = None,
) -> FraudInvestigator:
    """
    Return a configured FraudInvestigator.
    """

    return FraudInvestigator(
        graph_tools=graph_tools
    )