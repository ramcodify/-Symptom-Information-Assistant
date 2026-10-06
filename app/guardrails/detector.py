import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class GuardrailAssessment(BaseModel):
    is_emergency: bool = False
    emergency_condition: Optional[str] = None
    emergency_first_aid: Optional[str] = None
    matched_flags: List[str] = Field(default_factory=list)
    is_diagnosis_request: bool = False
    is_prescription_request: bool = False
    is_interaction_request: bool = False
    is_generic_request: bool = False
    is_drug_info_request: bool = False
    extracted_drugs: List[str] = Field(default_factory=list)
    policy_action: str = "ALLOW"  # "ESCALATE_EMERGENCY", "REFUSE_DIAGNOSIS", "REFUSE_PRESCRIPTION", "ALLOW"
    policy_message: Optional[str] = None
    intent_category: str = "GENERAL_HEALTH"
    confidence: float = 1.0


class GuardrailDetector:
    """Multi-tiered healthcare safety screener."""
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path(__file__).resolve().parent / "red_flags.json"
        
        with open(config_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
            
        self.emergency_conditions = self.data.get("emergency_conditions", [])
        self.out_of_scope = self.data.get("out_of_scope_categories", {})
        
        # Load known drug & substance names for extraction
        self.known_drugs = {
            "paracetamol", "acetaminophen", "tylenol", "panadol", "calpol",
            "ibuprofen", "advil", "motrin", "nurofen", "brufen",
            "lisinopril", "prinivil", "zestril", "qbrelis",
            "metformin", "glucophage", "fortamet", "glumetza",
            "amoxicillin", "amoxil", "moxatag", "trimox",
            "atorvastatin", "lipitor", "atorva",
            "omeprazole", "prilosec", "losec", "zegerid",
            "amlodipine", "norvasc", "amlor", "istin",
            "aspirin", "bayer", "ecotrin", "bufferin",
            "warfarin", "coumadin", "jantoven",
            "sertraline", "zoloft", "lustral",
            "tramadol", "clarithromycin", "clopidogrel", "plavix",
            "spironolactone", "sildenafil", "viagra", "nitroglycerin",
            "xanax", "adderall", "alcohol", "beer", "wine",
            "blood pressure medication", "blood pressure medicine", "blood pressure pills",
            "blood thinner", "antibiotics"
        }

    def extract_mentioned_drugs(self, query: str) -> List[str]:
        """Extract mentioned drug names or categories from text."""
        query_lower = query.lower()
        found = []
        for drug in self.known_drugs:
            pattern = r'\b' + re.escape(drug) + r'\b'
            if re.search(pattern, query_lower):
                found.append(drug)
        return list(dict.fromkeys(found))

    def check_emergency(self, query: str) -> Optional[Dict[str, Any]]:
        """Check if the query matches acute life-threatening emergency symptoms."""
        q = query.lower()
        
        for condition in self.emergency_conditions:
            # 1. Regex pattern match
            for pat in condition.get("patterns", []):
                if re.search(pat, q):
                    return {
                        "condition": condition["condition"],
                        "matched_flag": pat,
                        "first_aid": condition["first_aid"],
                        "severity": condition["severity"]
                    }

            # 2. Direct keyword/phrase match
            for kw in condition.get("keywords", []):
                if kw in q:
                    return {
                        "condition": condition["condition"],
                        "matched_flag": kw,
                        "first_aid": condition["first_aid"],
                        "severity": condition["severity"]
                    }
            
            # 3. Symptom combination match
            for combo in condition.get("symptom_combos", []):
                if all(term in q for term in combo if term):
                    return {
                        "condition": condition["condition"],
                        "matched_flag": " + ".join([c for c in combo if c]),
                        "first_aid": condition["first_aid"],
                        "severity": condition["severity"]
                    }
                    
        return None

    def check_out_of_scope(self, query: str) -> Dict[str, Any]:
        """Check for diagnosis demands or prescription demands."""
        q = query.lower()
        diag_data = self.out_of_scope.get("diagnosis_requests", {})
        presc_data = self.out_of_scope.get("prescription_requests", {})
        
        # Check prescription regex and keywords
        is_presc = False
        for pat in presc_data.get("patterns", []):
            if re.search(pat, q):
                is_presc = True
                break
        if not is_presc:
            for kw in presc_data.get("keywords", []):
                if kw in q:
                    is_presc = True
                    break

        # Check diagnosis regex and keywords
        is_diag = False
        if not is_presc:
            for pat in diag_data.get("patterns", []):
                if re.search(pat, q):
                    is_diag = True
                    break
            if not is_diag:
                for kw in diag_data.get("keywords", []):
                    if kw in q:
                        is_diag = True
                        break

        return {
            "is_diagnosis": is_diag,
            "is_prescription": is_presc,
            "diag_policy": diag_data.get("policy_response", ""),
            "presc_policy": presc_data.get("policy_response", "")
        }

    def assess(self, query: str) -> GuardrailAssessment:
        """Run full safety and intent assessment pipeline."""
        drugs = self.extract_mentioned_drugs(query)
        q = query.lower()
        
        # 1. First priority: Emergency check
        emergency_match = self.check_emergency(query)
        if emergency_match:
            return GuardrailAssessment(
                is_emergency=True,
                emergency_condition=emergency_match["condition"],
                emergency_first_aid=emergency_match["first_aid"],
                matched_flags=[emergency_match["matched_flag"]],
                extracted_drugs=drugs,
                policy_action="ESCALATE_EMERGENCY",
                policy_message=(
                    f"🚨 **CRITICAL RED-FLAG ALERT**: Symptoms matching **{emergency_match['condition']}** "
                    f"detected ('{emergency_match['matched_flag']}'). Please seek immediate emergency medical care."
                ),
                intent_category="EMERGENCY_RED_FLAG",
                confidence=1.0
            )

        # 2. Second priority: Out-of-scope diagnosis & prescription checks
        oos = self.check_out_of_scope(query)
        if oos["is_prescription"]:
            return GuardrailAssessment(
                is_emergency=False,
                is_prescription_request=True,
                extracted_drugs=drugs,
                policy_action="REFUSE_PRESCRIPTION",
                policy_message=oos["presc_policy"],
                intent_category="PRESCRIPTION_REQUEST",
                confidence=0.99
            )

        if oos["is_diagnosis"]:
            return GuardrailAssessment(
                is_emergency=False,
                is_diagnosis_request=True,
                extracted_drugs=drugs,
                policy_action="REFUSE_DIAGNOSIS",
                policy_message=oos["diag_policy"],
                intent_category="DIAGNOSIS_REQUEST",
                confidence=0.98
            )

        # 3. Third priority: Specific medical intent classification
        interaction_patterns = [
            "take.*with", "together", "interact", "interaction", "combine",
            "mix", "safe with", "at the same time", "can i take", "concurrent"
        ]
        is_interaction = (
            any(re.search(pat, q) for pat in interaction_patterns) and (len(drugs) >= 2 or "medication" in q or "medicine" in q or "alcohol" in q)
        ) or ("interaction" in q) or ("combine" in q and len(drugs) >= 1)

        generic_patterns = [
            "generic", "cheaper", "alternative", "equivalent", "brand name for",
            "generic for", "substitute", "cost less", "store brand"
        ]
        is_generic = any(re.search(pat, q) for pat in generic_patterns)

        drug_info_patterns = [
            "used for", "side effect", "side-effect", "dosage", "dose", "warning",
            "what is", "how does.*work", "contraindication", "indication", "storage", "taking it"
        ]
        is_drug_info = any(re.search(pat, q) for pat in drug_info_patterns) or (len(drugs) > 0 and not is_generic and not is_interaction)

        if is_interaction:
            intent = "INTERACTION_CHECK"
        elif is_generic:
            intent = "GENERIC_LOOKUP"
        elif is_drug_info and len(drugs) > 0:
            intent = "DRUG_INFO"
        else:
            intent = "GENERAL_HEALTH_RAG"

        return GuardrailAssessment(
            is_emergency=False,
            is_interaction_request=is_interaction,
            is_generic_request=is_generic,
            is_drug_info_request=is_drug_info,
            extracted_drugs=drugs,
            policy_action="ALLOW",
            intent_category=intent,
            confidence=0.96
        )
