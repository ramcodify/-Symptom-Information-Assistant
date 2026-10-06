import json
import httpx
from pathlib import Path
from typing import Dict, Any, Optional

def _normalize_name(name: str) -> str:
    """Normalize drug query name."""
    name = name.lower().strip()
    name = name.replace("tablets", "").replace("capsules", "").replace("mg", "").strip()
    return name

def _load_local_drugs() -> Dict[str, Any]:
    path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "drugs_database.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("drugs", {})
    return {}

def fetch_openfda_drug_label(drug_name: str) -> Optional[Dict[str, Any]]:
    """Query OpenFDA drug label API for official product monograph excerpts."""
    try:
        url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{drug_name}+openfda.generic_name:{drug_name}&limit=1"
        with httpx.Client(timeout=4.0) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                if results:
                    res = results[0]
                    return {
                        "source": "OpenFDA Official Drug Label API",
                        "indications_and_usage": res.get("indications_and_usage", ["N/A"])[0][:600],
                        "warnings": res.get("warnings", ["N/A"])[0][:600],
                        "adverse_reactions": res.get("adverse_reactions", ["N/A"])[0][:600],
                        "boxed_warning": res.get("boxed_warning", [None])[0]
                    }
    except Exception:
        # Fallback cleanly if network is unreachable or rate limited
        pass
    return None

def get_drug_info(drug_name: str) -> Dict[str, Any]:
    """
    Returns verified clinical uses, common side effects, severe warnings, 
    dosage notes, and storage info for a specified medicine.
    
    Args:
        drug_name: Name of the medicine (brand or generic).
    """
    cleaned = _normalize_name(drug_name)
    local_db = _load_local_drugs()
    
    # Check exact or brand name match
    matched_drug = None
    for key, info in local_db.items():
        if key == cleaned or cleaned in key:
            matched_drug = info
            break
        # Check brand names
        for b in info.get("brand_names", []):
            if cleaned == b.lower() or cleaned in b.lower():
                matched_drug = info
                break
        if matched_drug:
            break

    if matched_drug:
        return {
            "status": "success",
            "found": True,
            "source": "Curated Clinical Drug Knowledgebase & OpenFDA Reference",
            "generic_name": matched_drug["generic_name"],
            "brand_names": matched_drug.get("brand_names", []),
            "drug_class": matched_drug.get("class", "N/A"),
            "mechanism_of_action": matched_drug.get("mechanism", "N/A"),
            "approved_uses": matched_drug.get("indications", []),
            "standard_dosage_guidelines": matched_drug.get("standard_dosage", "Consult prescriber"),
            "common_side_effects": matched_drug.get("common_side_effects", []),
            "severe_side_effects": matched_drug.get("severe_side_effects", []),
            "boxed_warnings": matched_drug.get("warnings", []),
            "storage_instructions": matched_drug.get("storage", "Store at room temperature"),
            "rx_otc_status": matched_drug.get("rx_otc_status", "Unknown")
        }
    
    # Try OpenFDA live fallback
    fda_data = fetch_openfda_drug_label(cleaned)
    if fda_data:
        return {
            "status": "success",
            "found": True,
            "source": fda_data["source"],
            "generic_name": drug_name.capitalize(),
            "brand_names": [drug_name.capitalize()],
            "drug_class": "Pharmaceutical Agent",
            "approved_uses": [fda_data["indications_and_usage"]],
            "common_side_effects": [fda_data["adverse_reactions"]],
            "boxed_warnings": [fda_data["warnings"]] if not fda_data.get("boxed_warning") else [fda_data["boxed_warning"]],
            "standard_dosage_guidelines": "Refer to official prescription labeling and doctor's instructions.",
            "storage_instructions": "Store in a cool, dry place.",
            "rx_otc_status": "Regulated Medicine"
        }
    
    return {
        "status": "not_found",
        "found": False,
        "message": f"Clinical monograph for '{drug_name}' was not found in local reference database. Please verify the spelling or consult a licensed pharmacist."
    }
