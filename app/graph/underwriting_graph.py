from __future__ import annotations

from app.graph.nodes import (
    anomaly_detection, apply_policy_node, build_financial_profile, calculate_financial_metrics,
    calculate_risk_node, check_documents, classify_documents, extract_documents,
    generate_recommendation_node, load_case, persist_analysis, request_documents,
)
from app.graph.state import UnderwritingState


def _merge(state: dict, update: dict | None) -> dict:
    if update:
        state.update(update)
    return state


class SequentialFallbackGraph:
    """Development fallback used only when langgraph is not installed.

    requirements.txt installs LangGraph for the real hackathon runtime. Keeping this
    fallback makes deterministic unit/e2e tests possible in constrained environments.
    """
    def invoke(self, initial_state: UnderwritingState):
        state = dict(initial_state)
        _merge(state, load_case(state)); _merge(state, check_documents(state))
        if state.get('route') != 'continue':
            _merge(state, request_documents(state)); return state
        for node in (
            classify_documents, extract_documents, build_financial_profile,
            calculate_financial_metrics, anomaly_detection, calculate_risk_node,
            apply_policy_node, generate_recommendation_node, persist_analysis,
        ):
            _merge(state, node(state))
        return state


def build_underwriting_graph():
    try:
        from langgraph.graph import END, START, StateGraph
    except ModuleNotFoundError:
        return SequentialFallbackGraph()

    graph = StateGraph(UnderwritingState)
    graph.add_node('load_case', load_case)
    graph.add_node('check_documents', check_documents)
    graph.add_node('request_documents', request_documents)
    graph.add_node('classify_documents', classify_documents)
    graph.add_node('extract_documents', extract_documents)
    graph.add_node('build_financial_profile', build_financial_profile)
    graph.add_node('calculate_metrics', calculate_financial_metrics)
    graph.add_node('anomaly_detection', anomaly_detection)
    graph.add_node('calculate_risk', calculate_risk_node)
    graph.add_node('apply_policy', apply_policy_node)
    graph.add_node('generate_recommendation', generate_recommendation_node)
    graph.add_node('persist_analysis', persist_analysis)

    graph.add_edge(START, 'load_case')
    graph.add_edge('load_case', 'check_documents')
    graph.add_conditional_edges('check_documents', lambda s: s.get('route', 'request_documents'), {
        'continue': 'classify_documents', 'request_documents': 'request_documents'
    })
    graph.add_edge('request_documents', END)
    graph.add_edge('classify_documents', 'extract_documents')
    graph.add_edge('extract_documents', 'build_financial_profile')
    graph.add_edge('build_financial_profile', 'calculate_metrics')
    graph.add_edge('calculate_metrics', 'anomaly_detection')
    graph.add_edge('anomaly_detection', 'calculate_risk')
    graph.add_edge('calculate_risk', 'apply_policy')
    graph.add_edge('apply_policy', 'generate_recommendation')
    graph.add_edge('generate_recommendation', 'persist_analysis')
    graph.add_edge('persist_analysis', END)
    return graph.compile()


underwriting_graph = build_underwriting_graph()
