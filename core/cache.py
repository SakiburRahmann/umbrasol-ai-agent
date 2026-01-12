import json
import os
import hashlib

class SemanticCache:
    def __init__(self, cache_file="memory/nexus_cache.json"):
        self.cache_file = cache_file
        if not os.path.exists(os.path.dirname(cache_file)):
            os.makedirs(os.path.dirname(cache_file))
        if not os.path.exists(cache_file):
            with open(cache_file, 'w') as f:
                json.dump({}, f)

    def _hash(self, text):
        return hashlib.md5(text.lower().strip().encode()).hexdigest()

    def get(self, user_request):
        """Returns the command if it exists in cache."""
        with open(self.cache_file, 'r') as f:
            cache = json.load(f)
        return cache.get(self._hash(user_request))

    def set(self, user_request, tool, command):
        """Stores a successful command mapping."""
        with open(self.cache_file, 'r') as f:
            cache = json.load(f)
        cache[self._hash(user_request)] = {"tool": tool, "command": command}
        with open(self.cache_file, 'w') as f:
            json.dump(cache, f, indent=4)
