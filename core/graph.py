from langgraph.graph import StateGraph, START, END
from core.state import AgentState
from core.nodes import (
    segregator_node,
    id_agent_node,
    discharge_agent_node,
    bill_agent_node,
    aggregator_node
)

def build_graph():
    """Compiles the LangGraph orchestration pipeline."""
    
    # 1. Initialize the graph with your shared state schema
    builder = StateGraph(AgentState)
    
    # 2. Add all nodes to the graph
    builder.add_node("segregator", segregator_node)
    builder.add_node("id_agent", id_agent_node)
    builder.add_node("discharge_agent", discharge_agent_node)
    builder.add_node("bill_agent", bill_agent_node)
    builder.add_node("aggregator", aggregator_node)
    
    # 3. Define the Control Flow (Edges)
    # Start -> Segregator
    builder.add_edge(START, "segregator")
    
    # Parallel Branching: Segregator triggers all three extraction agents simultaneously
    builder.add_edge("segregator", "id_agent")
    builder.add_edge("segregator", "discharge_agent")
    builder.add_edge("segregator", "bill_agent")
    
    # Convergence: All three agents must finish before the Aggregator runs
    builder.add_edge("id_agent", "aggregator")
    builder.add_edge("discharge_agent", "aggregator")
    builder.add_edge("bill_agent", "aggregator")
    
    # Aggregator -> End of workflow
    builder.add_edge("aggregator", END)
    
    # Compile into an executable application
    return builder.compile()

# Instantiate the graph for import into your FastAPI app
workflow_app = build_graph()