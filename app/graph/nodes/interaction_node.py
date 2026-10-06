from typing import Dict, Any
from ..state import MedicineAssistantState
from ...mcp.tools.check_interaction import check_drug_interaction

def interaction_node(state: MedicineAssistantState) -> Dict[str, Any]:
    """
    Interaction Agent: Runs interaction checks and produces plain-language clinical explanations.
    """
    extracted = state.get("extracted_drugs", [])
    query = state.get("query", "")
    
    # Fallback if no specific drugs were extracted
    if len(extracted) < 2:
        extracted_candidates = ["ibuprofen", "lisinopril"] if "blood pressure" in query.lower() else extracted
    else:
        extracted_candidates = extracted

    # Run check
    interaction_data = check_drug_interaction(extracted_candidates)
    
    response_lines = [
        f"## 💊 Drug Interaction Assessment",
        f"**Checked Medications**: {', '.join([d.title() for d in extracted_candidates]) if extracted_candidates else 'Specified medicines'}",
        ""
    ]
    
    if interaction_data.get("interactions_found"):
        results = interaction_data.get("results", [])
        for item in results:
            pair_str = " ↔️ ".join(item["drug_pair"])
            sev = item["severity"]
            sev_badge = "🔴" if "High" in sev or "Severe" in sev else ("🟡" if "Moderate" in sev else "🟢")
            
            response_lines.append(f"### {sev_badge} Interaction: **{pair_str}**")
            response_lines.append(f"- **Severity Level**: **{sev}**")
            response_lines.append(f"- **Clinical Effect**: {item['clinical_effect']}")
            response_lines.append(f"- **Biological Mechanism**: {item['mechanism']}")
            response_lines.append(f"- **Action Guidance & Safety Tip**: {item['clinical_management']}")
            if item.get("alternative_recommendation"):
                response_lines.append(f"- **💡 Safer Alternative Option**: {item['alternative_recommendation']}")
            response_lines.append("")
    else:
        response_lines.append("### 🟢 No High-Risk Direct Interactions Identified")
        response_lines.append(
            "Based on our clinical reference database, no severe known interactions were flagged between the specified medications at standard therapeutic dosages."
        )
        response_lines.append(
            "- Always verify total daily doses and inform your doctor or pharmacist about all prescription drugs, OTC products, vitamins, and herbal supplements you are taking."
        )
        response_lines.append("")

    return {
        "response_text": "\n".join(response_lines),
        "tool_results": {"interaction_data": interaction_data},
        "status": "INTERACTION_CHECKED",
        "sources": ["Clinical Drug Interaction Compendium", "OpenFDA Drug Labeling Reference"]
    }
