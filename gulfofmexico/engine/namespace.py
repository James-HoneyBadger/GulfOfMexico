"""Optimized namespace management with caching.

This module provides the NamespaceManager class for efficient variable
lookups with caching and invalidation.
"""

from typing import Optional, Union
from gulfofmexico.builtin import Variable, Name
from gulfofmexico.constants import NAMESPACE_CACHE_SIZE


class NamespaceManager:
    """Manages variable namespaces with caching for performance.

    Provides optimized lookup of variables across the namespace stack
    with LRU caching to avoid repeated linear searches.
    """

    def __init__(self, namespaces: list[dict], enable_cache: bool = True):
        """Initialize the namespace manager.

        Args:
            namespaces: Stack of namespace dictionaries
            enable_cache: Whether to enable namespace caching
        """
        self.namespaces = namespaces
        self.enable_cache = enable_cache
        self._cache: dict[str, tuple[int, Union[Variable, Name]]] = {}
        self._cache_hits = 0
        self._cache_misses = 0

    def lookup(
        self, name: str
    ) -> tuple[Optional[Union[Variable, Name]], Optional[dict]]:
        """Find a variable in the namespace stack.

        Args:
            name: Variable name to find

        Returns:
            Tuple of (Variable/Name if found, namespace dict if found)
        """
        # Check cache if enabled
        if self.enable_cache and name in self._cache:
            scope_idx, var = self._cache[name]

            # Validate cache entry
            if (
                scope_idx < len(self.namespaces)
                and self.namespaces[scope_idx].get(name) is var
            ):
                self._cache_hits += 1
                return var, self.namespaces[scope_idx]

            # Cache invalidated - remove entry
            del self._cache[name]

        self._cache_misses += 1

        # Perform lookup
        for idx, namespace in enumerate(reversed(self.namespaces)):
            if name in namespace:
                var = namespace[name]

                # Update cache if enabled
                if self.enable_cache and len(self._cache) < NAMESPACE_CACHE_SIZE:
                    actual_idx = len(self.namespaces) - idx - 1
                    self._cache[name] = (actual_idx, var)

                return var, namespace

        return None, None

    def invalidate(self, name: str) -> None:
        """Invalidate cache entry for a variable.

        Args:
            name: Variable name to invalidate
        """
        self._cache.pop(name, None)

    def invalidate_all(self) -> None:
        """Clear the entire namespace cache."""
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0

    def get_stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total * 100 if total > 0 else 0

        return {
            "cache_size": len(self._cache),
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": hit_rate,
        }
