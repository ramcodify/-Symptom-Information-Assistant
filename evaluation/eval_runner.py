import json
import time
from pathlib import Path
from typing import Dict, Any, List
from app.guardrails.detector import GuardrailDetector
from app.graph.workflow import run_medicine_assistant

def run_evaluation_suite(dataset_path: Path = None) -> Dict[str, Any]:
    """
    Executes benchmark evaluation on the test dataset and calculates
    precision, recall, F1, accuracy, and safety compliance.
    """
    if dataset_path is None:
        dataset_path = Path(__file__).resolve().parent / "test_dataset.json"
        
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        test_cases: List[Dict[str, Any]] = data.get("test_cases", [])

    detector = GuardrailDetector()
    
    # Metrics counters
    total_tests = len(test_cases)
    emergency_tp = 0
    emergency_fp = 0
    emergency_fn = 0
    emergency_tn = 0
    
    policy_correct = 0
    intent_correct = 0
    disclaimer_count = 0
    
    detailed_results = []
    latencies = []

    for case in test_cases:
        query = case["query"]
        expected_intent = case["expected_intent"]
        expected_emergency = case["expected_emergency"]
        expected_action = case["expected_policy_action"]
        
        start_time = time.perf_counter()
        
        # 1. Guardrail assessment
        assessment = detector.assess(query)
        
        # 2. End-to-end LangGraph execution
        graph_output = run_medicine_assistant(query)
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        latencies.append(elapsed_ms)
        
        # Evaluate emergency detection
        actual_emergency = assessment.is_emergency
        if expected_emergency and actual_emergency:
            emergency_tp += 1
        elif not expected_emergency and actual_emergency:
            emergency_fp += 1
        elif expected_emergency and not actual_emergency:
            emergency_fn += 1
        else:
            emergency_tn += 1
            
        # Evaluate policy action
        actual_action = assessment.policy_action
        action_match = (actual_action == expected_action)
        if action_match:
            policy_correct += 1
            
        # Evaluate intent
        actual_intent = graph_output.get("intent")
        intent_match = (actual_intent == expected_intent)
        if intent_match:
            intent_correct += 1
            
        # Check disclaimer presence
        has_disclaimer = graph_output.get("disclaimer_included", False)
        if has_disclaimer:
            disclaimer_count += 1

        detailed_results.append({
            "id": case["id"],
            "category": case["category"],
            "query": query,
            "expected_intent": expected_intent,
            "actual_intent": actual_intent,
            "intent_match": intent_match,
            "expected_emergency": expected_emergency,
            "actual_emergency": actual_emergency,
            "expected_policy_action": expected_action,
            "actual_policy_action": actual_action,
            "action_match": action_match,
            "disclaimer_present": has_disclaimer,
            "latency_ms": round(elapsed_ms, 2)
        })

    # Calculate metrics
    precision = emergency_tp / (emergency_tp + emergency_fp) if (emergency_tp + emergency_fp) > 0 else 1.0
    recall = emergency_tp / (emergency_tp + emergency_fn) if (emergency_tp + emergency_fn) > 0 else 1.0
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    accuracy_policy = (policy_correct / total_tests) * 100 if total_tests > 0 else 0.0
    accuracy_intent = (intent_correct / total_tests) * 100 if total_tests > 0 else 0.0
    disclaimer_compliance = (disclaimer_count / total_tests) * 100 if total_tests > 0 else 0.0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

    summary = {
        "total_test_cases": total_tests,
        "emergency_detection": {
            "true_positives": emergency_tp,
            "false_positives": emergency_fp,
            "false_negatives": emergency_fn,
            "true_negatives": emergency_tn,
            "precision": round(precision * 100, 2),
            "recall": round(recall * 100, 2),
            "f1_score": round(f1_score * 100, 2)
        },
        "policy_adherence_accuracy_percent": round(accuracy_policy, 2),
        "intent_classification_accuracy_percent": round(accuracy_intent, 2),
        "disclaimer_safety_compliance_percent": round(disclaimer_compliance, 2),
        "average_pipeline_latency_ms": round(avg_latency, 2),
        "detailed_results": detailed_results
    }

    # Save benchmark results
    out_path = Path(__file__).resolve().parent / "benchmark_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary

if __name__ == "__main__":
    res = run_evaluation_suite()
    print("Benchmark complete.")
