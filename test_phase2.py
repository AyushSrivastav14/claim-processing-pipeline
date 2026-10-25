from core.schemas import IdentityInfo
from core.state import AgentState
from core.llm_factory import LLMFactory

def run_test():
    print("=== Phase 2 Schema & Extraction Test ===")
    
    # 1. Test State Initialization
    print("[*] Testing AgentState dictionary...")
    mock_state: AgentState = {
        "claim_id": "TEST-123",
        "raw_pages": {1: "Mock text"},
        "categorized_pages": {},
        "id_data": {},
        "discharge_data": {},
        "bill_data": {},
        "final_output": {}
    }
    print("[+] AgentState initialized successfully.")

    # 2. Test Pydantic Schema Validation
    print("\n[*] Testing Pydantic Schema validation...")
    mock_id = IdentityInfo(
        patient_name="John Doe",
        dob="01-JAN-1990",
        id_numbers=["ID-12345"],
        policy_details="POL-999"
    )
    print(f"[+] Schema valid: {mock_id.model_dump()}")

    # 3. Test LLM Structured Output against Qwen 3B
    print("\n[*] Testing LLM Extraction with Qwen 2.5:3b...")
    llm = LLMFactory.get_llm(temperature=0)
    
    # Sample text mimicking pages 1 and 3 from the PDF
    sample_text = """
    GOVERNMENT ID CARD
    Full Name: JOHN MICHAEL SMITH
    ID Number: ID-987-654-321
    Date of Birth: 15-MAR-1985
    MEDICAL CLAIM FORM
    Policy Number: POL-987654321
    """
    
    try:
        # LangChain magic: Bind the Pydantic schema directly to the model
        structured_llm = llm.with_structured_output(IdentityInfo)
        
        print("[*] Prompting LLM to extract data into IdentityInfo schema (this may take a few seconds)...")
        prompt = f"Extract the identity and policy information from the following text into the requested JSON schema:\n\n{sample_text}"
        
        result = structured_llm.invoke(prompt)
        
        print("\n[+] Extraction Successful! The 3B model understands the schema:")
        print(result.model_dump_json(indent=2))
        
    except Exception as e:
        print(f"\n[!] LLM Extraction Failed: {e}")

if __name__ == "__main__":
    run_test()