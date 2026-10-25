import os
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

class LLMFactory:
    """
    Factory pattern to dynamically switch between local and cloud LLMs
    using environment variables.
    """
    @staticmethod
    def get_llm(temperature=0):
        provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        
        if provider == "groq":
            # Cloud: Groq API
            cloud_model = os.getenv("CLOUD_MODEL_NAME", "llama-3.1-8b-instant")
            return ChatGroq(
                model=cloud_model,
                temperature=temperature,
                max_retries=2
            )
            
        elif provider == "openrouter":
            # Cloud: OpenRouter API (Supports the "qwen/qwen..." format)
            cloud_model = os.getenv("CLOUD_MODEL_NAME", "qwen/qwen-2.5-32b-instruct")
            return ChatOpenAI(
                model=cloud_model,
                temperature=temperature,
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
                max_retries=2
            )
            
        else:
            # Local: Ollama
            local_model = os.getenv("LOCAL_MODEL_NAME", "qwen2.5:3b")
            return ChatOllama(
                model=local_model,
                temperature=temperature,
                base_url="http://localhost:11434"
            )