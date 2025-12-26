"""
LangGraph Workflow Runner for BinusBrain
Owns orchestration, state, routing
"""

from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from src.upload_handler import upload_handler
from src.kg_extractor import kg_extractor
from src.query_engine import query_engine
from src.neo4j_client import neo4j_client


class AgentState(TypedDict):
    user_id: str
    action: str

    file_data: Optional[bytes]
    filename: Optional[str]
    extracted_text: Optional[str]
    file_type: Optional[str]
    processing_result: Optional[dict]

    question: Optional[str]
    query_result: Optional[dict]

    graph_data: Optional[dict]

    messages: Annotated[list, "conversation messages"]
    error: Optional[str]
    success: bool


class BinusBrainWorkflow:
    def __init__(self):
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        graph = StateGraph(AgentState)

        graph.add_node("route", self._route)
        graph.add_node("upload", self._upload)
        graph.add_node("extract", self._extract)
        graph.add_node("query", self._query)
        graph.add_node("visualize", self._visualize)
        graph.add_node("error", self._error)

        graph.set_entry_point("route")

        graph.add_conditional_edges(
            "route",
            self._route_action,
            {
                "upload": "upload",
                "query": "query",
                "visualize": "visualize",
                "error": "error"
            }
        )

        graph.add_edge("upload", "extract")
        graph.add_edge("extract", END)
        graph.add_edge("query", END)
        graph.add_edge("visualize", END)
        graph.add_edge("error", END)

        return graph.compile()

    def _route(self, state: AgentState) -> AgentState:
        return state

    def _route_action(self, state: AgentState) -> str:
        if state.get("error"):
            return "error"
        return state.get("action", "error")

    def _upload(self, state: AgentState) -> AgentState:
        extracted_text, file_type = upload_handler.process_upload(
            state["file_data"],
            state["filename"],
            state["user_id"]
        )

        if not extracted_text:
            return {**state, "error": "Text extraction failed"}

        return {
            **state,
            "extracted_text": extracted_text,
            "file_type": file_type
        }

    def _extract(self, state: AgentState) -> AgentState:
        result = kg_extractor.extract_from_single_text(
            state["extracted_text"],
            state["user_id"]
        )

        return {
            **state,
            "processing_result": result,
            "success": True
        }

    def _query(self, state: AgentState) -> AgentState:
        result = query_engine.generate_answer(
            state["question"],
            state["user_id"]
        )
        return {**state, "query_result": result, "success": True}

    def _visualize(self, state: AgentState) -> AgentState:
        graph_data = neo4j_client.get_user_graph_data(state["user_id"])
        return {**state, "graph_data": graph_data, "success": True}

    def _error(self, state: AgentState) -> AgentState:
        return {**state, "success": False}


# singleton workflow
_workflow = BinusBrainWorkflow()

def run_agent(state: dict) -> dict:
    if "messages" not in state:
        state["messages"] = []
    return _workflow.workflow.invoke(state)