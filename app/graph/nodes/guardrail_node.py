from typing import Dict, Any
from ..state import MedicineAssistantState
from ...guardrails.detector import GuardrailDetector

detector = GuardrailDetector()

def guardrail_node(state: MedicineAssistantState) -> Dict[str, Any]:
    """
    Screens every query for emergency red flags, out-of-scope requests,
    and extracts drug entities.
    """
    query = state.get("query", "")
    assessment = detector.assess(query)
    
    return {
        "guardrail_result": assessment.model_dump(),
        "intent": assessment.intent_category,
        "extracted_drugs": assessment.extracted_drugs,
        "escalation_triggered": assessment.is_emergency,
        "status": "GUARDRAIL_COMPLETED"
    }
