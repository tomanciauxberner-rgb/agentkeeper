from src.cso.types import CognitiveStateObject, Fact


def estimate_tokens(text: str) -> int:
    """
    Approximate token count without network calls.
    Rule of thumb: ~1 token per 4 chars (OpenAI/Anthropic average).
    Good enough for budget decisions.
    """
    return max(1, len(text) // 4)


class CognitiveReconstructionEngine:
    """
    Core of AgentKeeper.
    Reconstructs agent cognitive state for a target model under token constraints.
    Does NOT just inject all facts — it prioritizes and selects based on:
    1. Critical flag
    2. Token budget for the target model
    """

    # Token budgets per model (conservative — leave room for task prompt)
    MODEL_TOKEN_LIMITS = {
        "gpt-4":           6000,
        "gpt-4-turbo":     8000,
        "claude-3-5-sonnet-20241022": 8000,
        "claude-3-haiku":  4000,
    }

    DEFAULT_TOKEN_LIMIT = 4000

    def __init__(self, cso: CognitiveStateObject):
        self.cso = cso
        self._count_tokens_for_all_facts()

    def _count_tokens_for_all_facts(self):
        for fact in self.cso.memory_facts:
            fact.token_count = estimate_tokens(fact.content)

    def prioritize(self, target_model: str, max_tokens: int | None = None) -> list[Fact]:
        """
        Returns the optimal subset of facts to inject for a given model and token budget.
        Priority: critical facts first, then by token efficiency.
        """
        budget = max_tokens or self.MODEL_TOKEN_LIMITS.get(target_model, self.DEFAULT_TOKEN_LIMIT)

        # Sort: critical first, then shortest (maximize facts per token)
        sorted_facts = sorted(
            self.cso.memory_facts,
            key=lambda f: (0 if f.critical else 1, f.token_count)
        )

        selected = []
        used_tokens = 0

        for fact in sorted_facts:
            if used_tokens + fact.token_count <= budget:
                selected.append(fact)
                used_tokens += fact.token_count
            elif fact.critical:
                # Critical facts are force-included even if tight
                # Truncate last non-critical to make room
                for i in range(len(selected) - 1, -1, -1):
                    if not selected[i].critical:
                        used_tokens -= selected[i].token_count
                        selected.pop(i)
                        break
                if used_tokens + fact.token_count <= budget:
                    selected.append(fact)
                    used_tokens += fact.token_count

        return selected

    def build_context_prompt(self, target_model: str, task: str, max_tokens: int | None = None) -> str:
        """
        Builds the memory injection prompt for a given model and task.
        This is what gets injected as system context.
        """
        facts = self.prioritize(target_model, max_tokens)

        if not facts:
            return f"Task: {task}"

        facts_text = "\n".join([
            f"- {'[CRITICAL] ' if f.critical else ''}{f.content}"
            for f in facts
        ])

        return f"""You are a persistent AI agent. Your memory from previous sessions:

{facts_text}

Current task: {task}

Use your memory to maintain continuity. Do not ask for information you already have."""

    def reconstruction_stats(self, target_model: str, max_tokens: int | None = None) -> dict:
        selected = self.prioritize(target_model, max_tokens)
        total_facts = len(self.cso.memory_facts)
        critical_total = len(self.cso.critical_facts())
        critical_selected = len([f for f in selected if f.critical])
        tokens_used = sum(f.token_count for f in selected)

        return {
            "total_facts": total_facts,
            "selected_facts": len(selected),
            "critical_total": critical_total,
            "critical_selected": critical_selected,
            "critical_recovery_rate": round(critical_selected / critical_total, 3) if critical_total else 0,
            "tokens_used": tokens_used,
            "token_budget": max_tokens or self.MODEL_TOKEN_LIMITS.get(target_model, self.DEFAULT_TOKEN_LIMIT),
        }
