from typing import Dict, Any, List
from ..state import MedicineAssistantState
from ...mcp.tools.drug_info import get_drug_info
from ...mcp.tools.find_generic import find_generic_equivalent
from ...mcp.tools.web_search import search_health_advisories
from ...rag.retriever import retriever

def info_node(state: MedicineAssistantState) -> Dict[str, Any]:
    """
    Info Agent: Answers general health, drug monographs, and generic queries using RAG and MCP tools.
    Also politely handles out-of-scope diagnostic and prescription requests.
    """
    intent = state.get("intent", "GENERAL_HEALTH_RAG")
    guardrail = state.get("guardrail_result", {})
    query = state.get("query", "")
    extracted_drugs = state.get("extracted_drugs", [])
    
    response_lines: List[str] = []
    sources: List[str] = []
    tool_results: Dict[str, Any] = {}

    # 1. Handle Diagnosis Refusal
    if intent == "DIAGNOSIS_REQUEST" or guardrail.get("is_diagnosis_request"):
        policy_msg = guardrail.get("policy_message") or (
            "I cannot provide a personalized medical diagnosis. Evaluating illnesses requires a physical "
            "examination, clinical history, and diagnostic laboratory or imaging tests by a doctor."
        )
        response_lines.append(f"🛡️ **Clinical Guidance Note**: {policy_msg}\n")
        response_lines.append("### 📚 Educational Health Context:")
        
        # Retrieve general RAG context for education
        rag_docs = retriever.retrieve(query, top_k=2)
        if rag_docs:
            for doc in rag_docs:
                response_lines.append(f"**From {doc['title']} ({doc['source']})**:")
                response_lines.append(f"{doc['content']}\n")
                sources.append(f"{doc['title']} - {doc['source']}")
        else:
            response_lines.append(
                "Symptoms can often be caused by multiple distinct medical conditions ranging from benign self-limiting issues "
                "to conditions requiring specific medical treatment. We strongly recommend scheduling an evaluation with a primary care physician."
            )
            sources.append("WHO General Health Guidelines")

    # 2. Handle Prescription Refusal
    elif intent == "PRESCRIPTION_REQUEST" or guardrail.get("is_prescription_request"):
        policy_msg = guardrail.get("policy_message") or (
            "I cannot prescribe medications or authorize changes to your dosage. "
            "Modifying medication regimens requires clinical authorization from a licensed prescriber."
        )
        response_lines.append(f"🛡️ **Prescription Policy**: {policy_msg}\n")
        response_lines.append("### ℹ️ What You Should Do:")
        response_lines.append("1. **Contact Your Prescriber**: Reach out to your doctor or clinic to request refills or dosage adjustments.")
        response_lines.append("2. **Speak with Your Pharmacist**: Pharmacists can assist with emergency refill supplies or clarify dosing schedules.")
        response_lines.append("3. **Never Alter Dosages Independently**: Adjusting doses on your own can lead to adverse effects, toxicity, or loss of therapeutic control.")
        sources.append("Safe Pharmacy Dispensing Practices")

    # 3. Handle Generic Equivalent Lookup
    elif intent == "GENERIC_LOOKUP":
        search_target = extracted_drugs[0] if extracted_drugs else query
        gen_data = find_generic_equivalent(search_target)
        tool_results["generic_data"] = gen_data
        
        response_lines.append("## 🏷️ Generic Medicine & Bioequivalence Finder\n")
        if gen_data.get("found"):
            response_lines.append(f"### Brand Name: **{gen_data.get('brand_name')}**")
            response_lines.append(f"- **Generic Active Ingredient**: **{gen_data.get('generic_name')}**")
            response_lines.append(f"- **Active Molecule**: `{gen_data.get('active_ingredient')}`")
            response_lines.append(f"- **Bioequivalence Rating**: **{gen_data.get('therapeutic_equivalence')}**")
            response_lines.append(f"- **💰 Estimated Cost Savings**: **{gen_data.get('average_cost_savings')}**")
            response_lines.append(f"- **Available Dosage Forms**: {', '.join(gen_data.get('common_forms', []))}")
            response_lines.append(f"- **Access Category**: {gen_data.get('otc_availability')}")
            response_lines.append(f"\n**💡 Switching Tip**: {gen_data.get('switching_guidance')}")
            sources.append("FDA Orange Book: Approved Drug Products with Therapeutic Equivalence Evaluations")
            sources.append("WHO Quality-Assured Generics Policy")
        else:
            response_lines.append(gen_data.get("message", "Generic information not found."))
            sources.append("WHO Essential Medicines Guide")

    # 4. Handle Drug Info Monograph Request
    elif intent == "DRUG_INFO" or len(extracted_drugs) > 0:
        target_drug = extracted_drugs[0] if extracted_drugs else "paracetamol"
        drug_data = get_drug_info(target_drug)
        tool_results["drug_data"] = drug_data
        
        response_lines.append(f"## 📋 Medicine Profile: {drug_data.get('generic_name', target_drug.title())}\n")
        if drug_data.get("found"):
            response_lines.append(f"**Class**: {drug_data.get('drug_class')}")
            if drug_data.get("brand_names"):
                response_lines.append(f"**Common Brand Names**: {', '.join(drug_data.get('brand_names'))}")
            response_lines.append(f"**Mechanism of Action**: {drug_data.get('mechanism_of_action')}\n")
            
            response_lines.append("### 🩺 Approved Uses & Indications:")
            for use in drug_data.get("approved_uses", []):
                response_lines.append(f"- {use}")
            
            response_lines.append("\n### ⚠️ Side Effects & Tolerability:")
            response_lines.append("**Common Side Effects** (usually mild):")
            for se in drug_data.get("common_side_effects", []):
                response_lines.append(f"- {se}")
            
            if drug_data.get("severe_side_effects"):
                response_lines.append("\n**Severe Adverse Reactions** (seek medical care if experienced):")
                for sse in drug_data.get("severe_side_effects", []):
                    response_lines.append(f"- 🔴 {sse}")

            if drug_data.get("boxed_warnings"):
                response_lines.append("\n### 🚨 Important Safety Warnings & Precautions:")
                for w in drug_data.get("boxed_warnings", []):
                    response_lines.append(f"- {w}")

            response_lines.append(f"\n**Standard Reference Dosing**: {drug_data.get('standard_dosage_guidelines')}")
            response_lines.append(f"**Storage Instructions**: {drug_data.get('storage_instructions')}")
            sources.append(drug_data.get("source", "OpenFDA Drug Labels"))
        else:
            response_lines.append(drug_data.get("message", "Drug details not found."))
            sources.append("Clinical Drug Monograph Leaflet")

    # 5. General Health Query with RAG & Search
    else:
        rag_docs = retriever.retrieve(query, top_k=2)
        response_lines.append("## 🩺 Verified Health & Medicine Information\n")
        
        if rag_docs:
            for doc in rag_docs:
                response_lines.append(f"### {doc['title']}")
                response_lines.append(f"*{doc['category']} — {doc['source']}*")
                response_lines.append(f"{doc['content']}\n")
                sources.append(f"{doc['title']} ({doc['source']})")
        else:
            # Fallback to search / advisory
            adv = search_health_advisories(query, max_results=2)
            tool_results["search_data"] = adv
            results = adv.get("results", [])
            if results:
                for r in results:
                    response_lines.append(f"### {r['title']}")
                    response_lines.append(f"{r['snippet']}\n")
                    sources.append(f"{r['title']} - {r['source']}")
            else:
                response_lines.append("For comprehensive medical advice on this topic, please consult with your healthcare professional.")
                sources.append("WHO Health Information")

    return {
        "response_text": "\n".join(response_lines),
        "tool_results": tool_results,
        "rag_context": retriever.retrieve(query, top_k=2),
        "status": "INFO_SYNTHESIZED",
        "sources": sources
    }
