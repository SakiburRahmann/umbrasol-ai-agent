import hashlib
from core.omega_memory import OmegaMemory

class SemanticCache:
    def __init__(self, memory=None):
        self.memory = memory or OmegaMemory()

    def _hash(self, text):
        return hashlib.md5(text.lower().strip().encode()).hexdigest()

    async def get(self, user_request):
        """Returns the command if it exists in cache."""
        req_hash = self._hash(user_request)
        return await self.memory.get_cache(req_hash)

    async def set(self, user_request, tool, command):
        """Stores a successful command mapping."""
        req_hash = self._hash(user_request)
        await self.memory.set_cache(req_hash, tool, command)
