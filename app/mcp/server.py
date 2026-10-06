import json
import sys
from typing import Dict, Any, List
from .tools.drug_info import get_drug_info
from .tools.check_interaction import check_drug_interaction
from .tools.find_generic import find_generic_equivalent
from .tools.web_search import search_health_advisories

MCP_TOOLS_MANIFEST = [
    {
        "name": "drug_info",
        "description": "Returns verified uses, common side effects, severe warnings, and dosage precautions for a medicine.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "drug_name": {
                    "type": "string",
                    "description": "Name of the medicine (brand or generic), e.g. 'Paracetamol', 'Ibuprofen', 'Lisinopril'."
                }
            },
            "required": ["drug_name"]
        }
    },
    {
        "name": "check_interaction",
        "description": "Checks known clinical interactions between two or more medicines and returns severity, mechanism, and recommendations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "drugs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of 2 or more medicine names to check, e.g. ['ibuprofen', 'lisinopril']."
                }
            },
            "required": ["drugs"]
        }
    },
    {
        "name": "find_generic",
        "description": "Returns generic equivalents, bioequivalence ratings, and cost saving insights for a branded medicine.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "medicine_name": {
                    "type": "string",
                    "description": "Branded medicine name or generic name, e.g. 'Tylenol', 'Lipitor', 'Advil'."
                }
            },
            "required": ["medicine_name"]
        }
    },
    {
        "name": "search_health_advisories",
        "description": "Searches for current health advisories, outbreak news, and drug recall notices.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Advisory search query, e.g. 'FDA drug recall cough syrup' or 'outbreak news'."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Max results to return (default 3)",
                    "default": 3
                }
            },
            "required": ["query"]
        }
    }
]

class MCPServer:
    """Standard Model Context Protocol (MCP) server for Healthcare Assistant Tools."""

    def __init__(self):
        self.tools = {
            "drug_info": get_drug_info,
            "check_interaction": check_drug_interaction,
            "find_generic": find_generic_equivalent,
            "search_health_advisories": search_health_advisories
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        return MCP_TOOLS_MANIFEST

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name not in self.tools:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Error: Tool '{tool_name}' not found."}]
            }
        
        handler = self.tools[tool_name]
        try:
            result = handler(**arguments)
            return {
                "isError": False,
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
                "raw_result": result
            }
        except Exception as e:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Execution error in tool '{tool_name}': {str(e)}"}]
            }

    def handle_json_rpc(self, request_str: str) -> str:
        """Handle standard JSON-RPC 2.0 MCP request."""
        try:
            req = json.loads(request_str)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "tools/list":
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": self.list_tools()}
                })
            elif method == "tools/call":
                name = params.get("name")
                args = params.get("arguments", {})
                res = self.call_tool(name, args)
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": res
                })
            else:
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method '{method}' not implemented"}
                })
        except Exception as e:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
            })

    def run_stdio(self):
        """Run MCP server in stdio mode for direct IDE/CLI integration."""
        for line in sys.stdin:
            if not line.strip():
                continue
            response = self.handle_json_rpc(line)
            sys.stdout.write(response + "\n")
            sys.stdout.flush()

mcp_server = MCPServer()

if __name__ == "__main__":
    mcp_server.run_stdio()
