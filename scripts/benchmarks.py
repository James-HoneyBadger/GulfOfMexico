"""⚠️ EXPERIMENTAL - Performance benchmarks for the experimental engine.

WARNING: These benchmarks test the EXPERIMENTAL gulfofmexico/engine/ package,
NOT the production interpreter (gulfofmexico/interpreter.py).

The benchmarks show performance improvements for the experimental caching
infrastructure (ExpressionEvaluator, NamespaceManager), but this code is
NOT used in production.

The 1.77x speedup reported in IMPLEMENTATION_SUMMARY.md applies ONLY to the
experimental engine, not to actual Gulf of Mexico code execution.

To benchmark the production interpreter, you would need to:
1. Create benchmark .gom files
2. Time execution via gulfofmexico.__init__.run_file()
3. Compare with/without proposed optimizations to interpreter.py
"""

import time
import statistics
from typing import Callable, Any
from gulfofmexico.engine.evaluator import ExpressionEvaluator
from gulfofmexico.engine.namespace import NamespaceManager
from gulfofmexico.builtin import (
    GulfOfMexicoNumber,
    Variable,
    VariableLifetime,
    Name,
)


def benchmark(func: Callable, iterations: int = 1000) -> dict[str, float]:
    """Benchmark a function.

    Args:
        func: Function to benchmark
        iterations: Number of iterations to run

    Returns:
        Dictionary with timing statistics
    """
    times = []

    for _ in range(iterations):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append(end - start)

    return {
        "mean": statistics.mean(times) * 1000,  # ms
        "median": statistics.median(times) * 1000,  # ms
        "stdev": statistics.stdev(times) * 1000 if len(times) > 1 else 0,
        "min": min(times) * 1000,  # ms
        "max": max(times) * 1000,  # ms
        "total": sum(times) * 1000,  # ms
    }


def benchmark_namespace_lookup():
    """Benchmark namespace lookups with and without caching."""
    # Create a deep namespace stack
    namespaces = []
    for i in range(10):
        ns = {}
        for j in range(100):
            var_name = f"var_{i}_{j}"
            ns[var_name] = Variable(
                var_name,
                [VariableLifetime(GulfOfMexicoNumber(j), 100000000000, 0, True, True)],
                [],
            )
        namespaces.append(ns)

    # Variable in deepest scope
    test_var = "var_0_50"

    # Benchmark without caching
    manager_no_cache = NamespaceManager(namespaces, enable_cache=False)

    def lookup_no_cache():
        manager_no_cache.lookup(test_var)

    print("Namespace Lookup WITHOUT Cache:")
    no_cache_stats = benchmark(lookup_no_cache, iterations=10000)
    for key, value in no_cache_stats.items():
        print(f"  {key}: {value:.4f}ms")

    # Benchmark with caching
    manager_cache = NamespaceManager(namespaces, enable_cache=True)

    def lookup_cache():
        manager_cache.lookup(test_var)

    print("\nNamespace Lookup WITH Cache:")
    cache_stats = benchmark(lookup_cache, iterations=10000)
    for key, value in cache_stats.items():
        print(f"  {key}: {value:.4f}ms")

    # Calculate speedup
    speedup = no_cache_stats["mean"] / cache_stats["mean"]
    print(f"\nSpeedup: {speedup:.2f}x faster with cache")
    print(f"Cache stats: {manager_cache.get_stats()}")


def benchmark_expression_evaluation():
    """Benchmark expression evaluation (placeholder)."""
    print("\nExpression Evaluation Benchmarks:")
    print("  (To be implemented with actual expression trees)")

    # This would benchmark expression evaluation with/without caching
    # once expression trees are properly integrated


def benchmark_handler_dispatch():
    """Benchmark handler registry dispatch."""
    from gulfofmexico.handlers import HandlerRegistry
    from gulfofmexico.engine.handlers.variables import (
        VariableDeclarationHandler,
    )
    from gulfofmexico.processor.syntax_tree import VariableDeclaration
    from gulfofmexico.base import Token, TokenType
    from gulfofmexico.processor.expression_tree import ValueNode

    registry = HandlerRegistry()
    registry.register(VariableDeclarationHandler())

    stmt = VariableDeclaration(
        name=Token(TokenType.NAME, "x", 1, 4),
        modifiers=[Token(TokenType.NAME, "var", 1, 0)],
        type_annotation=None,
        lifetime=None,
        expression=ValueNode(Token(TokenType.NAME, "5", 1, 8)),
        debug=0,
        confidence=1,
    )

    def dispatch():
        registry.get_handler(stmt)

    print("\nHandler Dispatch (with type caching):")
    stats = benchmark(dispatch, iterations=10000)
    for key, value in stats.items():
        print(f"  {key}: {value:.4f}ms")


def run_all_benchmarks():
    """Run all performance benchmarks."""
    print("=" * 60)
    print("Gulf of Mexico Interpreter - Performance Benchmarks")
    print("=" * 60)

    benchmark_namespace_lookup()
    benchmark_expression_evaluation()
    benchmark_handler_dispatch()

    print("\n" + "=" * 60)
    print("Benchmarks Complete")
    print("=" * 60)


if __name__ == "__main__":
    run_all_benchmarks()
