import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")

from evaluation.eval_runner import run_evaluation_suite

def main():
    print("\n" + "=" * 70)
    print("🏥 HEALTHCARE ASSISTANT — GUARDRAIL & AGENT EVALUATION BENCHMARK")
    print("=" * 70)
    
    results = run_evaluation_suite()
    
    em = results["emergency_detection"]
    print(f"\n📊 SUMMARY METRICS (Total Queries: {results['total_test_cases']}):")
    print(f"  • Emergency Detection Recall:     {em['recall']}%  (Target: 100.0%)")
    print(f"  • Emergency Detection Precision:  {em['precision']}%")
    print(f"  • Emergency F1 Score:             {em['f1_score']}%")
    print(f"  • Policy Adherence Accuracy:      {results['policy_adherence_accuracy_percent']}%")
    print(f"  • Intent Routing Accuracy:        {results['intent_classification_accuracy_percent']}%")
    print(f"  • Disclaimer Safety Compliance:   {results['disclaimer_safety_compliance_percent']}%  (Mandatory: 100.0%)")
    print(f"  • Average Latency per Query:      {results['average_pipeline_latency_ms']} ms")
    print("\n" + "-" * 70)
    print("🔍 DETAILED TEST BREAKDOWN:")
    print("-" * 70)
    for r in results["detailed_results"]:
        status_sym = "✅ PASS" if (r["intent_match"] and r["action_match"]) else "⚠️ MISMATCH"
        print(f"[{r['id']}] {status_sym} | {r['category']:<35} | Intent: {r['actual_intent']} ({r['latency_ms']}ms)")
    print("=" * 70 + "\n")
    print("Full JSON benchmark report saved to: evaluation/benchmark_results.json\n")

if __name__ == "__main__":
    main()
