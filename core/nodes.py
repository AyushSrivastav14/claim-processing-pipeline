from core.state import AgentState
from core.schemas import IdentityInfo, DischargeSummary, ItemizedBill, PageClassification
from core.llm_factory import LLMFactory
import time
import os

def apply_rate_limit_stagger(agent_name: str):
    """
    Staggers API calls to bypass free-tier TPM limits by spacing out parallel node execution.
    """
    is_free_tier = os.getenv("FREE_TIER", "false").lower() == "true"
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    
    if is_free_tier and provider != "ollama":
        # Segregator already ran. Offset the parallel agents.
        stagger_map = {
            "id_agent": 10,        # Let the segregator's token window clear slightly
            "discharge_agent": 65, # Pushes into the next minute's token bucket
            "bill_agent": 125      # Pushes into the third minute's token bucket
        }
        
        delay = stagger_map.get(agent_name, 0)
        if delay > 0:
            print(f"[*] FREE_TIER Hack: {agent_name} sleeping for {delay} seconds...")
            time.sleep(delay)

def segregator_node(state: AgentState) -> dict:
    """
    Analyzes each raw page and categorizes it into the 9 required types.
    Returns a dictionary containing only the state updates.
    """
    print("--- [NODE] SEGREGATOR AGENT ---")
    raw_pages = state.get("raw_pages", {})
    
    # Initialize the LLM with the structured output binding
    llm = LLMFactory.get_llm(temperature=0)
    structured_llm = llm.with_structured_output(PageClassification)
    
    categorized_pages = {
        "claim_forms": [],
        "cheque_or_bank_details": [],
        "identity_document": [],
        "itemized_bill": [],
        "discharge_summary": [],
        "prescription": [],
        "investigation_report": [],
        "cash_receipt": [],
        "other": []
    }
    
    for page_num, text in raw_pages.items():
        if not text.strip():
            continue
            
        # We truncate to the first 1500 chars to save context window and speed up the 3B model
        prompt = (
            "Analyze the following document page and classify it into exactly one of the allowed categories.\n\n"
            f"Page Text:\n{text[:1500]}\n" 
        )
        
        try:
            result = structured_llm.invoke(prompt)
            categorized_pages[result.category].append(page_num)
            print(f"[*] Page {page_num} -> {result.category}")
            time.sleep(0.5)  # Slight delay to avoid overwhelming the LLM
        except Exception as e:
            print(f"[!] Error classifying page {page_num}, routing to 'other': {e}")
            categorized_pages["other"].append(page_num) 
            
    time.sleep(1) # Final delay to ensure all LLM calls are completed before returning
    # LangGraph automatically merges this returned dictionary into the master AgentState
    return {"categorized_pages": categorized_pages}

def get_text_for_category(state: AgentState, categories: list[str]) -> str:
    """Helper function to fetch full, untruncated text for specific categories."""
    raw_pages = state.get("raw_pages", {})
    categorized = state.get("categorized_pages", {})
    
    combined_text = []
    for cat in categories:
        page_nums = categorized.get(cat, [])
        for num in page_nums:
            if num in raw_pages:
                combined_text.append(raw_pages[num])
                
    return "\n\n".join(combined_text)

def id_agent_node(state: AgentState) -> dict:
    print("--- [NODE] ID AGENT ---")
    apply_rate_limit_stagger("id_agent")
    # Identity info spans both the ID card and the claim form (for policy details)
    text = get_text_for_category(state, ["identity_document", "claim_forms"])
    
    if not text.strip():
        print("[!] No identity pages routed to ID Agent.")
        return {"id_data": {}}
        
    llm = LLMFactory.get_llm(temperature=0).with_structured_output(IdentityInfo)
    result = llm.invoke(f"Extract identity and policy info from the following text:\n\n{text}")
    return {"id_data": result.model_dump()}

def discharge_agent_node(state: AgentState) -> dict:
    print("--- [NODE] DISCHARGE AGENT ---")
    apply_rate_limit_stagger("discharge_agent")
    text = get_text_for_category(state, ["discharge_summary"])
    
    if not text.strip():
        print("[!] No discharge pages routed to Discharge Agent.")
        return {"discharge_data": {}}
    llm = LLMFactory.get_llm(temperature=0).with_structured_output(DischargeSummary)
    result = llm.invoke(f"Extract the discharge summary details:\n\n{text}")
    
    return {"discharge_data": result.model_dump()}

def bill_agent_node(state: AgentState) -> dict:
    print("--- [NODE] ITEM BILL AGENT ---")
    apply_rate_limit_stagger("bill_agent")
    text = get_text_for_category(state, ["itemized_bill"])
    
    if not text.strip():
        print("[!] No billing pages routed to Bill Agent.")
        return {"bill_data": {}}
    time.sleep(1)  # Slight delay to avoid overwhelming the LLM
    llm = LLMFactory.get_llm(temperature=0).with_structured_output(ItemizedBill)
    result = llm.invoke(f"Extract all line items and the total amount from this bill:\n\n{text}")
    return {"bill_data": result.model_dump()}

def aggregator_node(state: AgentState) -> dict:
    print("--- [NODE] AGGREGATOR ---")
    final_output = {
        "claim_id": state.get("claim_id"),
        "patient_identity": state.get("id_data", {}),
        "discharge_details": state.get("discharge_data", {}),
        "billing_details": state.get("bill_data", {})
    }
    return {"final_output": final_output}