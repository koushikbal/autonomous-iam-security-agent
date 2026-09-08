from langgraph.graph import END, START, StateGraph
from src.config import get_settings
from src.nodes.checkov_scanner import scan
from src.nodes.git_publisher import publish
from src.nodes.iam_context_builder import build_context
from src.nodes.iac_remediator import remediate
from src.nodes.validation_gate import validate
from src.state import AgentState

def _route(state: AgentState) -> str:
    if state.is_secure:
        return "publish"
    if state.validation_attempts < get_settings().max_validation_attempts:
        return "remediate"
    return END

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("scan", scan); graph.add_node("context", build_context); graph.add_node("remediate", remediate); graph.add_node("validate", validate); graph.add_node("publish", publish)
    graph.add_edge(START, "scan"); graph.add_edge("scan", "context"); graph.add_edge("context", "remediate"); graph.add_edge("remediate", "validate")
    graph.add_conditional_edges("validate", _route, {"remediate": "remediate", "publish": "publish", END: END}); graph.add_edge("publish", END)
    return graph.compile()

