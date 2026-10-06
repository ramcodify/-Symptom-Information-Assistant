from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict

class MedicineAssistantState(TypedDict, total=False):
    """LangGraph State for Medicine & Symptom Information Assistant."""
    query: str
    history: List[Dict[str, str]]
    guardrail_result: Dict[str, Any]
    intent: str
    extracted_drugs: List[str]
    tool_results: Dict[str, Any]
    rag_context: List[Dict[str, Any]]
    response_text: str
    escalation_triggered: bool
    disclaimer_included: bool
    interrupted: bool
    status: str
    sources: List[str]
    metadata: Dict[str, Any]
