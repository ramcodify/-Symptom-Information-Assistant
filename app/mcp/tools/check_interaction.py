import json
from pathlib import Path
from typing import List, Dict, Any

DRUG_SYNONYMS = {
    "blood pressure medication": "lisinopril",
    "blood pressure medicine": "lisinopril",
    "blood pressure pills": "lisinopril",
    "bp meds": "lisinopril",
    "bp medication": "lisinopril",
    "blood thinner": "warfarin",
    "tylenol": "paracetamol",
    "panadol": "paracetamol",
    "acetaminophen": "paracetamol",
    "advil": "ibuprofen",
    "motrin": "ibuprofen",
    "nurofen": "ibuprofen",
    "prinivil": "lisinopril",
    "zestril": "lisinopril",
    "lipitor": "atorvastatin",
    "glucophage": "metformin",
    "amoxil": "amoxicillin",
    "prilosec": "omeprazole",
    "norvasc": "amlodipine",
    "coumadin": "warfarin",
    "zoloft": "sertraline",
    "viagra": "sildenafil"
}

def _load_interactions_db() -> Dict[str, Any]:
    path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "drug_interactions.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"interactions": []}

def normalize_drug_term(term: str) -> str:
    cleaned = term.lower().strip()
    return DRUG_SYNONYMS.get(cleaned, cleaned)

def check_drug_interaction(drugs: List[str]) -> Dict[str, Any]:
    """
    Checks known interactions between two or more medicines.
    
    Args:
        drugs: List of medicine names (e.g. ['ibuprofen', 'lisinopril'])
    """
    if len(drugs) < 2:
        return {
            "status": "insufficient_inputs",
            "message": "At least two medications are required to perform a drug interaction check.",
            "interactions_found": False,
            "results": []
        }

    normalized = [normalize_drug_term(d) for d in drugs]
    interactions_db = _load_interactions_db().get("interactions", [])
    
    found_interactions = []
    
    # Check all pairs
    for i in range(len(normalized)):
        for j in range(i + 1, len(normalized)):
            d1, d2 = normalized[i], normalized[j]
            raw1, raw2 = drugs[i], drugs[j]
            
            for item in interactions_db:
                pair = [p.lower() for p in item["pair"]]
                if (d1 in pair[0] and d2 in pair[1]) or (d1 in pair[1] and d2 in pair[0]):
                    found_interactions.append({
                        "drug_pair": [raw1.title(), raw2.title()],
                        "canonical_pair": [pair[0].title(), pair[1].title()],
                        "severity": item.get("severity", "Moderate"),
                        "severity_score": item.get("severity_score", 3),
                        "clinical_effect": item.get("effect"),
                        "mechanism": item.get("mechanism"),
                        "clinical_management": item.get("clinical_management"),
                        "alternative_recommendation": item.get("alternative_recommendation")
                    })
                    break

    max_severity = "None"
    if found_interactions:
        scores = [item["severity_score"] for item in found_interactions]
        max_score = max(scores)
        if max_score >= 5:
            max_severity = "High / Severe"
        elif max_score >= 3:
            max_severity = "Moderate"
        else:
            max_severity = "Minor"

    return {
        "status": "success",
        "checked_drugs": [d.title() for d in drugs],
        "interactions_found": len(found_interactions) > 0,
        "total_interactions": len(found_interactions),
        "highest_severity": max_severity,
        "results": found_interactions,
        "summary": (
            f"Found {len(found_interactions)} interaction(s) among the provided medications. "
            f"Highest risk level: {max_severity}."
            if found_interactions
            else "No direct severe interactions were flagged in our clinical reference dataset. However, always verify concurrent medications with your doctor or pharmacist."
        )
    }
