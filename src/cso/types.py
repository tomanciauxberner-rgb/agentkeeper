from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Fact:
    id: str
    content: str
    critical: bool = False
    token_count: int = 0

    @staticmethod
    def create(content: str, critical: bool = False) -> "Fact":
        return Fact(
            id=str(uuid.uuid4()),
            content=content,
            critical=critical
        )


@dataclass
class CognitiveStateObject:
    agent_id: str
    memory_facts: list[Fact] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @staticmethod
    def create(agent_id: Optional[str] = None) -> "CognitiveStateObject":
        return CognitiveStateObject(
            agent_id=agent_id or str(uuid.uuid4())
        )

    def add_fact(self, content: str, critical: bool = False) -> Fact:
        fact = Fact.create(content, critical)
        self.memory_facts.append(fact)
        self.updated_at = datetime.utcnow().isoformat()
        return fact

    def critical_facts(self) -> list[Fact]:
        return [f for f in self.memory_facts if f.critical]

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "memory_facts": [
                {
                    "id": f.id,
                    "content": f.content,
                    "critical": f.critical,
                    "token_count": f.token_count
                }
                for f in self.memory_facts
            ],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @staticmethod
    def from_dict(data: dict) -> "CognitiveStateObject":
        cso = CognitiveStateObject(
            agent_id=data["agent_id"],
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )
        cso.memory_facts = [
            Fact(
                id=f["id"],
                content=f["content"],
                critical=f["critical"],
                token_count=f.get("token_count", 0)
            )
            for f in data["memory_facts"]
        ]
        return cso
