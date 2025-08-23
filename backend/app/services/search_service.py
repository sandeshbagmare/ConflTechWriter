"""
Search service using DuckDuckGo and BeautifulSoup for web scraping.
This service is designed to be free and not require API keys.
"""

import asyncio
import aiohttp
from typing import List, Dict, Optional, Set
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class FreeSearchService:
    """
    A free search service that uses DuckDuckGo for search and BeautifulSoup
    for scraping content from the resulting URLs.
    """

    def __init__(self, max_results: int = 10, request_timeout: int = 15):
        self.max_results = max_results
        self.request_timeout = request_timeout
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Initializes the aiohttp session."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.request_timeout),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the aiohttp session."""
        if self.session:
            await self.session.close()

    async def search_web(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Performs a web search using DuckDuckGo.

        Args:
            query: The search query string.
            max_results: The maximum number of search results to return.

        Returns:
            A list of dictionaries, each representing a search result.
        """
        results = []
        num_results = max_results or self.max_results
        logger.info(f"Performing DDG search for '{query}' with max_results={num_results}")
        try:
            with DDGS() as ddgs:
                # The DDGS library returns a generator, so we convert it to a list
                ddgs_results = list(ddgs.text(keywords=query, max_results=num_results))
                for r in ddgs_results:
                    results.append({
                        'title': r.get('title', ''),
                        'url': r.get('href', ''),
                        'snippet': r.get('body', ''),
                        'source': 'duckduckgo'
                    })
            logger.info(f"DDG search for '{query}' returned {len(results)} results.")
        except Exception as e:
            logger.error(f"DuckDuckGo search failed for query '{query}': {e}", exc_info=True)
        return results

    async def _fetch_and_parse(self, url: str) -> Optional[str]:
        """Fetches a URL and parses its main text content."""
        if not self.session or self.session.closed:
            logger.error("Attempted to fetch URL with no active session.")
            return None
        try:
            async with self.session.get(url, allow_redirects=True, timeout=self.request_timeout) as response:
                response.raise_for_status()
                if 'text/html' not in response.headers.get('Content-Type', ''):
                    logger.debug(f"Skipping non-HTML content at {url}")
                    return None
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml') # 'lxml' is generally faster

                # Remove non-content tags
                for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form']):
                    tag.decompose()

                # A more robust way to get text, trying common content containers
                main_content_selectors = ['article', 'main', '.main', '#main', '.post-body', '.entry-content']
                content_element = None
                for selector in main_content_selectors:
                    content_element = soup.select_one(selector)
                    if content_element:
                        break
                
                if not content_element:
                    content_element = soup.body

                if content_element:
                    text = content_element.get_text(separator=' ', strip=True)
                    # Clean up whitespace
                    text = re.sub(r'\s\s+', ' ', text)
                    return text
                return None
        except asyncio.TimeoutError:
            logger.warning(f"Timeout while fetching content from {url}")
            return None
        except aiohttp.ClientError as e:
            logger.warning(f"HTTP error fetching content from {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error extracting content from {url}: {e}", exc_info=True)
            return None

    async def search_and_extract(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Searches the web and then extracts the main content from the top results.

        Args:
            query: The search query.
            max_results: The maximum number of results to process.

        Returns:
            A list of search result dictionaries, enhanced with a 'content' key.
        """
        search_results = await self.search_web(query, max_results)
        
        # Use a set to avoid fetching the same URL multiple times if DDG returns duplicates
        unique_urls: Set[str] = {r['url'] for r in search_results if r.get('url')}
        
        tasks = {url: asyncio.create_task(self._fetch_and_parse(url)) for url in unique_urls}
        
        url_to_content: Dict[str, Optional[str]] = {}
        for url, task in tasks.items():
            try:
                url_to_content[url] = await task
            except Exception as e:
                logger.warning(f"Task for fetching {url} failed: {e}")
                url_to_content[url] = None

        enhanced_results = []
        for result in search_results:
            url = result.get('url')
            if url in url_to_content:
                content = url_to_content[url]
                if content:
                    result['content'] = content
                enhanced_results.append(result)
        
        logger.info(f"Extracted content from {len([r for r in enhanced_results if 'content' in r])} of {len(search_results)} search results for query '{query}'.")
        return enhanced_results

# Example usage function
async def search_example():
    """Example of how to use the search service."""
    logging.basicConfig(level=logging.INFO)
    async with FreeSearchService() as search:
        query = "impact of reinforcement learning on robotics"
        logger.info(f"--- Running search_and_extract for '{query}' ---")
        enhanced_results = await search.search_and_extract(query, max_results=5)
        
        for i, result in enumerate(enhanced_results):
            print(f"\n--- Result {i+1} ---")
            print(f"Title: {result.get('title')}")
            print(f"URL: {result.get('url')}")
            content_preview = result.get('content', 'N/A')[:200]
            print(f"Content Preview: {content_preview}...")
            print(f"Content Length: {len(result.get('content', ''))}")

if __name__ == "__main__":
    asyncio.run(search_example())
