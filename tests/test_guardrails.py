import unittest
from app.guardrails.detector import GuardrailDetector

class TestGuardrails(unittest.TestCase):
    def setUp(self):
        self.detector = GuardrailDetector()

    def test_emergency_chest_pain(self):
        res = self.detector.assess("I have chest pain and my left arm feels numb.")
        self.assertTrue(res.is_emergency)
        self.assertEqual(res.policy_action, "ESCALATE_EMERGENCY")
        self.assertEqual(res.intent_category, "EMERGENCY_RED_FLAG")

    def test_emergency_stroke_fast(self):
        res = self.detector.assess("My father has facial drooping and slurred speech.")
        self.assertTrue(res.is_emergency)
        self.assertEqual(res.policy_action, "ESCALATE_EMERGENCY")

    def test_emergency_anaphylaxis(self):
        res = self.detector.assess("My throat is swelling up and I cannot breathe after eating peanuts.")
        self.assertTrue(res.is_emergency)
        self.assertEqual(res.policy_action, "ESCALATE_EMERGENCY")

    def test_diagnosis_refusal(self):
        res = self.detector.assess("Do I have lupus? I have joint pain and a butterfly rash.")
        self.assertFalse(res.is_emergency)
        self.assertTrue(res.is_diagnosis_request)
        self.assertEqual(res.policy_action, "REFUSE_DIAGNOSIS")

    def test_prescription_refusal(self):
        res = self.detector.assess("Can you prescribe me amoxicillin 500mg?")
        self.assertFalse(res.is_emergency)
        self.assertTrue(res.is_prescription_request)
        self.assertEqual(res.policy_action, "REFUSE_PRESCRIPTION")

    def test_interaction_intent(self):
        res = self.detector.assess("Can I take ibuprofen with my blood pressure medication?")
        self.assertFalse(res.is_emergency)
        self.assertEqual(res.intent_category, "INTERACTION_CHECK")

    def test_generic_intent(self):
        res = self.detector.assess("Is there a cheaper generic for Lipitor?")
        self.assertFalse(res.is_emergency)
        self.assertEqual(res.intent_category, "GENERIC_LOOKUP")

    def test_drug_info_intent(self):
        res = self.detector.assess("What is paracetamol used for and what are its side effects?")
        self.assertFalse(res.is_emergency)
        self.assertEqual(res.intent_category, "DRUG_INFO")

if __name__ == "__main__":
    unittest.main()
