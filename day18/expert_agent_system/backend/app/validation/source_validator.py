import asyncio
import aiohttp
import time
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import structlog
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = structlog.get_logger()

class SourceValidator:
    def __init__(self):
        self.trusted_domains = {
            'wikipedia.org': 0.7,
            'scholar.google.com': 0.9,
            'ncbi.nlm.nih.gov': 0.95,
            'who.int': 0.95,
            'cdc.gov': 0.95,
            'nature.com': 0.9,
            'ieee.org': 0.9,
            'stackoverflow.com': 0.8,
            'github.com': 0.8,
            'docs.python.org': 0.9,
            'developer.mozilla.org': 0.85
        }
    
    async def validate_source(self, source: str, query: str) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            if not source or not isinstance(source, str):
                return self._create_validation_result(0.0, "Invalid source format", start_time)
            
            if source.startswith('http'):
                return await self._validate_url_source(source, query, start_time)
            else:
                return await self._validate_text_source(source, query, start_time)
                
        except Exception as e:
            logger.error("Source validation error", source=source, error=str(e))
            return self._create_validation_result(0.0, f"Validation error: {str(e)}", start_time)
    
    async def _validate_url_source(self, url: str, query: str, start_time: float) -> Dict[str, Any]:
        try:
            parsed_url = urlparse(url)
            domain_confidence = self._get_domain_confidence(parsed_url.netloc)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        content_relevance = await self._assess_content_relevance(content, query)
                        
                        final_confidence = (domain_confidence + content_relevance) / 2
                        
                        return self._create_validation_result(
                            final_confidence,
                            f"URL validated: domain trust {domain_confidence:.2f}, relevance {content_relevance:.2f}",
                            start_time
                        )
                    else:
                        return self._create_validation_result(
                            0.2,
                            f"URL returned status {response.status}",
                            start_time
                        )
                        
        except asyncio.TimeoutError:
            return self._create_validation_result(0.1, "URL validation timeout", start_time)
        except Exception as e:
            return self._create_validation_result(0.0, f"URL validation error: {str(e)}", start_time)
    
    async def _validate_text_source(self, source: str, query: str, start_time: float) -> Dict[str, Any]:
        # For text sources, assess based on content quality indicators
        quality_score = 0.5  # Base score for text sources
        
        # Check for academic indicators
        academic_indicators = ['doi:', 'published', 'journal', 'research', 'study', 'analysis']
        for indicator in academic_indicators:
            if indicator.lower() in source.lower():
                quality_score += 0.1
        
        # Check for citation format
        if any(marker in source for marker in ['(', ')', '[', ']', 'et al.', 'pp.']):
            quality_score += 0.15
        
        quality_score = min(quality_score, 1.0)
        
        return self._create_validation_result(
            quality_score,
            f"Text source validated with quality indicators",
            start_time
        )
    
    def _get_domain_confidence(self, domain: str) -> float:
        for trusted_domain, confidence in self.trusted_domains.items():
            if trusted_domain in domain.lower():
                return confidence
        
        # Default confidence for unknown domains
        if any(tld in domain for tld in ['.edu', '.gov', '.org']):
            return 0.6
        elif any(tld in domain for tld in ['.com', '.net']):
            return 0.4
        else:
            return 0.2
    
    async def _assess_content_relevance(self, content: str, query: str) -> float:
        try:
            soup = BeautifulSoup(content, 'html.parser')
            text_content = soup.get_text()[:2000]  # First 2000 chars
            
            query_words = set(query.lower().split())
            content_words = set(text_content.lower().split())
            
            if not query_words:
                return 0.0
            
            overlap = len(query_words.intersection(content_words))
            relevance = overlap / len(query_words)
            
            return min(relevance, 1.0)
            
        except Exception:
            return 0.3  # Default relevance if parsing fails
    
    def _create_validation_result(self, confidence: float, reason: str, start_time: float) -> Dict[str, Any]:
        return {
            "confidence": confidence,
            "reason": reason,
            "validation_time": time.time() - start_time,
            "timestamp": time.time()
        }
