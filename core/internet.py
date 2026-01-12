import requests
import json
import os
import time

class Internet:
    def __init__(self, cache_dir="memory/cache"):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "web_cache.json")
        self.cache_expiry = 3600  # 1 hour
        
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
        if not os.path.exists(self.cache_file):
            with open(self.cache_file, 'w') as f:
                json.dump({}, f)

    def is_connected(self):
        """Check if internet is available."""
        try:
            requests.get("https://8.8.8.8", timeout=2)
            return True
        except:
            return False

    def swift_search(self, query):
        """
        Performs a cached search. 
        In production, this would use a real Search API.
        For Phase 1.5, we will simulate the return or use a lightweight scraper.
        """
        # 1. Check Cache
        with open(self.cache_file, 'r') as f:
            cache = json.load(f)
            
        if query in cache:
            entry = cache[query]
            if time.time() - entry["timestamp"] < self.cache_expiry:
                return f"CACHE_HIT: {entry['data']}"

        # 2. Check Connection
        if not self.is_connected():
            return "ERROR_OFFLINE: No internet access available."

        # 3. Simulate/Perform Search (Placeholder for real integration)
        # Note: In the final version, this will call a search tool.
        search_result = f"Latest information found for: {query}. (Simulated Result)"
        
        # 4. Save to Cache
        cache[query] = {
            "timestamp": time.time(),
            "data": search_result
        }
        with open(self.cache_file, 'w') as f:
            json.dump(cache, f, indent=4)
            
        return search_result

if __name__ == "__main__":
    net = Internet()
    print("Online:", net.is_connected())
    print("Search Result:", net.swift_search("How to organize files using Python"))
