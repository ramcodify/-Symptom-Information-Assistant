from typing import Dict, Any
from ..state import MedicineAssistantState
from ...config import settings

def escalation_node(state: MedicineAssistantState) -> Dict[str, Any]:
    """
    Emergency Escalation Node (LangGraph Interrupt / Immediate Emergency Flow).
    Halts normal pipeline and issues urgent life-saving guidance and emergency numbers.
    """
    guardrail = state.get("guardrail_result", {})
    condition = guardrail.get("emergency_condition", "Critical Medical Emergency")
    matched_flag = ", ".join(guardrail.get("matched_flags", ["Severe symptoms"]))
    first_aid = guardrail.get("emergency_first_aid", "Seek immediate emergency assistance.")
    
    emergency_text = f"""🚨 **URGENT MEDICAL EMERGENCY DETECTED**

> **Identified Warning Sign**: `{matched_flag}`  
> **Possible Condition**: **{condition}**

### 🚑 Immediate Actions Required:
1. **CALL EMERGENCY SERVICES RIGHT NOW**:
   - 🇺🇸 **US & Canada**: Dial **911**
   - 🇪🇺 **Europe & International**: Dial **112**
   - 🇬🇧 **United Kingdom**: Dial **999**
   - 🇦🇺 **Australia**: Dial **000**
   - 🧪 **Poison Emergency (US)**: **1-800-222-1222**
   - 🎗️ **Suicide & Mental Health Crisis**: **988**

### 🩺 First-Aid & Safety Steps:
{first_aid}

---
*Normal informational processing has been suspended because your safety is paramount. Do not wait or drive yourself to the hospital—call emergency responders immediately.*"""

    return {
        "response_text": emergency_text,
        "interrupted": True,
        "escalation_triggered": True,
        "status": "EMERGENCY_HALTED",
        "sources": ["Emergency First Aid Protocols (WHO / Red Cross)", "Global Emergency Services Dispatch"]
    }
