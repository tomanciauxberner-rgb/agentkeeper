"""
AgentKeeper — Cognitive persistence layer for AI agents.
Cross-model memory continuity.

Usage:
    import agentkeeper

    agent = agentkeeper.create(agent_id="my-agent")
    agent.remember("budget: 50k€", critical=True)
    agent.remember("client: Acme Corp", critical=True)

    # Switch provider — memory survives
    response = agent.ask("What is the project budget?", provider="anthropic")

    # Save and restore later
    agent.save()
    agent2 = agentkeeper.load("my-agent")
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from src.cso.types import CognitiveStateObject, Fact
from src.cre.engine import CognitiveReconstructionEngine
from src.storage.sqlite_store import Storage
from src.adapters.adapters import OpenAIAdapter, AnthropicAdapter, MockAdapter, GeminiAdapter, OllamaAdapter, BaseAdapter

load_dotenv(Path(__file__).parent / ".env")

_storage = Storage()

PROVIDERS = {
    "openai": lambda: OpenAIAdapter(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model=os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    ),
    "anthropic": lambda: AnthropicAdapter(
        api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
    ),
    "gemini": lambda: GeminiAdapter(
        api_key=os.getenv("GEMINI_API_KEY", ""),
        model=os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    ),
    "ollama": lambda: OllamaAdapter(
        model=os.getenv("OLLAMA_MODEL", "llama3"),
        host=os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ),
    "mock": lambda: MockAdapter(),
}


class Agent:
    def __init__(self, cso: CognitiveStateObject, default_provider: str = "anthropic"):
        self._cso = cso
        self._default_provider = default_provider

    @property
    def id(self) -> str:
        return self._cso.agent_id

    @property
    def facts(self) -> list[Fact]:
        return self._cso.memory_facts

    def remember(self, content: str, critical: bool = False) -> "Agent":
        """Add a fact to agent memory."""
        self._cso.add_fact(content, critical=critical)
        return self

    def forget(self, fact_id: str) -> "Agent":
        """Remove a fact by ID."""
        self._cso.memory_facts = [f for f in self._cso.memory_facts if f.id != fact_id]
        return self

    def ask(self, question: str, provider: str | None = None, token_budget: int = 4000) -> str:
        """
        Ask the agent a question.
        Memory is reconstructed and injected for the target provider.
        """
        provider = provider or self._default_provider
        adapter = self._get_adapter(provider)
        cre = CognitiveReconstructionEngine(self._cso)
        prompt = cre.build_context_prompt(provider, question, max_tokens=token_budget)
        return adapter.query(prompt, question)

    def switch_provider(self, provider: str) -> "Agent":
        """Switch default provider. Memory is preserved."""
        if provider not in PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}. Available: {list(PROVIDERS.keys())}")
        self._default_provider = provider
        return self

    def save(self) -> "Agent":
        """Persist agent state to SQLite."""
        _storage.save(self._cso)
        return self

    def stats(self, provider: str | None = None, token_budget: int = 4000) -> dict:
        """Show memory reconstruction stats for a given provider."""
        provider = provider or self._default_provider
        cre = CognitiveReconstructionEngine(self._cso)
        return cre.reconstruction_stats(provider, max_tokens=token_budget)

    def _get_adapter(self, provider: str) -> BaseAdapter:
        if provider not in PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}")
        return PROVIDERS[provider]()

    def __repr__(self):
        return f"Agent(id={self.id}, facts={len(self.facts)}, provider={self._default_provider})"


def create(agent_id: str | None = None, provider: str = "anthropic") -> Agent:
    """Create a new agent."""
    cso = CognitiveStateObject.create(agent_id=agent_id)
    return Agent(cso, default_provider=provider)


def load(agent_id: str) -> Agent:
    """Load an existing agent from storage."""
    cso = _storage.load(agent_id)
    if cso is None:
        raise ValueError(f"Agent '{agent_id}' not found.")
    return Agent(cso)


def delete(agent_id: str):
    """Delete an agent from storage."""
    _storage.delete(agent_id)
