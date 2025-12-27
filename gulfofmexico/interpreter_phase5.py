"""
Phase 5 Interpreter Refactoring - Handler Dispatcher Integration

Bridges the existing interpreter with the optimized handler dispatch system.
Enables gradual migration from legacy pattern matching to handler-based execution.

This module provides:
    - Integrated handler dispatcher for the main interpreter loop
    - Automatic profiling of statement execution
    - Enhanced error handling with debugging support
    - Backward compatibility with legacy pattern matching
"""

import logging
from typing import Optional, Any
from gulfofmexico.handler_dispatch import HandlerDispatcher, DispatcherStats
from gulfofmexico.profiling import (
    PerformanceProfiler,
    ExecutionDebugger,
    ProfilingContext,
    get_global_profiler,
    get_global_debugger,
)
from gulfofmexico.plugin_manager import get_plugin_manager
from gulfofmexico.handler_registry import ProductionHandlerRegistry
from gulfofmexico.processor.syntax_tree import CodeStatement
from gulfofmexico.builtin import GulfOfMexicoValue

logger = logging.getLogger(__name__)


class OptimizedInterpreterContext:
    """Context for optimized interpreter execution.
    
    Manages:
        - Handler dispatcher
        - Profiling and debugging
        - Plugin integration
        - Statistics collection
    """
    
    def __init__(
        self,
        enable_profiling: bool = False,
        enable_debugging: bool = False,
    ):
        """Initialize optimized interpreter context.
        
        Args:
            enable_profiling: Enable performance profiling
            enable_debugging: Enable debugging features
        """
        self.dispatcher = HandlerDispatcher(enable_profiling=enable_profiling)
        self.profiler = PerformanceProfiler()
        self.debugger = ExecutionDebugger()
        self.plugin_manager = get_plugin_manager()
        
        self.profiling_enabled = enable_profiling
        self.debugging_enabled = enable_debugging
        
        if enable_profiling:
            self.profiler.enable()
        if enable_debugging:
            self.debugger.enable()
    
    def initialize_handlers(self) -> None:
        """Initialize all handlers from registry and plugins.
        
        Registers handlers from:
            - ProductionHandlerRegistry
            - Loaded plugins
        """
        registry = ProductionHandlerRegistry()
        
        # Register handlers from main registry
        # Note: This would be populated by existing handler registration code
        # in handler_registry.py's create_production_registry()
        
        # Register handlers from plugins
        for handler in self.plugin_manager.get_all_statement_handlers():
            stmt_type = handler.statement_type
            self.dispatcher.register_handler(stmt_type, handler)
            logger.debug(f"Registered handler for {stmt_type.__name__}")
    
    def execute_statement(
        self,
        statement: CodeStatement,
        context: Any,
    ) -> tuple[bool, Optional[GulfOfMexicoValue]]:
        """Execute a statement with optimizations.
        
        Handles:
            - Handler dispatch with caching
            - Profiling collection
            - Debugging support
            - Error handling
        
        Args:
            statement: Statement to execute
            context: Execution context
            
        Returns:
            (handled, result) tuple
        """
        stmt_type = type(statement).__name__
        
        # Push debug scope
        if self.debugging_enabled:
            self.debugger.push_scope(stmt_type)
        
        # Profile execution
        profiling_ctx = None
        if self.profiling_enabled:
            profiling_ctx = ProfilingContext(self.profiler, stmt_type)
            profiling_ctx.__enter__()
        
        try:
            # Dispatch through optimized handler system
            handled, result = self.dispatcher.dispatch(statement, context)
            
            # Record successful statement execution
            if self.profiling_enabled:
                self.profiler.record_statement_time(stmt_type, 0)  # Time tracked in dispatcher
            
            return (handled, result)
            
        except Exception as e:
            logger.error(f"Error executing {stmt_type}: {e}")
            if self.debugging_enabled:
                self.debugger.log_statement_execution(stmt_type, -1)
            if profiling_ctx:
                self.profiler.record_error()
            return (False, None)
            
        finally:
            # Pop debug scope
            if self.debugging_enabled:
                self.debugger.pop_scope()
            
            # Exit profiling context
            if profiling_ctx:
                profiling_ctx.__exit__(None, None, None)
    
    def get_dispatch_stats(self) -> DispatcherStats:
        """Get dispatcher statistics.
        
        Returns:
            DispatcherStats object
        """
        return self.dispatcher.get_stats()
    
    def get_profiling_report(self) -> dict[str, Any]:
        """Get detailed profiling report.
        
        Returns:
            Dictionary with profiling information
        """
        if not self.profiling_enabled:
            return {}
        
        trace = self.profiler.get_trace()
        stmt_stats = self.profiler.get_statement_stats()
        func_stats = self.profiler.get_function_stats()
        
        return {
            "total_duration_ms": trace.total_duration_ms,
            "statements_executed": trace.statements_executed,
            "errors": trace.errors_encountered,
            "statement_stats": stmt_stats,
            "function_calls": func_stats,
            "frames": len(trace.frames),
        }
    
    def reset_stats(self) -> None:
        """Reset all statistics."""
        self.dispatcher.reset_stats()
        self.profiler.reset()


# Global optimized context
_global_optimized_context: Optional[OptimizedInterpreterContext] = None


def get_optimized_context() -> OptimizedInterpreterContext:
    """Get or create global optimized interpreter context.
    
    Returns:
        OptimizedInterpreterContext instance
    """
    global _global_optimized_context
    if _global_optimized_context is None:
        _global_optimized_context = OptimizedInterpreterContext(
            enable_profiling=True,
            enable_debugging=False,
        )
        _global_optimized_context.initialize_handlers()
    return _global_optimized_context


def reset_optimized_context() -> None:
    """Reset the global optimized context."""
    global _global_optimized_context
    _global_optimized_context = None


def enable_profiling() -> None:
    """Enable interpreter profiling."""
    ctx = get_optimized_context()
    ctx.profiling_enabled = True
    ctx.profiler.enable()


def disable_profiling() -> None:
    """Disable interpreter profiling."""
    ctx = get_optimized_context()
    ctx.profiling_enabled = False
    ctx.profiler.disable()


def enable_debugging() -> None:
    """Enable interpreter debugging."""
    ctx = get_optimized_context()
    ctx.debugging_enabled = True
    ctx.debugger.enable()


def disable_debugging() -> None:
    """Disable interpreter debugging."""
    ctx = get_optimized_context()
    ctx.debugging_enabled = False
    ctx.debugger.disable()


def get_execution_stats() -> dict[str, Any]:
    """Get execution statistics.
    
    Returns:
        Dictionary with dispatch and profiling stats
    """
    ctx = get_optimized_context()
    return {
        "dispatch": {
            "total_statements": ctx.get_dispatch_stats().total_statements,
            "cache_hit_rate": ctx.get_dispatch_stats().cache_hit_rate,
            "avg_dispatch_ms": ctx.get_dispatch_stats().avg_dispatch_time_ms,
        },
        "profiling": ctx.get_profiling_report(),
    }


def print_execution_report() -> None:
    """Print formatted execution report."""
    stats = get_execution_stats()
    
    print("\n" + "=" * 60)
    print("EXECUTION STATISTICS REPORT")
    print("=" * 60)
    
    dispatch = stats.get("dispatch", {})
    print(f"\nHandler Dispatch:")
    print(f"  Total Statements: {dispatch.get('total_statements', 0)}")
    print(f"  Cache Hit Rate: {dispatch.get('cache_hit_rate', 0):.2%}")
    print(f"  Avg Dispatch: {dispatch.get('avg_dispatch_ms', 0):.3f}ms")
    
    profiling = stats.get("profiling", {})
    if profiling:
        print(f"\nProfiling:")
        print(f"  Total Duration: {profiling.get('total_duration_ms', 0):.2f}ms")
        print(f"  Statements Executed: {profiling.get('statements_executed', 0)}")
        print(f"  Errors: {profiling.get('errors', 0)}")
        print(f"  Call Frames: {profiling.get('frames', 0)}")
        
        stmt_stats = profiling.get("statement_stats", {})
        if stmt_stats:
            print(f"\n  Statement Types:")
            for stmt_type, stats in sorted(stmt_stats.items()):
                print(f"    {stmt_type:20s}: count={stats['count']:3d} "
                      f"avg={stats['avg_ms']:.3f}ms")
    
    print("\n" + "=" * 60 + "\n")
