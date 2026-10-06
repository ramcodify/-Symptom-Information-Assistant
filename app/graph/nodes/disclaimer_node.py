from typing import Dict, Any
from ..state import MedicineAssistantState
from ...config import settings

def disclaimer_node(state: MedicineAssistantState) -> Dict[str, Any]:
    """
    Appends mandatory medical disclaimer, verified source citations,
    and standardized safety reminders to every final response.
    """
    response_text = state.get("response_text", "")
    sources = state.get("sources", [])
    
    # Format sources list
    formatted_sources = ""
    if sources:
        formatted_sources = "\n\n### 📖 Verified Medical Sources & Citations:\n"
        for s in dict.fromkeys(sources):
            formatted_sources += f"- 🔍 *{s}*\n"

    # Standardized medical disclaimer
    final_output = f"{response_text}{formatted_sources}\n---\n{settings.STANDARD_DISCLAIMER}"
    
    return {
        "response_text": final_output,
        "disclaimer_included": True,
        "status": "COMPLETED"
    }
