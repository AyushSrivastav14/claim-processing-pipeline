import pymupdf
from typing import Dict

class PDFProcessor:
    """Handles entirely in-memory document parsing for the LangGraph state."""
    
    @staticmethod
    def extract_pages_from_bytes(file_bytes: bytes) -> Dict[int, str]:
        """
        Extracts text from a PDF byte stream.
        
        Args:
            file_bytes: Raw bytes from the uploaded PDF.
            
        Returns:
            A dictionary mapping the 1-indexed page number to its extracted raw text.
        """
        pages_text = {}
        
        # Open the PDF from the byte stream directly using the updated API
        with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text").strip()
                
                # Use 1-indexed mapping to align with standard human-readable page numbers
                pages_text[page_num + 1] = text
                
        return pages_text