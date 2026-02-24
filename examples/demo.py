"""
AgentKeeper — Example: cross-model memory continuity.

Démonstration :
1. Créer un agent
2. Stocker des facts
3. Interroger sur OpenAI
4. Switch sur Anthropic
5. Vérifier que la mémoire survit
"""

import sys
sys.path.insert(0, ".")

import agentkeeper

print("=" * 50)
print("AgentKeeper — Cross-model memory demo")
print("=" * 50)

# 1. Créer agent
agent = agentkeeper.create(agent_id="demo-agent-001", provider="openai")
print(f"\n✓ Agent créé : {agent.id}")

# 2. Stocker des facts
agent.remember("project budget: 50000 EUR", critical=True)
agent.remember("client name: Acme Corporation", critical=True)
agent.remember("deadline: March 1 2025", critical=True)
agent.remember("tech stack: Python FastAPI React", critical=True)
agent.remember("team size: 3 engineers", critical=True)
agent.remember("meeting notes day 1: discussed onboarding")
agent.remember("ticket 001: fixed login bug")
agent.remember("ticket 002: updated dashboard UI")
print(f"✓ {len(agent.facts)} facts stockés ({len([f for f in agent.facts if f.critical])} critiques)")

# 3. Stats mémoire
stats = agent.stats(provider="anthropic", token_budget=2000)
print(f"\nMémoire pour Anthropic (budget 2000 tokens):")
print(f"  Facts sélectionnés : {stats['selected_facts']}/{stats['total_facts']}")
print(f"  Critiques récupérés : {stats['critical_selected']}/{stats['critical_total']}")
print(f"  Tokens utilisés : {stats['tokens_used']}/{stats['token_budget']}")

# 4. Interroger sur OpenAI
print(f"\n[OpenAI] Question: What is the project budget?")
response_openai = agent.ask("What is the project budget?", provider="openai")
print(f"Réponse: {response_openai[:200]}")

# 5. Switch provider → Anthropic
agent.switch_provider("anthropic")
print(f"\n[Switch] Provider → Anthropic")

# 6. Même question sur Anthropic — mémoire survit
print(f"[Anthropic] Question: What is the project budget and deadline?")
response_anthropic = agent.ask("What is the project budget and deadline?", provider="anthropic")
print(f"Réponse: {response_anthropic[:300]}")

# 7. Sauvegarder
agent.save()
print(f"\n✓ Agent sauvegardé")

# 8. Recharger depuis storage
agent2 = agentkeeper.load("demo-agent-001")
print(f"✓ Agent rechargé : {agent2.id} — {len(agent2.facts)} facts")

print("\n" + "=" * 50)
print("DEMO COMPLETE — Memory survived cross-model switch")
print("=" * 50)
