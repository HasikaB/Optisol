from serpapi import GoogleSearch
import os
import logging
from dotenv import load_dotenv  # <-- import this

# Load .env file
load_dotenv()  # <-- ensures environment variables are available in Python

class WebSearchService:
    def __init__(self):
        self.api_key = os.getenv('SERPAPI_API_KEY')
        self.logger = logging.getLogger(__name__)

    def search(self, query, count=5):
        """
        Search web using SerpAPI
        
        Args:
            query (str): Search query
            count (int): Number of results to return
            
        Returns:
            list: Parsed search results
        """
        try:
            if not self.api_key:
                self.logger.error("SerpAPI key not found")
                return self._get_fallback_results()
            
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": count,
                "engine": "google"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            return self._parse_results(results)
            
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return self._get_fallback_results()
    
    def _parse_results(self, results):
        """Parse SerpAPI results into consistent format"""
        parsed = []
        
        # Get organic results
        organic_results = results.get('organic_results', [])
        
        for result in organic_results:
            parsed.append({
                'title': result.get('title', ''),
                'description': result.get('snippet', ''),
                'url': result.get('link', ''),
                'source': result.get('displayed_link', '')
            })
        
        # Also check for answer box (featured snippet)
        answer_box = results.get('answer_box', {})
        if answer_box:
            parsed.insert(0, {
                'title': answer_box.get('title', 'Featured Answer'),
                'description': answer_box.get('answer', answer_box.get('snippet', '')),
                'url': answer_box.get('link', ''),
                'source': 'Featured Snippet'
            })
        
        return parsed
    
    def _get_fallback_results(self):
        """Return fallback results if API fails"""
        return [
            {
                'title': 'Sample Result 1',
                'description': 'This is a fallback result for demo purposes.',
                'url': 'https://example.com',
                'source': 'example.com'
            }
        ]
    
    def search_news(self, query, count=5):
        """
        Search for news articles
        
        Args:
            query (str): Search query
            count (int): Number of results
            
        Returns:
            list: News results
        """
        try:
            params = {
                "q": query,
                "api_key": self.api_key,
                "tbm": "nws",  # News search
                "num": count,
                "engine": "google"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            return self._parse_news_results(results)
            
        except Exception as e:
            self.logger.error(f"News search error: {e}")
            return []
    
    def _parse_news_results(self, results):
        """Parse news results"""
        parsed = []
        news_results = results.get('news_results', [])
        
        for result in news_results:
            parsed.append({
                'title': result.get('title', ''),
                'description': result.get('snippet', ''),
                'url': result.get('link', ''),
                'source': result.get('source', ''),
                'date': result.get('date', '')
            })
        
        return parsed


# Test function
if __name__ == "__main__":
    # Test the search service
    search_service = WebSearchService()
    results = search_service.search("renewable energy trends 2025", count=3)
    
    print("Search Results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   {result['description']}")
        print(f"   URL: {result['url']}")