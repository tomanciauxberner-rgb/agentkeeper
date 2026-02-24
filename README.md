# AgentKeeper

**Cognitive persistence layer for AI agents.**

Your agent's memory survives crashes, restarts, and provider switches.

```python
import agentkeeper

agent = agentkeeper.create()
agent.remember("project budget: 50000 EUR", critical=True)
agent.remember("client: Acme Corporation", critical=True)

# Switch provider — memory survives
agent.switch_provider("anthropic")
response = agent.ask("What is the project budget?")
# → "The project budget is 50,000 EUR."

agent.save()
agent = agentkeeper.load("my-agent")
```

---

## The problem

Every LLM call is stateless. When your agent switches providers, crashes, or restarts — it forgets everything.

Today:
```
Agent (GPT-4) → learns facts → crashes
Agent (Claude) → starts fresh → knows nothing
```

With AgentKeeper:
```
Agent (GPT-4) → learns facts → crashes
Agent (Claude) → resumes → 95% facts recovered
```

---

## How it works

AgentKeeper introduces a **Cognitive Reconstruction Engine (CRE)** that sits between your agent and any LLM provider.

```
Your Agent
    ↓
AgentKeeper (CRE)        ← cognitive layer
    ↓       ↓       ↓       ↓
OpenAI  Anthropic  Gemini  Ollama  ← any provider
```

The CRE:
1. Stores facts independently of any provider
2. Prioritizes critical facts under token constraints
3. Reconstructs optimal context for each target model
4. Persists state to SQLite locally

This is **not prompt engineering**. It's a cognitive state layer that's provider-agnostic by design.

---

## Benchmark

```
100 facts stored (20 critical)
Token budget: 2000 tokens
Cross-model: GPT-4 → Claude (and Claude → GPT-4)

Critical recovery: 19/20 = 95% (bidirectional)
```

---

## Install

```bash
git clone https://github.com/tomanciauxberner-rgb/agentkeeper
cd agentkeeper
pip install -r requirements.txt
cp env.example .env  # Add your API keys
```

---

## Quickstart

```python
import agentkeeper

# Create agent
agent = agentkeeper.create(agent_id="my-agent", provider="openai")

# Store memory
agent.remember("project budget: 50000 EUR", critical=True)
agent.remember("deadline: March 1 2025", critical=True)
agent.remember("meeting notes: discussed onboarding")

# Ask on OpenAI
response = agent.ask("What is the budget?", provider="openai")

# Switch to Anthropic — memory survives
response = agent.ask("What is the deadline?", provider="anthropic")

# Switch to Gemini — memory survives
response = agent.ask("Who is the client?", provider="gemini")

# Switch to local Ollama — memory survives
response = agent.ask("What is the tech stack?", provider="ollama")

# Persist
agent.save()

# Restore later
agent = agentkeeper.load("my-agent")
```

---

## Supported providers

| Provider | Model | Requires |
|----------|-------|----------|
| `openai` | gpt-4-turbo | `OPENAI_API_KEY` |
| `anthropic` | claude-sonnet-4-5 | `ANTHROPIC_API_KEY` |
| `gemini` | gemini-1.5-pro | `GEMINI_API_KEY` |
| `ollama` | llama3 | Ollama running locally |
| `mock` | — | Nothing (for testing) |

---

## API

```python
agentkeeper.create(agent_id=None, provider="anthropic") → Agent
agentkeeper.load(agent_id) → Agent
agentkeeper.delete(agent_id)

agent.remember(content, critical=False) → Agent
agent.forget(fact_id) → Agent
agent.ask(question, provider=None, token_budget=4000) → str
agent.switch_provider(provider) → Agent
agent.save() → Agent
agent.stats(provider=None, token_budget=4000) → dict
```

---

## Why not Temporal?

Temporal handles **execution persistence** — your workflow doesn't crash.

AgentKeeper handles **cognitive persistence** — your agent doesn't forget.

Different layers. Complementary.

---

## Roadmap

- [x] Cross-model memory continuity (OpenAI, Anthropic, Gemini, Ollama)
- [x] Critical fact prioritization under token constraints
- [x] SQLite persistence
- [ ] Memory compression (v0.2)
- [ ] Semantic memory (embeddings)
- [ ] Multi-agent memory sharing
- [ ] Cloud sync

---

## License

MIT
