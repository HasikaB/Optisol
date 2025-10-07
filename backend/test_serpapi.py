from dotenv import load_dotenv
import os
from serpapi import GoogleSearch

load_dotenv()

def test_serpapi():
    api_key = os.getenv('SERPAPI_API_KEY')
    
    if not api_key:
        print("❌ Error: SERPAPI_API_KEY not found in .env file")
        return
    
    print("✅ API Key found")
    print(f"🔍 Testing search with query: 'artificial intelligence 2025'")
    
    try:
        params = {
            "q": "artificial intelligence 2025",
            "api_key": api_key,
            "num": 3,
            "engine": "google"
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        print("\n📊 Search Results:")
        print("-" * 60)
        
        if 'organic_results' in results:
            for i, result in enumerate(results['organic_results'][:3], 1):
                print(f"\n{i}. {result.get('title')}")
                print(f"   {result.get('snippet')}")
                print(f"   URL: {result.get('link')}")
        
        # Check answer box
        if 'answer_box' in results:
            print("\n🎯 Featured Answer:")
            print(results['answer_box'].get('answer', 'N/A'))
        
        print("\n✅ SerpAPI is working correctly!")
        
        # Check remaining credits
        if 'search_metadata' in results:
            print(f"\n📈 Search ID: {results['search_metadata'].get('id')}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPossible issues:")
        print("1. Invalid API key")
        print("2. No credits remaining")
        print("3. Network connection issue")

if __name__ == "__main__":
    test_serpapi()