"""
Optimized Handler Dispatch System - Phase 5

Provides high-performance statement routing with:
    - Type-based caching for O(1) handler lookup
    - Execution profiling and statistics
    - Memory-efficient batch processing
    - Handler composition and middleware
    - Fallback chain management
"""

import time
from dataclasses import dataclass, field
from typing import Callable, Optional, Type, Any
import logging

from gulfofmexico.processor.syntax_tree import CodeStatement
from gulfofmexico.builtin import GulfOfMexicoValue

logger = logging.getLogger(__name__)


@dataclass
class HandlerMetrics:
    """Performance metrics for a single handler."""
    
    statement_type: str
    invocation_count: int = 0
    total_time_ms: float = 0.0
    error_count: int = 0
    avg_time_ms: float = field(init=False)
    success_rate: float = field(init=False)
    
    def __post_init__(self):
        """Calculate derived metrics."""
        self._update_derived()
    
    def _update_derived(self):
        """Update derived metrics."""
        if self.invocation_count > 0:
            self.avg_time_ms = self.total_time_ms / self.invocation_count
            self.success_rate = (self.invocation_count - self.error_count) / self.invocation_count
        else:
            self.avg_time_ms = 0.0
            self.success_rate = 1.0
    
    def record_execution(self, elapsed_ms: float, error: bool = False) -> None:
        """Record a handler execution.
        
        Args:
            elapsed_ms: Execution time in milliseconds
            error: Whether execution had an error
        """
        self.invocation_count += 1
        self.total_time_ms += elapsed_ms
        if error:
            self.error_count += 1
        self._update_derived()


@dataclass
class DispatcherStats:
    """Global dispatcher statistics."""
    
    total_statements: int = 0
    total_dispatch_time_ms: float = 0.0
    cached_lookups: int = 0
    cache_misses: int = 0
    handler_metrics: dict[str, HandlerMetrics] = field(default_factory=dict)
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total_lookups = self.cached_lookups + self.cache_misses
        if total_lookups == 0:
            return 0.0
        return self.cached_lookups / total_lookups
    
    @property
    def avg_dispatch_time_ms(self) -> float:
        """Calculate average dispatch time."""
        if self.total_statements == 0:
            return 0.0
        return self.total_dispatch_time_ms / self.total_statements


class HandlerDispatcher:
    """High-performance handler dispatch system.
    
    Features:
        - Type-based caching for O(1) lookup
        - Execution profiling
        - Middleware support
        - Fallback chain management
    """
    
    def __init__(self, enable_profiling: bool = False):
        """Initialize the dispatcher.
        
        Args:
            enable_profiling: Whether to collect performance metrics
        """
        self._handlers: dict[Type[CodeStatement], Any] = {}
        self._type_cache: dict[Type[CodeStatement], Any] = {}
        self._fallback_chain: list[Callable] = []
        self._middleware_chain: list[Callable] = []
        self._enable_profiling = enable_profiling
        self._stats = DispatcherStats()
    
    def register_handler(
        self,
        statement_type: Type[CodeStatement],
        handler: Any,
    ) -> None:
        """Register a handler for a statement type.
        
        Args:
            statement_type: The statement type to handle
            handler: The handler instance
        """
        self._handlers[statement_type] = handler
        self._type_cache.clear()  # Invalidate cache on registration
    
    def add_fallback(self, fallback: Callable) -> None:
        """Add a fallback handler to the chain.
        
        Args:
            fallback: Callable that handles unmatched statements
        """
        self._fallback_chain.append(fallback)
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to the dispatch chain.
        
        Middleware is called before handler execution and can:
        - Modify the context
        - Log execution
        - Implement retry logic
        
        Args:
            middleware: Callable that wraps handler execution
        """
        self._middleware_chain.append(middleware)
    
    def dispatch(
        self,
        statement: CodeStatement,
        context: Any,
    ) -> tuple[bool, Optional[GulfOfMexicoValue]]:
        """Dispatch a statement to the appropriate handler.
        
        Args:
            statement: The statement to execute
            context: Execution context
            
        Returns:
            (handled, result) tuple
        """
        start_time = time.perf_counter() if self._enable_profiling else 0
        stmt_type = type(statement)
        
        try:
            # Try cached lookup first
            handler = self._try_cache_lookup(stmt_type)
            if handler is None:
                handler = self._handlers.get(stmt_type)
                self._type_cache[stmt_type] = handler
                if self._enable_profiling:
                    self._stats.cache_misses += 1
            else:
                if self._enable_profiling:
                    self._stats.cached_lookups += 1
            
            # Execute handler if found
            if handler is not None:
                result = self._execute_with_middleware(handler, statement, context)
                if self._enable_profiling:
                    self._record_success(stmt_type, start_time)
                return (True, result)
            
            # Try fallback chain
            for fallback in self._fallback_chain:
                result = fallback(statement, context)
                if result is not None:
                    if self._enable_profiling:
                        self._record_success(stmt_type, start_time)
                    return (True, result)
            
            # No handler or fallback
            if self._enable_profiling:
                self._record_miss(stmt_type, start_time)
            return (False, None)
            
        except Exception as e:
            if self._enable_profiling:
                self._record_error(stmt_type, start_time)
            logger.error(f"Dispatch error for {stmt_type.__name__}: {e}")
            return (False, None)
    
    def _try_cache_lookup(self, stmt_type: Type[CodeStatement]) -> Optional[Any]:
        """Try to get handler from cache.
        
        Args:
            stmt_type: Statement type to look up
            
        Returns:
            Handler or None if not cached
        """
        return self._type_cache.get(stmt_type)
    
    def _execute_with_middleware(
        self,
        handler: Any,
        statement: CodeStatement,
        context: Any,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute handler with middleware chain.
        
        Args:
            handler: The handler to execute
            statement: The statement
            context: Execution context
            
        Returns:
            Handler result
        """
        if not self._middleware_chain:
            return handler.execute(statement, context)
        
        def next_middleware(mw_index: int = 0) -> Optional[GulfOfMexicoValue]:
            if mw_index >= len(self._middleware_chain):
                return handler.execute(statement, context)
            
            middleware = self._middleware_chain[mw_index]
            return middleware(statement, context, lambda: next_middleware(mw_index + 1))
        
        return next_middleware()
    
    def _record_success(self, stmt_type: Type[CodeStatement], start_time: float) -> None:
        """Record successful handler execution.
        
        Args:
            stmt_type: Statement type
            start_time: Execution start time
        """
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        type_name = stmt_type.__name__
        
        if type_name not in self._stats.handler_metrics:
            self._stats.handler_metrics[type_name] = HandlerMetrics(type_name)
        
        self._stats.handler_metrics[type_name].record_execution(elapsed_ms, error=False)
        self._stats.total_statements += 1
        self._stats.total_dispatch_time_ms += elapsed_ms
    
    def _record_error(self, stmt_type: Type[CodeStatement], start_time: float) -> None:
        """Record handler execution error.
        
        Args:
            stmt_type: Statement type
            start_time: Execution start time
        """
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        type_name = stmt_type.__name__
        
        if type_name not in self._stats.handler_metrics:
            self._stats.handler_metrics[type_name] = HandlerMetrics(type_name)
        
        self._stats.handler_metrics[type_name].record_execution(elapsed_ms, error=True)
        self._stats.total_statements += 1
        self._stats.total_dispatch_time_ms += elapsed_ms
    
    def _record_miss(self, stmt_type: Type[CodeStatement], start_time: float) -> None:
        """Record unhandled statement.
        
        Args:
            stmt_type: Statement type
            start_time: Execution start time
        """
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        self._stats.total_statements += 1
        self._stats.total_dispatch_time_ms += elapsed_ms
    
    def get_stats(self) -> DispatcherStats:
        """Get current dispatcher statistics.
        
        Returns:
            DispatcherStats object
        """
        return self._stats
    
    def reset_stats(self) -> None:
        """Reset statistics."""
        self._stats = DispatcherStats()
        self._type_cache.clear()


class BatchDispatcher:
    """Batch dispatch processor for multiple statements.
    
    Useful for processing multiple statements with overhead reduction.
    """
    
    def __init__(self, dispatcher: HandlerDispatcher):
        """Initialize batch dispatcher.
        
        Args:
            dispatcher: The dispatcher to use
        """
        self._dispatcher = dispatcher
    
    def dispatch_batch(
        self,
        statements: list[CodeStatement],
        context: Any,
    ) -> list[tuple[bool, Optional[GulfOfMexicoValue]]]:
        """Dispatch multiple statements.
        
        Args:
            statements: List of statements to dispatch
            context: Execution context
            
        Returns:
            List of (handled, result) tuples
        """
        results = []
        for statement in statements:
            handled, result = self._dispatcher.dispatch(statement, context)
            results.append((handled, result))
        return results
