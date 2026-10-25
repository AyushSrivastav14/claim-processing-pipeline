from typing import TypedDict, Dict, List, Any
from core.schemas import IdentityInfo, DischargeSummary, ItemizedBill

class AgentState(TypedDict):
    """The shared state payload passed between LangGraph nodes."""
    claim_id: str
    raw_pages: Dict[int, str]              # Input: Page num -> text
    
    # Segregator Output
    categorized_pages: Dict[str, List[int]] # Mapping: category -> list of page numbers
    
    # Extraction Agent Outputs
    id_data: dict                          # Will hold IdentityInfo dict
    discharge_data: dict                   # Will hold DischargeSummary dict
    bill_data: dict                        # Will hold ItemizedBill dict
    
    # Final API Output
    final_output: dict