from duckduckgo_search import DDGS
import json
import os
import time
import requests

class Internet:
    def __init__(self, cache_dir="memory/cache"):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "web_cache.json")
        self.cache_expiry = 14400  # 4 hours
        
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
        if not os.path.exists(self.cache_file):
            with open(self.cache_file, 'w') as f:
                json.dump({}, f)

    def is_connected(self):
        """Check if internet is available."""
        try:
            requests.get("https://1.1.1.1", timeout=2)
            return True
        except:
            return False

    def swift_search(self, query):
        """
        Performs a real, privacy-focused search via DuckDuckGo.
        Results are cached to minimize network overhead.
        """
        # 1. Check Cache
        try:
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
        except: cache = {}
            
        if query in cache:
            entry = cache[query]
            if time.time() - entry["timestamp"] < self.cache_expiry:
                return entry["data"]

        # 2. Check Connection
        if not self.is_connected():
            return "ERROR: Offline. Cannot reach search engine."

        # 3. Perform Search
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                if not results:
                    return "No relevant results found for this query."
                
                # Format summary
                summary = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
                
                # Save to Cache
                cache[query] = {
                    "timestamp": time.time(),
                    "data": summary
                }
                with open(self.cache_file, 'w') as f:
                    json.dump(cache, f, indent=4)
                    
                return summary
        except Exception as e:
            return f"ERROR: Search failed: {str(e)}"

if __name__ == "__main__":
    net = Internet()
    print("Online:", net.is_connected())
    print("Search Result:", net.swift_search("Who is the current Prime Minister of United Kingdom?"))
