import os
from core.pdf_processor import PDFProcessor
from core.llm_factory import LLMFactory

def run_test():
    print("=== Phase 1 Sandbox Test ===")
    
    # 1. Test PDF Extraction
    pdf_path = "final.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"[!] Error: '{pdf_path}' not found in the current directory.")
        return

    print(f"\n[*] Reading bytes from {pdf_path}...")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    print("[*] Passing bytes to PDFProcessor...")
    extracted_pages = PDFProcessor.extract_pages_from_bytes(pdf_bytes)
    
    print(f"[+] Successfully extracted {len(extracted_pages)} pages.")
    
    # Preview Page 1 to ensure PyMuPDF parsed the tabular/form data cleanly
    if 1 in extracted_pages:
        print("\n--- Preview of Page 1 (First 250 chars) ---")
        print(extracted_pages[1][:250] + "...")
        print("-------------------------------------------\n")

    # 2. Test LLM Factory (Local Environment)
    print("[*] Testing LLMFactory initialization...")
    
    # We leave LLM_PROVIDER unset so it defaults to "local"

    try:
        llm = LLMFactory.get_llm(temperature=0)
        print(f"[+] Successfully instantiated LLM class: {llm.__class__.__name__}")
        
        # Safely fetch base_url if it exists, otherwise default to "Cloud API"
        endpoint = getattr(llm, "base_url", "Cloud API")
        model_name = getattr(llm, "model", getattr(llm, "model_name", "Unknown"))
        
        print(f"    Targeting endpoint: {endpoint}")
        print(f"    Model name: {model_name}")
    except Exception as e:
        print(f"[!] LLMFactory failed: {e}")


if __name__ == "__main__":
    run_test()