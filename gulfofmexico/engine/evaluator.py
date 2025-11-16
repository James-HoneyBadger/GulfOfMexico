"""EXPERIMENTAL expression evaluator with caching support.

⚠️ WARNING: This module is NOT used in production! ⚠️

The actual Gulf of Mexico interpreter uses evaluate_expression() in interpreter.py
for expression evaluation. This experimental evaluator demonstrates how caching
could improve performance in a future refactoring.
"""

from typing import Optional
from functools import lru_cache
from gulfofmexico.context import ExecutionContext
from gulfofmexico.builtin import GulfOfMexicoValue
from gulfofmexico.processor.expression_tree import ExpressionTreeNode
from gulfofmexico.constants import EXPRESSION_CACHE_SIZE


class ExpressionEvaluator:
    """Evaluates expressions with optional caching for performance.

    This class wraps the core expression evaluation logic and adds
    caching for pure expressions (no side effects).
    """

    def __init__(self, enable_cache: bool = True):
        """Initialize the expression evaluator.

        Args:
            enable_cache: Whether to enable expression caching
        """
        self.enable_cache = enable_cache
        self._cache: dict[int, GulfOfMexicoValue] = {}
        self._cache_hits = 0
        self._cache_misses = 0

    def evaluate(
        self,
        expression: ExpressionTreeNode,
        context: ExecutionContext,
    ) -> GulfOfMexicoValue:
        """Evaluate an expression with optional caching.

        Args:
            expression: The expression tree to evaluate
            context: Execution context

        Returns:
            The evaluated value
        """
        # Import here to avoid circular dependency
        from gulfofmexico.interpreter import evaluate_expression

        # Check cache if enabled and expression is pure
        if self.enable_cache and self._is_pure(expression):
            cache_key = self._get_cache_key(expression, context)

            if cache_key in self._cache:
                self._cache_hits += 1
                return self._cache[cache_key]

            self._cache_misses += 1

        # Evaluate expression
        result = evaluate_expression(
            expression,
            context.namespaces,
            context.async_statements,
            context.when_watchers,
        )

        # Cache result if applicable
        if (
            self.enable_cache
            and self._is_pure(expression)
            and len(self._cache) < EXPRESSION_CACHE_SIZE
        ):
            cache_key = self._get_cache_key(expression, context)
            self._cache[cache_key] = result

        return result

    def _is_pure(self, expression: ExpressionTreeNode) -> bool:
        """Check if an expression is pure (no side effects).

        Pure expressions:
        - Literal values
        - Simple arithmetic operations
        - Variable reads (but not writes)

        Not pure:
        - Function calls (may have side effects)
        - Assignments
        - Method calls

        Args:
            expression: Expression to check

        Returns:
            True if expression is pure
        """
        from gulfofmexico.processor.expression_tree import (
            ValueNode,
            SingleOperatorNode,
            FunctionNode,
        )

        if isinstance(expression, ValueNode):
            return True

        if isinstance(expression, SingleOperatorNode):
            # Binary operations are pure if operands are pure
            return self._is_pure(expression.left) and self._is_pure(expression.right)

        if isinstance(expression, FunctionNode):
            # Function calls may have side effects
            return False

        # Conservative: assume impure
        return False

    def _get_cache_key(
        self,
        expression: ExpressionTreeNode,
        context: ExecutionContext,
    ) -> int:
        """Generate a cache key for an expression.

        This creates a structural hash of the expression tree combined
        with relevant namespace state. Two expressions with the same
        structure and variable values will have the same cache key.

        Args:
            expression: Expression to generate key for
            context: Execution context

        Returns:
            Cache key as integer
        """
        expr_hash = self._hash_expression_tree(expression)
        namespace_hash = self._hash_namespace_state(context)
        return hash((expr_hash, namespace_hash))

    def _hash_expression_tree(self, node: ExpressionTreeNode) -> int:
        """Recursively hash an expression tree structure.

        Args:
            node: Expression tree node

        Returns:
            Hash of the tree structure
        """
        from gulfofmexico.processor.expression_tree import (
            ValueNode,
            SingleOperatorNode,
            FunctionNode,
        )

        if isinstance(node, ValueNode):
            # Hash based on token type and value
            if hasattr(node.value, "type") and hasattr(node.value, "value"):
                return hash((node.value.type, node.value.value))
            return hash(str(node.value))

        if isinstance(node, SingleOperatorNode):
            # Hash based on operator and operands
            op_hash = hash(node.operator.value) if node.operator else 0
            left_hash = self._hash_expression_tree(node.left)
            right_hash = self._hash_expression_tree(node.right)
            return hash((op_hash, left_hash, right_hash))

        # For other node types, use a generic hash
        return hash(type(node).__name__)

    def _hash_namespace_state(self, context: ExecutionContext) -> int:
        """Hash the current namespace state for cache key.

        For pure expressions, we only need to consider variable values
        that might be referenced in the expression.

        Args:
            context: Execution context

        Returns:
            Hash of relevant namespace state
        """
        # For now, use a simple approach: hash namespace depth
        # A more sophisticated approach would track which variables
        # are actually referenced in the expression
        return hash((len(context.namespaces), id(context.namespaces[-1])))

    def clear_cache(self) -> None:
        """Clear the expression cache."""
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
