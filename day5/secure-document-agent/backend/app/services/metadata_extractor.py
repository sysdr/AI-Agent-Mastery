import google.generativeai as genai
from typing import Dict, Any
import magic
import hashlib
from datetime import datetime
import os
from PIL import Image
import io
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

class MetadataExtractor:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def extract(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from document"""
        try:
            # Basic file metadata
            file_hash = hashlib.sha256(content).hexdigest()
            file_type = magic.from_buffer(content, mime=True)
            file_size = len(content)
            
            # File extension and validation
            file_ext = os.path.splitext(filename)[1].lower()
            
            metadata = {
                "filename": filename,
                "file_hash": file_hash,
                "file_size": file_size,
                "content_type": file_type,
                "file_extension": file_ext,
                "extracted_at": datetime.utcnow().isoformat(),
                "version": "1.0"
            }
            
            # Type-specific metadata extraction
            if file_type == "application/pdf":
                pdf_metadata = await self._extract_pdf_metadata(content)
                metadata.update(pdf_metadata)
            elif file_type.startswith("image/"):
                image_metadata = await self._extract_image_metadata(content)
                metadata.update(image_metadata)
            elif "office" in file_type or "document" in file_type:
                office_metadata = await self._extract_office_metadata(content)
                metadata.update(office_metadata)
            
            # AI-powered content analysis
            content_analysis = await self._analyze_content_metadata(content, file_type)
            metadata.update(content_analysis)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction error: {str(e)}")
            return {
                "filename": filename,
                "error": str(e),
                "extracted_at": datetime.utcnow().isoformat()
            }
    
    async def _extract_pdf_metadata(self, content: bytes) -> Dict[str, Any]:
        """Extract PDF-specific metadata"""
        try:
            import pypdf
            pdf_file = io.BytesIO(content)
            reader = pypdf.PdfReader(pdf_file)
            
            return {
                "page_count": len(reader.pages),
                "pdf_version": getattr(reader, 'pdf_header', 'unknown'),
                "encrypted": reader.is_encrypted,
                "metadata_pdf": dict(reader.metadata) if reader.metadata else {}
            }
        except Exception as e:
            logger.error(f"PDF metadata extraction error: {str(e)}")
            return {"pdf_error": str(e)}
    
    async def _extract_image_metadata(self, content: bytes) -> Dict[str, Any]:
        """Extract image-specific metadata"""
        try:
            image = Image.open(io.BytesIO(content))
            
            metadata = {
                "image_width": image.width,
                "image_height": image.height,
                "image_mode": image.mode,
                "image_format": image.format
            }
            
            # EXIF data if available
            if hasattr(image, '_getexif') and image._getexif():
                exif_data = image._getexif()
                metadata["exif_data"] = {str(k): str(v) for k, v in exif_data.items()}
            
            return metadata
        except Exception as e:
            logger.error(f"Image metadata extraction error: {str(e)}")
            return {"image_error": str(e)}
    
    async def _extract_office_metadata(self, content: bytes) -> Dict[str, Any]:
        """Extract Office document metadata"""
        try:
            from docx import Document
            doc_file = io.BytesIO(content)
            doc = Document(doc_file)
            
            core_props = doc.core_properties
            
            return {
                "author": core_props.author,
                "title": core_props.title,
                "subject": core_props.subject,
                "created": core_props.created.isoformat() if core_props.created else None,
                "modified": core_props.modified.isoformat() if core_props.modified else None,
                "word_count": len(doc.paragraphs)
            }
        except Exception as e:
            logger.error(f"Office metadata extraction error: {str(e)}")
            return {"office_error": str(e)}
    
    async def _analyze_content_metadata(self, content: bytes, file_type: str) -> Dict[str, Any]:
        """Use AI to analyze content and extract semantic metadata"""
        try:
            # For text-based files, analyze content
            if file_type in ["text/plain", "application/pdf"] or "document" in file_type:
                # Extract sample text for analysis
                sample_text = ""
                if file_type == "text/plain":
                    sample_text = content.decode('utf-8', errors='ignore')[:2000]
                
                if sample_text:
                    analysis = await self._ai_content_analysis(sample_text)
                    return {"content_analysis": analysis}
            
            return {"content_analysis": "Not applicable for this file type"}
            
        except Exception as e:
            logger.error(f"Content analysis error: {str(e)}")
            return {"analysis_error": str(e)}
    
    async def _ai_content_analysis(self, text_sample: str) -> Dict[str, Any]:
        """Analyze content using Gemini for semantic metadata"""
        try:
            prompt = f"""
            Analyze this document content and extract metadata:
            
            1. Language detection
            2. Reading difficulty level (1-10)
            3. Key topics/themes (max 5)
            4. Document purpose/intent
            5. Target audience
            6. Estimated reading time (minutes)
            
            Document sample:
            {text_sample}
            
            Respond in JSON format:
            {{
                "language": "english",
                "reading_level": 7,
                "topics": ["topic1", "topic2"],
                "purpose": "document purpose",
                "audience": "target audience",
                "reading_time_minutes": 5
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            import json
            try:
                analysis = json.loads(response.text)
                return analysis
            except json.JSONDecodeError:
                return {"analysis": "Failed to parse AI response"}
                
        except Exception as e:
            logger.error(f"AI content analysis error: {str(e)}")
            return {"ai_error": str(e)}
