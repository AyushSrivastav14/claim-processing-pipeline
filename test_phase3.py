import json
from core.pdf_processor import PDFProcessor
from core.graph import workflow_app

def run_test():
    print("=== Phase 3 LangGraph Orchestration Test ===")
    
    pdf_path = "final.pdf"
    
    # 1. Ingest the PDF
    print(f"[*] Reading and parsing {pdf_path}...")
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
    except FileNotFoundError:
        print(f"[!] Error: {pdf_path} not found.")
        return
        
    extracted_pages = PDFProcessor.extract_pages_from_bytes(pdf_bytes)
    print(f"[+] Extracted {len(extracted_pages)} pages.")
    
    # 2. Initialize the Graph State
    initial_state = {
        "claim_id": "CLM-2024-789456",
        "raw_pages": extracted_pages
    }
    
    # 3. Invoke the Graph
    print("\n[*] Invoking LangGraph Workflow...")
    print("[*] Note: The Segregator is analyzing 18 pages. With a 3B model running locally, this may take 1-3 minutes.")
    print("-" * 40)
    
    try:
        # The invoke method runs the graph synchronously
        final_state = workflow_app.invoke(initial_state)
        
        print("-" * 40)
        print("\n[+] Graph Execution Complete!")
        print("\n=== FINAL AGGREGATED JSON OUTPUT ===")
        
        # Pretty print the final output
        final_json = final_state.get("final_output", {})
        print(json.dumps(final_json, indent=2))
        
    except Exception as e:
        print(f"\n[!] Graph Execution Failed: {e}")

if __name__ == "__main__":
    run_test()