import unittest
from app.mcp.tools.drug_info import get_drug_info
from app.mcp.tools.check_interaction import check_drug_interaction
from app.mcp.tools.find_generic import find_generic_equivalent
from app.mcp.server import mcp_server

class TestMCPTools(unittest.TestCase):
    def test_drug_info_paracetamol(self):
        info = get_drug_info("paracetamol")
        self.assertTrue(info["found"])
        self.assertEqual(info["generic_name"], "Paracetamol (Acetaminophen)")
        self.assertIn("Mild to moderate pain", info["approved_uses"][0])

    def test_interaction_ibuprofen_lisinopril(self):
        res = check_drug_interaction(["ibuprofen", "lisinopril"])
        self.assertTrue(res["interactions_found"])
        self.assertIn(res["highest_severity"], ["Moderate", "High / Severe"])

    def test_find_generic_lipitor(self):
        gen = find_generic_equivalent("Lipitor")
        self.assertTrue(gen["found"])
        self.assertEqual(gen["generic_name"], "Atorvastatin Calcium")
        self.assertIn("AB Rated", gen["therapeutic_equivalence"])

    def test_mcp_server_list_tools(self):
        tools = mcp_server.list_tools()
        tool_names = [t["name"] for t in tools]
        self.assertIn("drug_info", tool_names)
        self.assertIn("check_interaction", tool_names)
        self.assertIn("find_generic", tool_names)

    def test_mcp_json_rpc(self):
        rpc_req = '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'
        resp_str = mcp_server.handle_json_rpc(rpc_req)
        self.assertIn("drug_info", resp_str)

if __name__ == "__main__":
    unittest.main()
