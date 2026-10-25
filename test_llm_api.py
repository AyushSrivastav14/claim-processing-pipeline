import os
import json
from pydantic import BaseModel, Field
from core.llm_factory import LLMFactory

# Define a simple schema to test the structured output capability
class DiagnosticResponse(BaseModel):
    status: str = Field(description="Set this to 'Connected'")
    model_acknowledged: str = Field(description="The name of the model you are running on")
    message: str = Field(description="A brief hello world message")

def test_groq_connection():
    print("=== Groq API Direct Invocation Test ===")
    
    provider = os.getenv("LLM_PROVIDER", "Not set")
    model = os.getenv("CLOUD_MODEL_NAME", "Not set")
    print(f"[*] Configured Provider: {provider}")
    print(f"[*] Configured Model: {model}")
    
    if not os.getenv("GROQ_API_KEY"):
        print("[!] WARNING: GROQ_API_KEY is missing from environment variables.")

    print("\n[*] Initializing LLMFactory...")
    try:
        llm = LLMFactory.get_llm(temperature=0)
        print(f"[+] Loaded class: {llm.__class__.__name__}")
    except Exception as e:
        print(f"[!] Factory initialization failed: {e}")
        return

    print("\n[*] Invoking API with strict JSON schema...")
    try:
        # Bind the Pydantic schema just like we do in the extraction agents
        structured_llm = llm.with_structured_output(DiagnosticResponse)
        
        prompt = "Hello! Please confirm you are online, identify the model you are using, and say a quick hello."
        response = structured_llm.invoke(prompt)
        
        print("\n[+] API Invocation Successful!")
        print("=== EXTRACTED JSON ===")
        print(json.dumps(response.model_dump(), indent=2))
        
    except Exception as e:
        print(f"\n[!] API Invocation Failed: {e}")
        print("    Ensure your GROQ_API_KEY is valid and the model name is correct.")

if __name__ == "__main__":
    test_groq_connection()