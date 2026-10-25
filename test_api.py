import os
import json
import requests
from core.llm_factory import LLMFactory

def test_llm_factory():
    print("=== 1. Testing LLMFactory Configuration ===")
    try:
        llm = LLMFactory.get_llm(temperature=0)
        print(f"[+] Successfully instantiated: {llm.__class__.__name__}")
        
        endpoint = getattr(llm, "base_url", "Cloud API")
        model_name = getattr(llm, "model", getattr(llm, "model_name", "Unknown"))
        
        print(f"    Targeting endpoint: {endpoint}")
        print(f"    Model name: {model_name}")
    except Exception as e:
        print(f"[!] LLMFactory failed: {e}")

def test_fastapi_endpoint():
    print("\n=== 2. Testing FastAPI Endpoint ===")
    url = "http://127.0.0.1:8000/api/process"
    
    # Check for the PDF file
    pdf_path = "final.pdf"
    if not os.path.exists(pdf_path):
        pdf_path = "final (1).pdf" # Fallback based on your previous logs
        if not os.path.exists(pdf_path):
            print(f"[!] Error: Could not find {pdf_path} in the current directory.")
            return

    print(f"[*] Preparing to send {pdf_path} to {url}")
    print("[*] Note: Ensure your FastAPI server is running in another terminal window!")
    
    try:
        with open(pdf_path, "rb") as f:
            # Construct the multipart/form-data payload
            files = {"file": (pdf_path, f, "application/pdf")}
            data = {"claim_id": "CLM-API-TEST-999"}
            
            print("[*] Waiting for API response (this may take a minute)...")
            response = requests.post(url, data=data, files=files)
            
        print(f"\n[*] HTTP Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("[+] API Request Successful! Extracted JSON Payload:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"[!] API Request Failed.")
            print(f"    Error Details: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n[!] Connection Refused.")
        print("    Did you forget to start the FastAPI server?")
        print("    Run 'uvicorn main:app --reload' in a separate terminal.")

if __name__ == "__main__":
    test_llm_factory()
    test_fastapi_endpoint()