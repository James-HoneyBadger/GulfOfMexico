"""
Enhanced Debugging and Profiling Tools - Phase 5

Comprehensive profiling, tracing, and debugging capabilities for the interpreter.

Features:
    - Execution profiling with detailed metrics
    - Call stack tracing
    - Performance timeline visualization
    - Memory usage tracking
    - Variable scope inspection
    - Statement execution logging
"""

import time
import sys
from dataclasses import dataclass, field
from typing import Optional, Any, Callable
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExecutionFrame:
    """Represents a single execution frame (function/block)."""
    
    frame_type: str  # "function", "block", "loop", etc.
    name: str
    start_time: float
    end_time: Optional[float] = None
    statements_executed: int = 0
    errors: int = 0
    depth: int = 0
    variables: dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_ms(self) -> float:
        """Get frame duration in milliseconds."""
        if self.end_time is None:
            return (time.perf_counter() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000
    
    @property
    def is_active(self) -> bool:
        """Check if frame is still active."""
        return self.end_time is None


@dataclass
class ExecutionTrace:
    """Complete execution trace for analysis."""
    
    total_duration_ms: float = 0.0
    frames: list[ExecutionFrame] = field(default_factory=list)
    statements_executed: int = 0
    errors_encountered: int = 0
    peak_memory_bytes: int = 0
    timeline: list[tuple[float, str]] = field(default_factory=list)
    
    def add_frame(self, frame: ExecutionFrame) -> None:
        """Add execution frame."""
        self.frames.append(frame)
        self.statements_executed += frame.statements_executed
        self.errors_encountered += frame.errors
    
    def add_timeline_event(self, timestamp_ms: float, event: str) -> None:
        """Add timeline event."""
        self.timeline.append((timestamp_ms, event))


class PerformanceProfiler:
    """Detailed performance profiler for statement execution.
    
    Tracks:
        - Statement execution time
        - Handler performance
        - Memory usage
        - Execution frequency
    """
    
    def __init__(self):
        """Initialize profiler."""
        self._frame_stack: list[ExecutionFrame] = []
        self._trace = ExecutionTrace()
        self._start_time = time.perf_counter()
        self._statement_times: dict[str, list[float]] = defaultdict(list)
        self._function_calls: dict[str, int] = defaultdict(int)
        self._enabled = False
    
    def enable(self) -> None:
        """Enable profiling."""
        self._enabled = True
        self._start_time = time.perf_counter()
    
    def disable(self) -> None:
        """Disable profiling."""
        self._enabled = False
    
    def push_frame(
        self,
        frame_type: str,
        name: str,
        depth: int = 0,
    ) -> None:
        """Push execution frame.
        
        Args:
            frame_type: Type of frame ("function", "block", etc.)
            name: Frame name
            depth: Call stack depth
        """
        if not self._enabled:
            return
        
        frame = ExecutionFrame(
            frame_type=frame_type,
            name=name,
            start_time=time.perf_counter(),
            depth=depth,
        )
        self._frame_stack.append(frame)
    
    def pop_frame(self) -> Optional[ExecutionFrame]:
        """Pop execution frame.
        
        Returns:
            Popped frame or None if stack empty
        """
        if not self._enabled or not self._frame_stack:
            return None
        
        frame = self._frame_stack.pop()
        frame.end_time = time.perf_counter()
        self._trace.add_frame(frame)
        return frame
    
    def record_statement_time(self, stmt_type: str, elapsed_ms: float) -> None:
        """Record statement execution time.
        
        Args:
            stmt_type: Type of statement
            elapsed_ms: Execution time in milliseconds
        """
        if not self._enabled:
            return
        
        self._statement_times[stmt_type].append(elapsed_ms)
        if self._frame_stack:
            self._frame_stack[-1].statements_executed += 1
    
    def record_function_call(self, func_name: str) -> None:
        """Record function call.
        
        Args:
            func_name: Function name
        """
        if not self._enabled:
            return
        
        self._function_calls[func_name] += 1
    
    def record_error(self) -> None:
        """Record an error in current frame."""
        if not self._enabled or not self._frame_stack:
            return
        
        self._frame_stack[-1].errors += 1
        self._trace.errors_encountered += 1
    
    def get_trace(self) -> ExecutionTrace:
        """Get execution trace.
        
        Returns:
            ExecutionTrace object
        """
        self._trace.total_duration_ms = (time.perf_counter() - self._start_time) * 1000
        return self._trace
    
    def get_statement_stats(self) -> dict[str, dict[str, float]]:
        """Get statistics for each statement type.
        
        Returns:
            Dictionary mapping statement types to stats
        """
        stats = {}
        for stmt_type, times in self._statement_times.items():
            if times:
                stats[stmt_type] = {
                    "count": len(times),
                    "total_ms": sum(times),
                    "avg_ms": sum(times) / len(times),
                    "min_ms": min(times),
                    "max_ms": max(times),
                }
        return stats
    
    def get_function_stats(self) -> dict[str, int]:
        """Get function call statistics.
        
        Returns:
            Dictionary mapping function names to call counts
        """
        return dict(self._function_calls)
    
    def reset(self) -> None:
        """Reset profiler state."""
        self._frame_stack = []
        self._trace = ExecutionTrace()
        self._start_time = time.perf_counter()
        self._statement_times.clear()
        self._function_calls.clear()


class ExecutionDebugger:
    """Enhanced debugger for execution visualization and inspection.
    
    Provides:
        - Variable inspection
        - Scope tracking
        - Breakpoint support (basic)
        - Execution logging
    """
    
    def __init__(self, enable_breakpoints: bool = False):
        """Initialize debugger.
        
        Args:
            enable_breakpoints: Whether to support breakpoints
        """
        self._breakpoints: set[tuple[str, int]] = set()  # (filename, line)
        self._watches: dict[str, Callable[[Any], bool]] = {}
        self._enabled = False
        self._enable_breakpoints = enable_breakpoints
        self._log_statements = False
        self._scope_stack: list[dict[str, Any]] = []
    
    def enable(self) -> None:
        """Enable debugging."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable debugging."""
        self._enabled = False
    
    def set_breakpoint(self, filename: str, line: int) -> None:
        """Set breakpoint at line.
        
        Args:
            filename: Source file
            line: Line number
        """
        if self._enable_breakpoints:
            self._breakpoints.add((filename, line))
    
    def remove_breakpoint(self, filename: str, line: int) -> None:
        """Remove breakpoint.
        
        Args:
            filename: Source file
            line: Line number
        """
        self._breakpoints.discard((filename, line))
    
    def add_watch(self, var_name: str, condition: Callable[[Any], bool]) -> None:
        """Add variable watch.
        
        Calls condition when variable changes. Condition should return
        True if watch should trigger, False otherwise.
        
        Args:
            var_name: Variable name to watch
            condition: Condition function
        """
        self._watches[var_name] = condition
    
    def remove_watch(self, var_name: str) -> None:
        """Remove variable watch.
        
        Args:
            var_name: Variable name
        """
        self._watches.pop(var_name, None)
    
    def check_watches(self, namespace: dict[str, Any]) -> list[str]:
        """Check all watches against current namespace.
        
        Args:
            namespace: Current variable namespace
            
        Returns:
            List of triggered watch names
        """
        if not self._enabled:
            return []
        
        triggered = []
        for var_name, condition in self._watches.items():
            if var_name in namespace:
                try:
                    if condition(namespace[var_name]):
                        triggered.append(var_name)
                except Exception as e:
                    logger.error(f"Watch condition error for {var_name}: {e}")
        
        return triggered
    
    def push_scope(self, scope_name: str) -> None:
        """Push new scope.
        
        Args:
            scope_name: Name of scope
        """
        if self._enabled:
            self._scope_stack.append({"name": scope_name, "variables": {}})
    
    def pop_scope(self) -> Optional[dict[str, Any]]:
        """Pop current scope.
        
        Returns:
            Popped scope or None if empty
        """
        if self._enabled and self._scope_stack:
            return self._scope_stack.pop()
        return None
    
    def inspect_variable(self, name: str) -> Optional[Any]:
        """Inspect variable in current scope.
        
        Args:
            name: Variable name
            
        Returns:
            Variable value or None if not found
        """
        if not self._scope_stack:
            return None
        
        for scope in reversed(self._scope_stack):
            if name in scope["variables"]:
                return scope["variables"][name]
        
        return None
    
    def log_statement_execution(self, stmt_type: str, line: int) -> None:
        """Log statement execution.
        
        Args:
            stmt_type: Statement type
            line: Source line number
        """
        if self._enabled and self._log_statements:
            logger.debug(f"Execute {stmt_type} at line {line}")
    
    def enable_statement_logging(self) -> None:
        """Enable statement execution logging."""
        self._log_statements = True
    
    def disable_statement_logging(self) -> None:
        """Disable statement execution logging."""
        self._log_statements = False


class ProfilingContext:
    """Context manager for profiling code blocks.
    
    Usage:
        profiler = PerformanceProfiler()
        profiler.enable()
        
        with ProfilingContext(profiler, "main_block"):
            # Code to profile
            pass
        
        trace = profiler.get_trace()
    """
    
    def __init__(self, profiler: PerformanceProfiler, block_name: str):
        """Initialize profiling context.
        
        Args:
            profiler: PerformanceProfiler instance
            block_name: Name of block being profiled
        """
        self._profiler = profiler
        self._block_name = block_name
    
    def __enter__(self):
        """Enter context."""
        self._profiler.push_frame("context", self._block_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        if exc_type is not None:
            self._profiler.record_error()
        self._profiler.pop_frame()
        return False


# Global profiler and debugger instances
_global_profiler = PerformanceProfiler()
_global_debugger = ExecutionDebugger()


def get_global_profiler() -> PerformanceProfiler:
    """Get global profiler instance.
    
    Returns:
        Global PerformanceProfiler
    """
    return _global_profiler


def get_global_debugger() -> ExecutionDebugger:
    """Get global debugger instance.
    
    Returns:
        Global ExecutionDebugger
    """
    return _global_debugger
