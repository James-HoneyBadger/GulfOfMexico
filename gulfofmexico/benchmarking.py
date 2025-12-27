"""
Phase 5 Performance Benchmarking Suite

Comprehensive benchmarking tools for measuring and comparing interpreter performance.

Features:
    - Statement execution benchmarks
    - Handler dispatch performance
    - Memory usage profiling
    - Cache effectiveness testing
    - Performance regression detection
"""

import time
import statistics
from dataclasses import dataclass
from typing import Callable, Optional, Any, list
import logging

from gulfofmexico.interpreter_phase5 import get_optimized_context
from gulfofmexico.handler_dispatch import DispatcherStats

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Result of a single benchmark execution."""
    
    name: str
    iterations: int
    times_ms: list[float]
    
    @property
    def min_ms(self) -> float:
        """Minimum execution time."""
        return min(self.times_ms) if self.times_ms else 0.0
    
    @property
    def max_ms(self) -> float:
        """Maximum execution time."""
        return max(self.times_ms) if self.times_ms else 0.0
    
    @property
    def mean_ms(self) -> float:
        """Mean execution time."""
        return statistics.mean(self.times_ms) if self.times_ms else 0.0
    
    @property
    def median_ms(self) -> float:
        """Median execution time."""
        return statistics.median(self.times_ms) if self.times_ms else 0.0
    
    @property
    def stdev_ms(self) -> float:
        """Standard deviation of execution times."""
        if len(self.times_ms) < 2:
            return 0.0
        return statistics.stdev(self.times_ms)
    
    def format_report(self) -> str:
        """Format benchmark result as report.
        
        Returns:
            Formatted report string
        """
        lines = [
            f"Benchmark: {self.name}",
            f"  Iterations: {self.iterations}",
            f"  Min:    {self.min_ms:.4f}ms",
            f"  Max:    {self.max_ms:.4f}ms",
            f"  Mean:   {self.mean_ms:.4f}ms",
            f"  Median: {self.median_ms:.4f}ms",
            f"  StdDev: {self.stdev_ms:.4f}ms",
        ]
        return "\n".join(lines)


@dataclass
class BenchmarkComparison:
    """Comparison between two benchmark results."""
    
    baseline: BenchmarkResult
    current: BenchmarkResult
    
    @property
    def mean_improvement_percent(self) -> float:
        """Percentage improvement in mean time.
        
        Positive = faster, Negative = slower
        """
        if self.baseline.mean_ms == 0:
            return 0.0
        improvement = (self.baseline.mean_ms - self.current.mean_ms)
        return (improvement / self.baseline.mean_ms) * 100
    
    @property
    def is_regression(self) -> bool:
        """Check if result is a performance regression.
        
        Returns True if current is significantly slower than baseline.
        """
        return self.mean_improvement_percent < -5.0  # 5% regression threshold
    
    def format_report(self) -> str:
        """Format comparison report.
        
        Returns:
            Formatted report string
        """
        improvement = self.mean_improvement_percent
        improvement_str = f"{improvement:+.2f}%"
        status = "✓ IMPROVED" if improvement > 0 else ("✗ REGRESSION" if improvement < -5 else "~ UNCHANGED")
        
        lines = [
            f"Comparison: {self.baseline.name}",
            f"  Status: {status}",
            f"  Baseline Mean: {self.baseline.mean_ms:.4f}ms",
            f"  Current Mean:  {self.current.mean_ms:.4f}ms",
            f"  Improvement:   {improvement_str}",
        ]
        return "\n".join(lines)


class PerformanceBenchmark:
    """Performance benchmarking suite for the interpreter.
    
    Supports:
        - Micro-benchmarks for individual operations
        - Macro-benchmarks for complete programs
        - Performance regression detection
        - Comparative analysis
    """
    
    def __init__(self):
        """Initialize benchmark suite."""
        self._results: dict[str, BenchmarkResult] = {}
    
    def benchmark(
        self,
        name: str,
        func: Callable[[], Any],
        iterations: int = 100,
        warmup: int = 10,
    ) -> BenchmarkResult:
        """Run a benchmark.
        
        Args:
            name: Benchmark name
            func: Function to benchmark
            iterations: Number of iterations to run
            warmup: Number of warmup iterations
            
        Returns:
            BenchmarkResult
        """
        # Warmup iterations to stabilize JIT/caches
        for _ in range(warmup):
            try:
                func()
            except Exception as e:
                logger.warning(f"Warmup iteration failed: {e}")
        
        # Actual benchmark iterations
        times_ms = []
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                func()
            except Exception as e:
                logger.error(f"Benchmark iteration failed: {e}")
            end = time.perf_counter()
            times_ms.append((end - start) * 1000)
        
        result = BenchmarkResult(name, iterations, times_ms)
        self._results[name] = result
        
        logger.info(f"Completed benchmark: {name}")
        return result
    
    def benchmark_dispatch_overhead(self) -> BenchmarkResult:
        """Benchmark handler dispatch overhead.
        
        Tests the cost of the dispatcher's caching and routing mechanisms.
        
        Returns:
            BenchmarkResult
        """
        from gulfofmexico.processor.syntax_tree import ExpressionStatement
        from gulfofmexico.builtin import GulfOfMexicoNumber
        from gulfofmexico.processor.expression_tree import ValueNode
        from gulfofmexico.base import Token, TokenType
        
        ctx = get_optimized_context()
        
        # Create a simple expression statement for dispatch
        token = Token(TokenType.NUMBER, "42", 0)
        value_node = ValueNode(GulfOfMexicoNumber(42), token)
        stmt = ExpressionStatement(value_node, False)
        context = {}
        
        def dispatch_once():
            ctx.dispatcher.dispatch(stmt, context)
        
        return self.benchmark(
            "handler_dispatch_overhead",
            dispatch_once,
            iterations=1000,
            warmup=100,
        )
    
    def benchmark_cache_hit_rate(self) -> float:
        """Benchmark cache hit rate.
        
        Returns:
            Cache hit rate (0.0 to 1.0)
        """
        from gulfofmexico.processor.syntax_tree import ExpressionStatement, VariableDeclaration
        from gulfofmexico.builtin import GulfOfMexicoNumber
        from gulfofmexico.processor.expression_tree import ValueNode
        from gulfofmexico.base import Token, TokenType, Name
        
        ctx = get_optimized_context()
        ctx.dispatcher.reset_stats()
        
        # Create various statement types
        token = Token(TokenType.NUMBER, "42", 0)
        value_node = ValueNode(GulfOfMexicoNumber(42), token)
        expr_stmt = ExpressionStatement(value_node, False)
        
        name_token = Token(TokenType.IDENTIFIER, "x", 0)
        decl_stmt = VariableDeclaration(
            Name(name_token, name_token.value),
            value_node,
            False,
            False,
            None,
            False,
        )
        
        # Execute multiple times to build cache
        context = {}
        for _ in range(100):
            ctx.dispatcher.dispatch(expr_stmt, context)
            ctx.dispatcher.dispatch(decl_stmt, context)
        
        stats = ctx.dispatcher.get_stats()
        return stats.cache_hit_rate
    
    def get_result(self, name: str) -> Optional[BenchmarkResult]:
        """Get a benchmark result.
        
        Args:
            name: Benchmark name
            
        Returns:
            BenchmarkResult or None if not found
        """
        return self._results.get(name)
    
    def compare(
        self,
        baseline_name: str,
        current_name: str,
    ) -> Optional[BenchmarkComparison]:
        """Compare two benchmark results.
        
        Args:
            baseline_name: Name of baseline result
            current_name: Name of current result
            
        Returns:
            BenchmarkComparison or None if results not found
        """
        baseline = self._results.get(baseline_name)
        current = self._results.get(current_name)
        
        if baseline is None or current is None:
            return None
        
        return BenchmarkComparison(baseline, current)
    
    def print_results(self) -> None:
        """Print all benchmark results."""
        print("\n" + "=" * 70)
        print("PERFORMANCE BENCHMARK RESULTS")
        print("=" * 70)
        
        for name, result in self._results.items():
            print("\n" + result.format_report())
        
        print("\n" + "=" * 70 + "\n")
    
    def check_regressions(self, threshold_percent: float = 5.0) -> list[str]:
        """Check for performance regressions.
        
        Args:
            threshold_percent: Regression threshold percentage
            
        Returns:
            List of regression names
        """
        regressions = []
        
        # TODO: Implement regression detection against baseline
        # This would require loading and comparing against previous results
        
        return regressions


def run_phase5_benchmark_suite() -> None:
    """Run comprehensive Phase 5 benchmark suite."""
    suite = PerformanceBenchmark()
    
    print("\n" + "=" * 70)
    print("PHASE 5 PERFORMANCE BENCHMARK SUITE")
    print("=" * 70 + "\n")
    
    # Benchmark 1: Handler dispatch overhead
    print("Benchmarking handler dispatch overhead...")
    dispatch_result = suite.benchmark_dispatch_overhead()
    print(dispatch_result.format_report())
    
    # Benchmark 2: Cache hit rate
    print("\nBenchmarking cache hit rate...")
    cache_hit_rate = suite.benchmark_cache_hit_rate()
    print(f"Cache Hit Rate: {cache_hit_rate:.2%}")
    
    # Benchmark 3: Get execution statistics
    ctx = get_optimized_context()
    stats = ctx.get_dispatch_stats()
    print(f"\nDispatcher Statistics:")
    print(f"  Total Statements: {stats.total_statements}")
    print(f"  Total Time: {stats.total_dispatch_time_ms:.2f}ms")
    print(f"  Avg Time per Statement: {stats.avg_dispatch_time_ms:.4f}ms")
    
    print("\n" + "=" * 70 + "\n")


# Global benchmark suite instance
_global_benchmark_suite = PerformanceBenchmark()


def get_benchmark_suite() -> PerformanceBenchmark:
    """Get global benchmark suite.
    
    Returns:
        Global PerformanceBenchmark instance
    """
    return _global_benchmark_suite
