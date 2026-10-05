"""LangGraph state shared between graph nodes."""

import operator
from typing import Annotated, List, Optional, TypedDict

from .schemas import EvidenceItem, Plan


class State(TypedDict):
    topic: str

    # Routing / research
    mode: str
    needs_research: bool
    queries: List[str]
    evidence: List[EvidenceItem]
    plan: Optional[Plan]

    # Recency
    as_of: str
    recency_days: int

    # Parallel workers
    # operator.add allows LangGraph worker outputs to be accumulated.
    sections: Annotated[List[tuple[int, str]], operator.add]

    # Reducer / image pipeline
    merged_md: str
    md_with_placeholders: str
    image_specs: List[dict]

    # Final result
    final: str
