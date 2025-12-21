"""
Expression Handler for Gulf of Mexico Interpreter.

Handles evaluation of all expression types including:
- Function calls (built-in and user-defined)
- Lists
- Values (literals and variables)
- Indexing operations
- Binary and unary operations
- Expression caching for performance optimization
"""

from __future__ import annotations

import logging
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Union

from gulfofmexico.base import StatementHandler
from gulfofmexico.builtin import (
    BuiltinFunction,
    GulfOfMexicoFunction,
    GulfOfMexicoIndexable,
    GulfOfMexicoKeyword,
    GulfOfMexicoList,
    GulfOfMexicoNamespaceable,
    GulfOfMexicoNumber,
    GulfOfMexicoPromise,
    GulfOfMexicoSpecialBlankValue,
    GulfOfMexicoString,
    GulfOfMexicoUndefined,
    GulfOfMexicoValue,
    Name,
    Variable,
)
from gulfofmexico.constants import OperatorType
from gulfofmexico.context import ExecutionContext
from gulfofmexico.processor.syntax_tree import (
    ExpressionNode,
    ExpressionTreeNode,
    FunctionNode,
    IndexNode,
    ListNode,
    ReturnStatement,
    SingleOperatorNode,
    Token,
    TokenType,
    ValueNode,
)


logger = logging.getLogger(__name__)


@dataclass
class ExpressionCacheEntry:
    """Single cached expression result with metadata."""

    value: GulfOfMexicoValue
    hash_key: str
    access_count: int = 1
    dependencies: set[str] = field(default_factory=set)

    def is_stale(self, max_age: int = 100) -> bool:
        """Check if cache entry is too old based on access count."""
        return access_count > max_age


class ExpressionCache:
    """Optional performance cache for expression evaluation results.
    
    Caches expression results to avoid re-evaluating identical expressions.
    Provides statistics and manual invalidation.
    """

    def __init__(self, enabled: bool = False, max_size: int = 1000):
        """Initialize expression cache.
        
        Args:
            enabled: Whether caching is enabled (default: False for safety)
            max_size: Maximum number of cached expressions
        """
        self.enabled = enabled
        self.max_size = max_size
        self.cache: Dict[str, ExpressionCacheEntry] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[GulfOfMexicoValue]:
        """Retrieve cached expression result."""
        if not self.enabled or key not in self.cache:
            self.misses += 1
            return None
        entry = self.cache[key]
        entry.access_count += 1
        self.hits += 1
        return entry.value

    def set(self, key: str, value: GulfOfMexicoValue, dependencies: set[str] = None) -> None:
        """Cache expression result."""
        if not self.enabled:
            return
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        self.cache[key] = ExpressionCacheEntry(
            value=value,
            hash_key=key,
            dependencies=dependencies or set(),
        )

    def invalidate(self, dependency: str) -> None:
        """Invalidate all cache entries depending on a variable."""
        if not self.enabled:
            return
        to_remove = [
            key for key, entry in self.cache.items() 
            if dependency in entry.dependencies
        ]
        for key in to_remove:
            del self.cache[key]

    def clear(self) -> None:
        """Clear entire cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "enabled": self.enabled,
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "total_accesses": total,
        }


class ExpressionHandler(StatementHandler):
    """Handler for evaluating all expression types.
    
    Supports:
    - Function calls (built-in and user-defined async/sync)
    - List literals
    - Value nodes (variables, literals, strings)
    - Indexing operations (list[i], dict[key], etc)
    - Binary operations (arithmetic, logical, comparison)
    - Unary operations (negation, logical not)
    - Expression caching for performance
    - When-statement reactive evaluation
    """

    def __init__(self, cache_enabled: bool = False):
        """Initialize expression handler.
        
        Args:
            cache_enabled: Enable expression result caching
        """
        super().__init__()
        self.cache = ExpressionCache(enabled=cache_enabled)
        self.eval_count = 0
        self.builtin_imports = {}  # Imported from interpreter scope

    def set_interpreter_imports(self, imports: Dict[str, Callable]) -> None:
        """Set references to interpreter functions needed for expression evaluation.
        
        Required imports:
        - get_built_expression
        - evaluate_escape_sequences
        - get_name_from_namespaces
        - get_value_from_namespaces
        - interpret_formatted_string
        - perform_two_value_operation
        - perform_single_value_operation
        - db_to_boolean
        - raise_error_at_line
        - raise_error_at_token
        - register_async_function
        - evaluate_normal_function
        - get_code_from_when_statement_watchers
        - execute_conditional
        """
        self.builtin_imports.update(imports)

    def can_handle(self, expr: ExpressionTreeNode) -> bool:
        """Expression handler can evaluate any expression tree node."""
        return isinstance(
            expr,
            (
                FunctionNode,
                ListNode,
                ValueNode,
                IndexNode,
                ExpressionNode,
                SingleOperatorNode,
            ),
        )

    def execute(self, expr: ExpressionTreeNode, context: ExecutionContext) -> GulfOfMexicoValue:
        """Evaluate expression in context.
        
        Args:
            expr: Expression tree node to evaluate
            context: Execution context with namespaces and state
            
        Returns:
            GulfOfMexicoValue result of expression evaluation
        """
        self.eval_count += 1
        
        if context.debug_level >= 3:
            logger.debug(f"[Expression] Evaluating: {type(expr).__name__}")

        return self._evaluate_expression_impl(expr, context)

    def _evaluate_expression_impl(
        self,
        expr: Union[list[Token], ExpressionTreeNode],
        context: ExecutionContext,
    ) -> GulfOfMexicoValue:
        """Core expression evaluation implementation with pattern matching."""
        # Get built expression from token list or expression tree
        get_built_expr = self.builtin_imports.get("get_built_expression")
        if get_built_expr:
            expr = get_built_expr(expr)

        match expr:
            case FunctionNode():
                return self._handle_function_call(expr, context)

            case ListNode():
                return self._handle_list(expr, context)

            case ValueNode():
                return self._handle_value(expr, context)

            case IndexNode():
                return self._handle_index(expr, context)

            case ExpressionNode():
                return self._handle_binary_operation(expr, context)

            case SingleOperatorNode():
                return self._handle_unary_operation(expr, context)

        return GulfOfMexicoUndefined()

    def _handle_function_call(
        self,
        expr: FunctionNode,
        context: ExecutionContext,
    ) -> GulfOfMexicoValue:
        """Handle function call evaluation including built-in and user-defined."""
        get_name = self.builtin_imports.get("get_name_from_namespaces")
        if not get_name:
            raise RuntimeError("Missing get_name_from_namespaces import")

        # Get function from namespace
        func = get_name(expr.name.value, context.namespaces)

        if func is None:
            raise_error = self.builtin_imports.get("raise_error_at_token")
            if raise_error:
                raise_error(
                    context.filename,
                    context.code,
                    "Cannot find token in namespace.",
                    expr.name,
                )
            raise RuntimeError(f"Function {expr.name.value} not found")

        # Handle special keywords: await, previous, next
        force_execute_sync = False
        if isinstance(func.value, GulfOfMexicoKeyword):
            result = self._handle_keyword_function(expr, func, context)
            if result is not None:
                return result
            force_execute_sync = True

        if not isinstance(func.value, (BuiltinFunction, GulfOfMexicoFunction)):
            raise_error = self.builtin_imports.get("raise_error_at_token")
            if raise_error:
                raise_error(
                    context.filename,
                    context.code,
                    "Attempted function call on non-function value.",
                    expr.name,
                )
            raise RuntimeError("Invalid function call")

        # Handle dotted calls (method-style)
        caller = None
        extended_namespaces = context.namespaces
        dotted_call = len(name_split := expr.name.value.split(".")) > 1

        if dotted_call:
            caller = ".".join(name_split[:-1])
            if isinstance(func.value, BuiltinFunction) and func.value.modifies_caller:
                expr = deepcopy(expr)
                expr.args.insert(
                    0,
                    ValueNode(Token(TokenType.NAME, caller, expr.name.line, expr.name.col)),
                )

            # Extend namespaces for method calls
            caller_entry = get_name(caller, context.namespaces)
            if isinstance(caller_entry, (Variable, Name)):
                caller_val = caller_entry.value
                if isinstance(caller_val, GulfOfMexicoNamespaceable):
                    extended_namespaces = context.namespaces + [caller_val.namespace]

        # Evaluate arguments
        args = [self._evaluate_expression_impl(arg, context) for arg in expr.args]
        if args and isinstance(args[0], GulfOfMexicoSpecialBlankValue):
            args = args[1:]

        # Handle async functions
        if isinstance(func.value, GulfOfMexicoFunction) and func.value.is_async and not force_execute_sync:
            register_async = self.builtin_imports.get("register_async_function")
            if register_async:
                register_async(expr, func.value, extended_namespaces, args, context.async_statements)
            return GulfOfMexicoUndefined()

        # Evaluate function
        eval_func = self.builtin_imports.get("evaluate_normal_function")
        if not eval_func:
            raise RuntimeError("Missing evaluate_normal_function import")

        if isinstance(func.value, BuiltinFunction) and func.value.modifies_caller:
            if caller:
                caller_var = get_name(caller, context.namespaces)
                if isinstance(caller_var, Variable) and not caller_var.can_edit_value:
                    raise_error = self.builtin_imports.get("raise_error_at_line")
                    if raise_error:
                        raise_error(
                            context.filename,
                            context.code,
                            context.current_line,
                            "Cannot edit the value of this variable.",
                        )
                    raise RuntimeError("Cannot edit readonly variable")

            retval = eval_func(expr, func.value, extended_namespaces, args, context.when_statement_watchers)

            # Trigger when-statement watchers
            get_when_code = self.builtin_imports.get("get_code_from_when_statement_watchers")
            exec_cond = self.builtin_imports.get("execute_conditional")
            if get_when_code and exec_cond and args:
                when_watchers = get_when_code(id(args[0]), context.when_statement_watchers)
                for when_watcher in when_watchers:
                    if len(when_watcher) == 3:
                        condition, inside_statements, captured_namespaces = when_watcher
                    else:
                        condition, inside_statements = when_watcher
                        captured_namespaces = context.namespaces
                    
                    condition_val = self._evaluate_expression_impl(condition, context)
                    exec_cond(
                        condition_val,
                        inside_statements,
                        captured_namespaces,
                        context.when_statement_watchers,
                        {},
                        [],
                    )
            return retval

        return eval_func(expr, func.value, extended_namespaces, args, context.when_statement_watchers)

    def _handle_keyword_function(
        self,
        expr: FunctionNode,
        func: Union[Variable, Name],
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        """Handle special keyword functions: await, previous, next."""
        if not isinstance(func.value, GulfOfMexicoKeyword):
            return None

        keyword = func.value.value
        get_name = self.builtin_imports.get("get_name_from_namespaces")
        get_name_ns = self.builtin_imports.get("get_name_and_namespace_from_namespaces")
        raise_error_token = self.builtin_imports.get("raise_error_at_token")

        if keyword == "await":
            if len(expr.args) != 1:
                if raise_error_token:
                    raise_error_token(
                        context.filename,
                        context.code,
                        "Expected only one argument for await function.",
                        expr.name,
                    )
                raise RuntimeError("await expects 1 argument")

            if not isinstance(expr.args[0], FunctionNode):
                if raise_error_token:
                    raise_error_token(
                        context.filename,
                        context.code,
                        "Expected argument of await function to be a function call.",
                        expr.name,
                    )
                raise RuntimeError("await argument must be function call")

            expr = expr.args[0]
            func = get_name(expr.name.value, context.namespaces)
            if func is None:
                if raise_error_token:
                    raise_error_token(
                        context.filename,
                        context.code,
                        "Cannot find token in namespaces.",
                        expr.name,
                    )
                raise RuntimeError(f"Function {expr.name.value} not found")
            return None  # Continue with sync execution

        elif keyword == "previous":
            if len(expr.args) != 1:
                if raise_error_token:
                    raise_error_token(
                        context.filename,
                        context.code,
                        "Expected only one argument for previous function.",
                        expr.name,
                    )
                raise RuntimeError("previous expects 1 argument")

            if not isinstance(expr.args[0], ValueNode):
                if raise_error_token:
                    raise_error_token(
                        context.filename,
                        context.code,
                        "Expected argument of previous function to be a variable.",
                        expr.name,
                    )
                raise RuntimeError("previous argument must be variable")

            val = get_name(expr.args[0].name_or_value.value, context.namespaces)
            if not isinstance(val, Variable):
                if raise_error_token:
                    raise_error_token(
                        context.filename,
                        context.code,
                        "Expected argument of previous function to be a defined variable.",
                        expr.args[0].name_or_value,
                    )
                raise RuntimeError("previous argument must be variable")
            return val.prev_values[-1] if val.prev_values else GulfOfMexicoUndefined()

        elif keyword == "next":
            if len(expr.args) != 1:
                if raise_error_token:
                    raise_error_token(
                        context.filename,
                        context.code,
                        "Expected only one argument for next function.",
                        expr.name,
                    )
                raise RuntimeError("next expects 1 argument")

            if not isinstance(expr.args[0], ValueNode):
                if raise_error_token:
                    raise_error_token(
                        context.filename,
                        context.code,
                        "Expected argument of next function to be a variable.",
                        expr.name,
                    )
                raise RuntimeError("next argument must be variable")

            val = get_name(expr.args[0].name_or_value.value, context.namespaces)
            if not isinstance(val, Variable):
                if raise_error_token:
                    raise_error_token(
                        context.filename,
                        context.code,
                        "Expected argument of next function to be a defined variable.",
                        expr.args[0].name_or_value,
                    )
                raise RuntimeError("next argument must be variable")

            # Create promise for future value
            promise = GulfOfMexicoPromise(None)

            if get_name_ns:
                _, ns = get_name_ns(expr.args[0].name_or_value.value, context.namespaces)
                if ns:
                    ns_id = id(ns)
                    var_name = expr.args[0].name_or_value.value

                    # Register watcher for promise resolution
                    dummy_return = ReturnStatement(
                        keyword=None,
                        expression=[expr.args[0].name_or_value],
                        debug=0,
                    )

                    watchers_key = (var_name, ns_id)
                    context.when_statement_watchers[watchers_key] = (
                        dummy_return,
                        {watchers_key},
                        context.namespaces + [{}],
                        promise,
                    )

            return promise

        return None

    def _handle_list(self, expr: ListNode, context: ExecutionContext) -> GulfOfMexicoList:
        """Handle list literal evaluation."""
        return GulfOfMexicoList(
            [self._evaluate_expression_impl(x, context) for x in expr.values]
        )

    def _handle_value(self, expr: ValueNode, context: ExecutionContext) -> GulfOfMexicoValue:
        """Handle value node: literals, variables, strings."""
        if expr.name_or_value.type == TokenType.STRING:
            interpret_string = self.builtin_imports.get("interpret_formatted_string")
            evaluate_escape = self.builtin_imports.get("evaluate_escape_sequences")

            if interpret_string:
                retval = interpret_string(
                    expr.name_or_value,
                    context.namespaces,
                    context.async_statements,
                    context.when_statement_watchers,
                )
                if evaluate_escape and context.ignore_string_escape_sequences is False:
                    return evaluate_escape(retval)
                return retval
            return GulfOfMexicoString(expr.name_or_value.value)

        get_value = self.builtin_imports.get("get_value_from_namespaces")
        if get_value:
            return get_value(expr.name_or_value, context.namespaces)
        return GulfOfMexicoUndefined()

    def _handle_index(self, expr: IndexNode, context: ExecutionContext) -> GulfOfMexicoValue:
        """Handle indexing operation (list[i], dict[key], etc)."""
        value = self._evaluate_expression_impl(expr.value, context)
        index = self._evaluate_expression_impl(expr.index, context)

        if not isinstance(value, GulfOfMexicoIndexable):
            raise_error = self.builtin_imports.get("raise_error_at_line")
            if raise_error:
                raise_error(
                    context.filename,
                    context.code,
                    context.current_line,
                    "Attempting to index a value that is not indexable.",
                )
            raise RuntimeError("Cannot index non-indexable value")

        return value.access_index(index)

    def _handle_binary_operation(
        self,
        expr: ExpressionNode,
        context: ExecutionContext,
    ) -> GulfOfMexicoValue:
        """Handle binary operations with short-circuit evaluation."""
        left = self._evaluate_expression_impl(expr.left, context)

        # Short-circuit evaluation for logical operators
        db_bool = self.builtin_imports.get("db_to_boolean")
        if db_bool:
            left_bool = db_bool(left).value
            if left_bool is True and expr.operator == OperatorType.OR:
                return left
            elif left_bool is False and expr.operator == OperatorType.AND:
                return left

        right = self._evaluate_expression_impl(expr.right, context)

        perform_op = self.builtin_imports.get("perform_two_value_operation")
        if perform_op:
            return perform_op(left, right, expr.operator, expr.operator_token)
        return GulfOfMexicoUndefined()

    def _handle_unary_operation(
        self,
        expr: SingleOperatorNode,
        context: ExecutionContext,
    ) -> GulfOfMexicoValue:
        """Handle unary operations (negation, not, etc)."""
        val = self._evaluate_expression_impl(expr.expression, context)

        perform_op = self.builtin_imports.get("perform_single_value_operation")
        if perform_op:
            return perform_op(val, expr.operator)
        return GulfOfMexicoUndefined()

    def enable_caching(self, enabled: bool = True) -> None:
        """Enable or disable expression result caching."""
        self.cache.enabled = enabled

    def get_stats(self) -> Dict[str, Any]:
        """Get handler statistics including cache performance."""
        return {
            "total_evaluations": self.eval_count,
            "cache": self.cache.get_stats(),
        }

    def get_debug_info(self) -> str:
        """Get debug information about expression handler state."""
        cache_stats = self.cache.get_stats()
        return (
            f"ExpressionHandler Debug Info:\n"
            f"  Total Evaluations: {self.eval_count}\n"
            f"  Cache Enabled: {cache_stats['enabled']}\n"
            f"  Cache Size: {cache_stats['size']}/{cache_stats['max_size']}\n"
            f"  Cache Hit Rate: {cache_stats['hit_rate']}\n"
            f"  Total Accesses: {cache_stats['total_accesses']}\n"
        )
