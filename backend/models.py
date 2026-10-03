from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class Source:
    """A normalized document from the NOVA dataset."""

    id: str
    filename: str
    path: str
    file_type: str
    category: str

    content: str = ""
    date: Optional[str] = None
    locator: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Evidence:
    """A precise piece of evidence supporting a fact."""

    source_id: str
    locator: str
    excerpt: str


@dataclass
class Fact:
    """A project fact extracted from one or more sources."""

    id: str
    statement: str
    status: str

    date: Optional[str] = None
    confidence: float = 0.0

    evidence: List[Evidence] = field(default_factory=list)


@dataclass
class Action:
    """An action or unresolved task discovered in project history."""

    description: str

    owner: Optional[str] = None
    deadline: Optional[str] = None
    status: str = "unknown"

    evidence: List[Evidence] = field(default_factory=list)