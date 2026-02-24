"""
AgentKeeper Benchmark
Tests cross-model cognitive continuity under token constraints.
"""

import json
from src.cso.types import CognitiveStateObject
from src.cre.engine import CognitiveReconstructionEngine
from src.adapters.adapters import BaseAdapter, MockAdapter


def generate_test_facts(n_total: int = 100, n_critical: int = 20) -> CognitiveStateObject:
    cso = CognitiveStateObject.create(agent_id="benchmark-agent-001")
    critical_data = [
        "project budget: 50000 EUR",
        "project deadline: March 1 2025",
        "client name: Acme Corporation",
        "primary contact: Jean Dupont jean@acme.com",
        "tech stack: Python FastAPI React PostgreSQL",
        "current sprint: Sprint 4 ends January 15",
        "blocker: API rate limiting on OpenAI tier 1",
        "decision: use Anthropic Claude for production",
        "team size: 3 engineers 1 designer",
        "deployment target: AWS eu-west-1",
        "database: PostgreSQL 15 with pgvector extension",
        "authentication: JWT tokens 24h expiry",
        "staging URL: https://staging.acme-project.com",
        "production URL: https://app.acme.com",
        "repository: github.com/acme/main-project private",
        "last release: v1.4.2 deployed December 20",
        "next milestone: beta launch February 1",
        "compliance requirement: GDPR data residency EU",
        "SLA target: 99.9 percent uptime",
        "monitoring: Datadog APM enabled",
    ]
    for content in critical_data[:n_critical]:
        cso.add_fact(content, critical=True)
    non_critical_templates = [
        "meeting notes day {i}: discussed sprint progress",
        "ticket AK-{i}: bug in user registration flow resolved",
        "dependency update {i}: bumped lodash to 4.17.{i}",
        "code review {i}: approved PR by engineer {i}",
        "slack message {i}: asked about deployment window",
        "log entry {i}: increased memory usage detected at noon",
        "research note {i}: evaluated competitor product feature",
        "todo {i}: refactor authentication middleware",
        "design feedback {i}: update button colors per brand guide",
        "infrastructure note {i}: reserved additional EC2 capacity",
    ]
    for i in range(n_total - n_critical):
        template = non_critical_templates[i % len(non_critical_templates)]
        cso.add_fact(template.format(i=i + 1), critical=False)
    return cso


def run_benchmark(source_model, target_model, source_adapter, target_adapter, token_budget=2000, verbose=True):
    print(f"\n{'='*60}")
    print(f"AgentKeeper Benchmark")
    print(f"Source: {source_model} → Target: {target_model}")
    print(f"Token budget: {token_budget}")
    print(f"{'='*60}\n")

    cso = generate_test_facts(n_total=100, n_critical=20)
    print(f"✓ Generated {len(cso.memory_facts)} facts ({len(cso.critical_facts())} critical)\n")

    cre = CognitiveReconstructionEngine(cso)
    stats = cre.reconstruction_stats(target_model, max_tokens=token_budget)

    print(f"CRE Analysis:")
    print(f"  Total facts:      {stats['total_facts']}")
    print(f"  Selected facts:   {stats['selected_facts']}")
    print(f"  Critical total:   {stats['critical_total']}")
    print(f"  Critical selected:{stats['critical_selected']}")
    print(f"  Token budget:     {stats['token_budget']}")
    print(f"  Tokens used:      {stats['tokens_used']}")
    print(f"  Critical recovery:{stats['critical_recovery_rate']*100:.1f}%\n")

    task = "What are the key project details I should know?"
    context_prompt = cre.build_context_prompt(target_model, task, max_tokens=token_budget)

    print(f"Querying {target_model}...")
    response = target_adapter.query(context_prompt, task)

    selected_facts = cre.prioritize(target_model, max_tokens=token_budget)
    critical_selected = [f for f in selected_facts if f.critical]
    recovered_ids = target_adapter.extract_facts_from_response(response, critical_selected)
    recovery_score = len(recovered_ids) / len(critical_selected) if critical_selected else 0

    print(f"\nResults:")
    print(f"  Facts injected (critical): {len(critical_selected)}")
    print(f"  Facts verified in response: {len(recovered_ids)}")
    print(f"  Recovery score: {len(recovered_ids)}/{len(critical_selected)} = {recovery_score*100:.1f}%")

    if verbose:
        print(f"\nSample response:\n{response[:500]}...")

    return {
        "source_model": source_model,
        "target_model": target_model,
        "token_budget": token_budget,
        "cre_stats": stats,
        "recovery_score": recovery_score,
        "recovered_count": len(recovered_ids),
        "critical_injected": len(critical_selected),
    }


if __name__ == "__main__":
    import os
    from pathlib import Path
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent.parent.parent / ".env")

    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    if not openai_key or "REMPLACE" in openai_key:
        print("⚠️  OpenAI key manquante — fallback mock")
        source_adapter = MockAdapter()
        source_model = "gpt-4-mock"
    else:
        from src.adapters.adapters import OpenAIAdapter
        source_adapter = OpenAIAdapter(api_key=openai_key, model="gpt-4-turbo")
        source_model = "gpt-4-turbo"
        print("✓ OpenAI adapter prêt")

    if not anthropic_key or "REMPLACE" in anthropic_key:
        print("⚠️  Anthropic key manquante — fallback mock")
        target_adapter = MockAdapter()
        target_model = "claude-mock"
    else:
        from src.adapters.adapters import AnthropicAdapter
        target_adapter = AnthropicAdapter(api_key=anthropic_key, model="claude-sonnet-4-5-20250929")
        target_model = "claude-sonnet-4-5-20250929"
        print("✓ Anthropic adapter prêt")

    result = run_benchmark(
        source_model=source_model,
        target_model=target_model,
        source_adapter=source_adapter,
        target_adapter=target_adapter,
        token_budget=2000,
        verbose=True
    )

    print(f"\n{'='*60}")
    print(f"BENCHMARK COMPLETE")
    print(f"Critical recovery rate: {result['cre_stats']['critical_recovery_rate']*100:.1f}%")
    print(f"{'='*60}")
