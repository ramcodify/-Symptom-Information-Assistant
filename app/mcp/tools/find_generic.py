import json
from pathlib import Path
from typing import Dict, Any

def _load_generics_db() -> Dict[str, Any]:
    path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "generic_equivalents.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("mappings", {})
    return {}

def find_generic_equivalent(medicine_name: str) -> Dict[str, Any]:
    """
    Returns generic equivalents, therapeutic equivalence details, 
    and estimated cost savings for a branded medicine.
    
    Args:
        medicine_name: Brand name or generic medicine (e.g., 'Tylenol', 'Lipitor', 'Advil')
    """
    query = medicine_name.lower().strip()
    db = _load_generics_db()
    
    # 1. Direct match by key
    for key, data in db.items():
        if key == query or query in key or query in data.get("brand_name", "").lower():
            return {
                "status": "success",
                "found": True,
                "input_name": medicine_name,
                "brand_name": data.get("brand_name"),
                "generic_name": data.get("generic_name"),
                "active_ingredient": data.get("active_ingredient"),
                "therapeutic_equivalence": data.get("therapeutic_equivalence"),
                "average_cost_savings": data.get("average_cost_savings"),
                "common_forms": data.get("common_forms", []),
                "otc_availability": data.get("otc_availability"),
                "switching_guidance": data.get("switching_guidance")
            }

    # 2. Check if user passed the generic name and wants to know what brands it replaces
    for key, data in db.items():
        if query in data.get("generic_name", "").lower() or query in data.get("active_ingredient", "").lower():
            return {
                "status": "success",
                "found": True,
                "input_name": medicine_name,
                "brand_name": data.get("brand_name"),
                "generic_name": data.get("generic_name"),
                "active_ingredient": data.get("active_ingredient"),
                "therapeutic_equivalence": data.get("therapeutic_equivalence"),
                "average_cost_savings": data.get("average_cost_savings"),
                "common_forms": data.get("common_forms", []),
                "otc_availability": data.get("otc_availability"),
                "switching_guidance": f"'{medicine_name.title()}' is the generic active compound. Branded versions include {data.get('brand_name')}."
            }

    return {
        "status": "not_found",
        "found": False,
        "input_name": medicine_name,
        "message": (
            f"No specific generic equivalence record found for '{medicine_name}'. "
            "Most active ingredients have store-brand/generic alternatives. "
            "Ask your pharmacist for the bioequivalent generic version using the active molecule name."
        )
    }
