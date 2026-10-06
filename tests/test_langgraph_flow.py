import unittest
from app.graph.workflow import run_medicine_assistant

class TestLangGraphFlow(unittest.TestCase):
    def test_emergency_halt_flow(self):
        state = run_medicine_assistant("I have chest pain and my left arm feels numb.")
        self.assertTrue(state.get("escalation_triggered"))
        self.assertTrue(state.get("disclaimer_included"))
        self.assertEqual(state.get("intent"), "EMERGENCY_RED_FLAG")
        self.assertIn("911", state.get("response_text"))

    def test_interaction_agent_flow(self):
        state = run_medicine_assistant("Can I take ibuprofen with my blood pressure medication?")
        self.assertFalse(state.get("escalation_triggered"))
        self.assertEqual(state.get("intent"), "INTERACTION_CHECK")
        self.assertTrue(state.get("disclaimer_included"))
        self.assertIn("Interaction", state.get("response_text"))

    def test_drug_info_flow(self):
        state = run_medicine_assistant("What is paracetamol used for and what are its side effects?")
        self.assertFalse(state.get("escalation_triggered"))
        self.assertEqual(state.get("intent"), "DRUG_INFO")
        self.assertTrue(state.get("disclaimer_included"))
        self.assertIn("Paracetamol", state.get("response_text"))

    def test_generic_flow(self):
        state = run_medicine_assistant("Is there a cheaper generic for Lipitor?")
        self.assertFalse(state.get("escalation_triggered"))
        self.assertEqual(state.get("intent"), "GENERIC_LOOKUP")
        self.assertTrue(state.get("disclaimer_included"))
        self.assertIn("Atorvastatin", state.get("response_text"))

if __name__ == "__main__":
    unittest.main()
