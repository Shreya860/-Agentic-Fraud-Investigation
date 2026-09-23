from typing import Any

from agent.llm import OllamaLLM, get_llm


class InvestigationExplainer:
    """
    Generate analyst-facing explanations from structured
    investigation results.

    The LLM is optional. Deterministic fallback text is always
    available so the investigation pipeline does not depend on
    Ollama being fast or available.
    """

    def __init__(
        self,
        llm: OllamaLLM | None = None,
    ):
        self.llm = llm or get_llm()

    def explain(
        self,
        investigation: dict[str, Any],
        assessment: dict[str, Any],
        memory: dict[str, Any] | None = None,
        plan: dict[str, Any] | None = None,
        decision: dict[str, Any] | None = None,
        use_llm: bool = True,
    ) -> dict[str, Any]:
        """
        Generate an explanation.

        The structured facts remain authoritative.
        Qwen can only summarize those facts.
        """

        memory = memory or {}
        plan = plan or {}
        decision = decision or {}

        fallback = self._build_deterministic_explanation(
            investigation=investigation,
            assessment=assessment,
            memory=memory,
            decision=decision,
        )

        if not use_llm:
            return {
                "explanation": fallback,
                "source": "deterministic",
                "llm_used": False,
            }

        try:
            if not self.llm.is_available():
                return {
                    "explanation": fallback,
                    "source": "deterministic_fallback",
                    "llm_used": False,
                }

            prompt = self._build_prompt(
                investigation=investigation,
                assessment=assessment,
                memory=memory,
                plan=plan,
                decision=decision,
            )

            llm_response = self.llm.generate(
                prompt=prompt,
                system=(
                    "You are a fraud investigation explanation assistant. "
                    "Summarize only the supplied structured facts. "
                    "Do not invent evidence. "
                    "Do not change the risk level. "
                    "Do not change the recommended action. "
                    "Do not create new fraud findings. "
                    "Return a concise analyst-facing explanation."
                ),
                temperature=0.1,
                num_predict=128,
            )

            if self._is_valid_llm_response(
                llm_response,
                assessment=assessment,
                decision=decision,
            ):
                return {
                    "explanation": llm_response,
                    "source": "qwen3:4b",
                    "llm_used": True,
                }

        except Exception as exc:
            return {
                "explanation": fallback,
                "source": "deterministic_fallback",
                "llm_used": False,
                "llm_error": str(exc),
            }

        return {
            "explanation": fallback,
            "source": "deterministic_fallback",
            "llm_used": False,
        }

    def _build_prompt(
        self,
        investigation: dict[str, Any],
        assessment: dict[str, Any],
        memory: dict[str, Any],
        plan: dict[str, Any],
        decision: dict[str, Any],
    ) -> str:
        risk_level = assessment.get(
            "risk_level",
            "unknown",
        )

        findings = assessment.get(
            "findings",
            [],
        )

        uncertainty = assessment.get(
            "uncertainty",
            [],
        )

        fraud_patterns = assessment.get(
            "fraud_patterns",
            [],
        )

        historical_match_count = memory.get(
            "historical_match_count",
            0,
        )

        recommended_action = decision.get(
            "recommended_action",
            "not_available",
        )

        approval_required = decision.get(
            "approval_required",
            False,
        )

        approval_route = decision.get(
            "approval_route",
            "not specified",
        )

        return f"""
Summarize this fraud investigation for an analyst.

Use only these facts:

Risk level:
{risk_level}

Findings:
{findings}

Fraud patterns:
{fraud_patterns}

Historical similar cases:
{historical_match_count}

Uncertainty:
{uncertainty}

Recommended action:
{recommended_action}

Approval required:
{approval_required}

Approval route:
{approval_route}

Write 1-2 concise sentences.
Do not add facts that are not listed above.
Do not change the risk level.
Do not change the recommended action.
""".strip()

    def _build_deterministic_explanation(
        self,
        investigation: dict[str, Any],
        assessment: dict[str, Any],
        memory: dict[str, Any],
        decision: dict[str, Any],
    ) -> str:
        risk_level = assessment.get(
            "risk_level",
            "unknown",
        )

        risk_label = str(
            risk_level
        ).replace("_", " ")

        evidence = investigation.get(
            "evidence",
            [],
        )

        findings = assessment.get(
            "source_findings",
            assessment.get("findings", []),
        )

        uncertainty = assessment.get(
            "uncertainty",
            [],
        )

        historical_count = memory.get(
            "historical_match_count",
            0,
        )

        action = decision.get(
            "recommended_action",
            "no action specified",
        )

        sentences = []

        sentences.append(
            f"The investigation is assessed as {risk_label} risk "
            f"based on {len(evidence)} evidence item(s) and "
            f"{len(findings)} finding(s)."
        )

        if historical_count:
            sentences.append(
                f"{historical_count} similar historical case "
                f"match(es) were identified."
            )

        if uncertainty:
            sentences.append(
                f"Remaining uncertainty includes: "
                f"{uncertainty[0]}"
            )

        sentences.append(
            f"The recommended action is {action}."
        )

        return " ".join(sentences)

    @staticmethod
    def _is_valid_llm_response(
        response: str,
        assessment: dict[str, Any],
        decision: dict[str, Any],
    ) -> bool:
        if not response:
            return False

        text = response.strip()

        if len(text) < 10:
            return False

        lower_text = text.lower()

        # Do not accept obvious leaked reasoning.
        reasoning_markers = [
            "the user wants",
            "hmm",
            "let me think",
            "first, why",
            "i should think",
            "let's unpack",
            "the user asked",
        ]

        if any(
            marker in lower_text
            for marker in reasoning_markers
        ):
            return False

        # If the model mentions the risk level, it must match.
        risk_level = str(
            assessment.get(
                "risk_level",
                "",
            )
        ).lower()

        if risk_level:
            if risk_level not in lower_text:
                return False

        # If an action is present, the model must not contradict it.
        action = str(
            decision.get(
                "recommended_action",
                "",
            )
        ).lower()

        if action:
            normalized_action = action.replace(
                "_",
                " ",
            )

            if (
                action not in lower_text
                and normalized_action not in lower_text
            ):
                return False

        return True


def get_investigation_explainer() -> InvestigationExplainer:
    return InvestigationExplainer()