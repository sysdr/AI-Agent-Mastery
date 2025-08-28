import asyncio
import aiohttp
import time
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import re
import logging
from ..core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from ..core.rate_limiter import DistributedRateLimiter

logger = logging.getLogger(__name__)

class PriceScraper:
    def __init__(self, rate_limiter: DistributedRateLimiter):
        self.rate_limiter = rate_limiter
        self.circuit_breakers = {}
        self.selectors = {
            "amazon.com": {
                "price": [".a-price-whole", ".a-offscreen", ".a-price"],
                "title": ["#productTitle", "h1"]
            },
            "ebay.com": {
                "price": [".u-flL.condense", ".notranslate"],
                "title": [".x-item-title-label", "h1"]
            },
            "default": {
                "price": [".price", ".cost", ".amount", "[data-price]"],
                "title": ["h1", ".title", ".product-title"]
            }
        }
    
    def _get_circuit_breaker(self, domain: str) -> CircuitBreaker:
        """Get or create circuit breaker for domain"""
        if domain not in self.circuit_breakers:
            config = CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=300,  # 5 minutes
                expected_exception=Exception
            )
            self.circuit_breakers[domain] = CircuitBreaker(config)
        return self.circuit_breakers[domain]
    
    async def scrape_price(self, url: str, max_retries: int = 3) -> Dict:
        """Scrape price with resilience patterns"""
        domain = self._extract_domain(url)
        circuit_breaker = self._get_circuit_breaker(domain)
        
        # Check rate limit
        allowed, rate_info = await self.rate_limiter.check_rate_limit(
            f"scraper:{domain}", 10, 60  # 10 requests per minute per domain
        )
        
        if not allowed:
            return {
                "success": False,
                "error": "Rate limit exceeded",
                "retry_after": rate_info.get("retry_after")
            }
        
        try:
            result = await circuit_breaker.call(self._scrape_with_retries, url, max_retries)
            return {
                "success": True,
                "data": result,
                "circuit_breaker_stats": circuit_breaker.get_stats()
            }
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "circuit_breaker_stats": circuit_breaker.get_stats()
            }
    
    async def _scrape_with_retries(self, url: str, max_retries: int) -> Dict:
        """Scrape with exponential backoff"""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return await self._scrape_single(url)
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    await asyncio.sleep(wait_time)
                    logger.warning(f"Scraping attempt {attempt + 1} failed, retrying in {wait_time}s")
        
        raise last_exception
    
    async def _scrape_single(self, url: str) -> Dict:
        """Single scraping attempt"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                content = await response.text()
                return self._parse_content(content, url)
    
    def _parse_content(self, content: str, url: str) -> Dict:
        """Parse HTML content to extract price and title"""
        soup = BeautifulSoup(content, 'html.parser')
        domain = self._extract_domain(url)
        
        selectors = self.selectors.get(domain, self.selectors["default"])
        
        # Extract title
        title = None
        for selector in selectors["title"]:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                break
        
        # Extract price
        price = None
        price_text = None
        for selector in selectors["price"]:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                price = self._extract_price_value(price_text)
                if price:
                    break
        
        return {
            "title": title,
            "price": price,
            "price_text": price_text,
            "url": url,
            "scraped_at": time.time()
        }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc.lower()
    
    def _extract_price_value(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text"""
        if not price_text:
            return None
        
        # Remove currency symbols and extract numbers
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        if price_match:
            try:
                return float(price_match.group())
            except ValueError:
                pass
        return None
