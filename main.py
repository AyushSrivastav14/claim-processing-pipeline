from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from core.pdf_processor import PDFProcessor
from core.graph import workflow_app
import json

app = FastAPI(title="Claim Processing Pipeline")

# --- HTML FRONTEND ---
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Claim Processing</title>
    <style>
        body { font-family: -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #f9fafb; color: #111827; }
        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        h2 { margin-top: 0; color: #2563eb; }
        .input-group { margin-bottom: 20px; }
        label { display: block; font-weight: bold; margin-bottom: 8px; color: #475569; }
        input[type="text"] { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 16px; }
        .upload-area { border: 2px dashed #cbd5e1; padding: 40px; text-align: center; border-radius: 8px; margin-bottom: 20px; background: #f8fafc; }
        button { background: #2563eb; color: white; border: none; padding: 12px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; font-size: 16px; }
        button:hover { background: #1d4ed8; }
        button:disabled { background: #94a3b8; cursor: not-allowed; }
        pre { background: #1e293b; color: #e2e8f0; padding: 15px; border-radius: 8px; overflow-x: auto; white-space: pre-wrap; }
        #loader { display: none; text-align: center; margin: 20px 0; color: #64748b; font-weight: 500; }
        .error-message { color: #dc2626; font-weight: bold; margin-top: 10px; text-align: center; display: none; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Medical Claim Auto-Extraction</h2>
        <p>Enter the Claim ID and upload a PDF to route pages through the AI pipeline.</p>
        
        <form id="uploadForm">
            <div class="input-group">
                <label for="claimId">Claim ID <span style="color: #dc2626;">*</span></label>
                <input type="text" id="claimId" placeholder="e.g., CLM-2025-789456" required>
            </div>
            
            <div class="upload-area">
                <input type="file" id="pdfFile" accept="application/pdf" required>
            </div>
            
            <button type="submit" id="submitBtn">Process Document</button>
        </form>

        <div id="errorMessage" class="error-message"></div>
        <div id="loader">Processing through AI Segregator and Extraction Agents... This may take some time.</div>
        
        <div id="resultBox" style="display: none; margin-top: 20px;">
            <h3>Extracted JSON Payload:</h3>
            <pre id="jsonOutput"></pre>
        </div>
    </div>

    <script>
        document.getElementById('uploadForm').onsubmit = async (e) => {
            e.preventDefault();
            const claimId = document.getElementById('claimId').value.trim();
            const fileInput = document.getElementById('pdfFile');
            const submitBtn = document.getElementById('submitBtn');
            const loader = document.getElementById('loader');
            const resultBox = document.getElementById('resultBox');
            const errorBox = document.getElementById('errorMessage');
            
            errorBox.style.display = 'none';

            if (!claimId) {
                errorBox.textContent = "Please enter a valid Claim ID.";
                errorBox.style.display = 'block';
                return;
            }

            if (fileInput.files.length === 0) return;

            const formData = new FormData();
            formData.append('claim_id', claimId);
            formData.append('file', fileInput.files[0]);

            submitBtn.disabled = true;
            loader.style.display = 'block';
            resultBox.style.display = 'none';

            try {
                const response = await fetch('/api/process', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to process document');
                }
                
                document.getElementById('jsonOutput').textContent = JSON.stringify(data, null, 2);
                resultBox.style.display = 'block';
            } catch (error) {
                errorBox.textContent = error.message;
                errorBox.style.display = 'block';
            } finally {
                submitBtn.disabled = false;
                loader.style.display = 'none';
            }
        };
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serves the single-page application."""
    return html_content

@app.post("/api/process")
async def process_claim(claim_id: str = Form(...), file: UploadFile = File(...)):
    """
    Ingests a PDF claim, extracts text, and routes it through the LangGraph AI pipeline.
    """
    # Strict backend validation for the claim ID
    if not claim_id or not claim_id.strip():
        raise HTTPException(status_code=400, detail="Claim ID is strictly required.")
        
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        file_bytes = await file.read()
        extracted_pages = PDFProcessor.extract_pages_from_bytes(file_bytes)
        
        if not extracted_pages:
            raise HTTPException(status_code=400, detail="Could not extract text from the provided PDF.")
            
        initial_state = {
            "claim_id": claim_id.strip(),
            "raw_pages": extracted_pages
        }
        
        final_state = workflow_app.invoke(initial_state)
        return final_state.get("final_output", {})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")