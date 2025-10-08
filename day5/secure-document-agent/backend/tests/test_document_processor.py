import pytest
import asyncio
from app.services.document_processor import DocumentProcessor

class TestDocumentProcessor:
    @pytest.fixture
    def processor(self):
        return DocumentProcessor()
    
    @pytest.mark.asyncio
    async def test_text_chunking(self, processor):
        text = "This is a test document. " * 100
        chunks = processor._chunk_text(text, chunk_size=100, overlap=20)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 120 for chunk in chunks)  # chunk_size + overlap
    
    @pytest.mark.asyncio
    async def test_pdf_processing(self, processor):
        # Mock PDF content
        pdf_content = b"%PDF-1.4 test content"
        
        result = await processor.process(
            content=pdf_content,
            filename="test.pdf",
            content_type="application/pdf"
        )
        
        assert "text_content" in result
        assert "chunks" in result
        assert "content_classification" in result
