import google.generativeai as genai
from typing import Dict, Any, List
import magic
import pypdf
from docx import Document
import pandas as pd
from PIL import Image
import io
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def process(self, content: bytes, filename: str, content_type: str) -> Dict[str, Any]:
        """Process document and extract text content"""
        try:
            # Detect file type
            file_type = magic.from_buffer(content, mime=True)
            
            # Extract text based on file type
            text_content = ""
            
            if file_type == "application/pdf":
                text_content = self._extract_pdf_text(content)
            elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                text_content = self._extract_docx_text(content)
            elif file_type == "text/plain":
                text_content = content.decode('utf-8')
            elif file_type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
                text_content = self._extract_excel_text(content)
            elif file_type.startswith("image/"):
                text_content = await self._extract_image_text(content)
            else:
                text_content = "Unsupported file type for text extraction"
            
            # Chunk text for processing
            chunks = self._chunk_text(text_content)
            
            # Classify content using Gemini
            content_classification = await self._classify_content(text_content[:2000])
            
            return {
                "text_content": text_content,
                "chunks": chunks,
                "file_type": file_type,
                "content_classification": content_classification,
                "chunk_count": len(chunks),
                "character_count": len(text_content)
            }
            
        except Exception as e:
            logger.error(f"Document processing error: {str(e)}")
            return {
                "text_content": "",
                "chunks": [],
                "file_type": "unknown",
                "content_classification": {"category": "unknown", "confidence": 0.0},
                "error": str(e)
            }
    
    def _extract_pdf_text(self, content: bytes) -> str:
        """Extract text from PDF"""
        try:
            pdf_file = io.BytesIO(content)
            reader = pypdf.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            return ""
    
    def _extract_docx_text(self, content: bytes) -> str:
        """Extract text from DOCX"""
        try:
            doc_file = io.BytesIO(content)
            doc = Document(doc_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"DOCX extraction error: {str(e)}")
            return ""
    
    def _extract_excel_text(self, content: bytes) -> str:
        """Extract text from Excel files"""
        try:
            excel_file = io.BytesIO(content)
            df = pd.read_excel(excel_file)
            return df.to_string()
        except Exception as e:
            logger.error(f"Excel extraction error: {str(e)}")
            return ""
    
    async def _extract_image_text(self, content: bytes) -> str:
        """Extract text from images using Gemini Vision"""
        try:
            # For now, return placeholder - would integrate with Gemini Vision API
            return "Image text extraction would be implemented with Gemini Vision"
        except Exception as e:
            logger.error(f"Image text extraction error: {str(e)}")
            return ""
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Chunk text with overlap for better context preservation"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Find sentence boundary near the end
            if end < len(text):
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            
        return chunks
    
    async def _classify_content(self, text_sample: str) -> Dict[str, Any]:
        """Classify document content using Gemini"""
        try:
            # Check if Gemini API key is available
            if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "demo-key-for-testing":
                # Return mock classification for testing
                return {
                    "category": "personal",
                    "confidence": 0.8,
                    "topics": ["test", "sample"],
                    "sensitivity": "low",
                    "description": "Test document classification"
                }
            
            prompt = f"""
            Analyze this document content and classify it into one of these categories:
            - financial (financial documents, invoices, receipts)
            - legal (contracts, agreements, legal documents)
            - medical (medical records, reports, prescriptions)
            - personal (personal letters, resumes, personal documents)
            - business (business reports, presentations, proposals)
            - technical (technical documentation, manuals, specifications)
            - academic (research papers, academic documents)
            - other (miscellaneous documents)
            
            Also provide a confidence score (0.0-1.0) and identify key topics.
            
            Document content:
            {text_sample}
            
            Respond in JSON format:
            {{
                "category": "category_name",
                "confidence": 0.95,
                "topics": ["topic1", "topic2"],
                "sensitivity": "low|medium|high",
                "description": "brief description"
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            import json
            try:
                classification = json.loads(response.text)
                return classification
            except json.JSONDecodeError:
                return {
                    "category": "unknown",
                    "confidence": 0.0,
                    "topics": [],
                    "sensitivity": "medium",
                    "description": "Classification failed"
                }
                
        except Exception as e:
            logger.error(f"Content classification error: {str(e)}")
            return {
                "category": "unknown", 
                "confidence": 0.0,
                "topics": [],
                "sensitivity": "medium",
                "error": str(e)
            }
