# 🚀 Local Execution & Setup Instructions

This guide covers how to configure and run the AI-driven Medical Claim Processing Pipeline locally on your machine. The pipeline supports two execution modes: **Ollama (100% Local)** and **Groq (Cloud API)**.

## 1. Choose Your Execution Mode

### Mode A: Local Inference via Ollama (Private & Offline)

This mode runs the Qwen model entirely on your local hardware. It is slower but guarantees complete data privacy as no documents leave your machine.

**Step 1: Install Ollama**
If you are using WSL/Linux, run this command to install Ollama:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```
*(For Windows/Mac, download the installer directly from [ollama.com](https://ollama.com/download))*

**Step 2: Pull the Model**
Download the local Qwen model (this may take a few minutes depending on your internet speed):

```bash
ollama pull qwen2.5:3b
```

**Step 3: Set Ollama Environment Variables**
Ensure Ollama is running in the background, then set your environment variables:

```env
LLM_PROVIDER="ollama"
LOCAL_MODEL_NAME="qwen2.5:3b"
FREE_TIER="false"
```

### Mode B: Cloud Inference via Groq 

This mode connects to Groq's LPU infrastructure for near-instant inference using the 27B parameter Qwen model. It requires a free Groq API key.

**Step 1: Get an API Key**
Generate an API key at [console.groq.com](https://console.groq.com/keys).

**Step 2: Set Groq Environment Variables**

```env
LLM_PROVIDER="groq"
CLOUD_MODEL_NAME="qwen/qwen3.8-27b"
GROQ_API_KEY="gsk_your_actual_api_key_here"

# Set to "true" to enable the stagger delay (bypasses Groq's 7,000 ITPM free-tier limit)
FREE_TIER="true" 
```

## 2. Standard Local Setup (Virtual Environment)

To run the Python application directly on your machine:

```bash
# 1. Create and activate a virtual environment (if not already done)
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 3. Local Docker Execution

To run the pipeline inside an isolated container on your machine:

```bash
# 1. Build the Docker image
docker build -t claim-pipeline:v1 .

# 2. Run the container (Example using Groq mode)
docker run -p 8000:8000 \
  -e PYTHONUNBUFFERED=1 \
  -e LLM_PROVIDER="groq" \
  -e CLOUD_MODEL_NAME="qwen/qwen3.8-27b" \
  -e GROQ_API_KEY="your_api_key_here" \
  -e FREE_TIER="true" \
  claim-pipeline:v1
```
*The API will be available at `http://localhost:8000/api/process`. All application logs, including the LangGraph staggered delays, will stream directly to this terminal.*