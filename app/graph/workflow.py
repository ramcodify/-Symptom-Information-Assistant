from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from .state import MedicineAssistantState
from .nodes.guardrail_node import guardrail_node
from .nodes.escalation_node import escalation_node
from .nodes.interaction_node import interaction_node
from .nodes.info_node import info_node
from .nodes.disclaimer_node import disclaimer_node

def route_after_guardrail(state: MedicineAssistantState) -> Literal["escalation_node", "interaction_node", "info_node"]:
    """
    Conditional router mapping guardrail classification to specialized agent nodes.
    """
    guardrail = state.get("guardrail_result", {})
    intent = state.get("intent", "GENERAL_HEALTH_RAG")
    
    # 1. Critical Emergency Red-Flag -> Route to Escalation / Interrupt Node
    if guardrail.get("is_emergency") or intent == "EMERGENCY_RED_FLAG":
        return "escalation_node"
    
    # 2. Drug Interaction Query -> Route to Interaction Agent
    if intent == "INTERACTION_CHECK":
        return "interaction_node"
    
    # 3. Everything else (Drug Info, Generic equivalents, Health RAG, Policy Refusals) -> Info Agent
    return "info_node"

def create_medicine_graph():
    """Build and compile the LangGraph workflow."""
    workflow = StateGraph(MedicineAssistantState)
    
    # Add Nodes
    workflow.add_node("guardrail_node", guardrail_node)
    workflow.add_node("escalation_node", escalation_node)
    workflow.add_node("interaction_node", interaction_node)
    workflow.add_node("info_node", info_node)
    workflow.add_node("disclaimer_node", disclaimer_node)
    
    # Add Edges
    workflow.add_edge(START, "guardrail_node")
    
    workflow.add_conditional_edges(
        "guardrail_node",
        route_after_guardrail,
        {
            "escalation_node": "escalation_node",
            "interaction_node": "interaction_node",
            "info_node": "info_node"
        }
    )
    
    # All branches pass through disclaimer before completion
    workflow.add_edge("escalation_node", "disclaimer_node")
    workflow.add_edge("interaction_node", "disclaimer_node")
    workflow.add_edge("info_node", "disclaimer_node")
    workflow.add_edge("disclaimer_node", END)
    
    return workflow.compile()

medicine_app = create_medicine_graph()

def run_medicine_assistant(query: str, history: list = None) -> Dict[str, Any]:
    """Execute the compiled LangGraph assistant pipeline on a query."""
    initial_state: MedicineAssistantState = {
        "query": query,
        "history": history or [],
        "guardrail_result": {},
        "intent": "GENERAL_HEALTH_RAG",
        "extracted_drugs": [],
        "tool_results": {},
        "rag_context": [],
        "response_text": "",
        "escalation_triggered": False,
        "disclaimer_included": False,
        "interrupted": False,
        "status": "INITIALIZED",
        "sources": [],
        "metadata": {}
    }
    
    final_state = medicine_app.invoke(initial_state)
    return final_state
