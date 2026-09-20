from typing import Any
from memory.case_dna import CaseDNA
from memory.case_memory import CaseMemory
from memory.outcomes import OutcomeMemory
from memory.similarity import CaseSimilarity

class MemoryService:
    """Coordinate case DNA, historical retrieval, similarity, and outcomes."""

    def __init__(
        self,
        case_memory: CaseMemory | None = None,
        case_dna: CaseDNA | None = None,
        similarity: CaseSimilarity | None = None,
        outcome_memory: OutcomeMemory | None = None,
    ):
        self.case_memory = case_memory or CaseMemory()
        self.case_dna = case_dna or CaseDNA()
        self.similarity = similarity or CaseSimilarity()
        self.outcome_memory = outcome_memory or OutcomeMemory()

    def store_case(self, case: dict[str, Any]) -> dict[str, Any]:
        return self.case_memory.store_case(case)

    def build_memory_context(
        self,
        case: dict[str, Any],
        limit: int = 5,
    ) -> dict[str, Any]:
        dna = self.case_dna.build(case)
        search_profile = self.case_dna.build_search_profile(case)

        historical_matches = []

        for pattern in search_profile["fraud_patterns"]:
            matches = self.case_memory.find_similar_historical_cases(
                customer_id=search_profile["customer_id"],
                fraud_pattern=pattern,
                limit=limit,
            )

            for historical_case in matches:
                comparison = self.similarity.compare(
                    search_profile,
                    historical_case,
                )

                outcome = self.outcome_memory.summarize(
                    historical_case
                )

                historical_matches.append(
                    {
                        "similarity": comparison,
                        "outcome_memory": outcome,
                    }
                )

        historical_matches.sort(
            key=lambda item: item["similarity"]["similarity_score"],
            reverse=True,
        )

        return {
            "case_dna": dna,
            "search_profile": search_profile,
            "historical_matches": historical_matches[:limit],
            "historical_match_count": len(historical_matches),
        }


def get_memory_service() -> MemoryService:
    return MemoryService()