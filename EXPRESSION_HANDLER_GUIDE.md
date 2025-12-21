# ExpressionHandler Technical Guide

**Complete reference for ExpressionHandler implementation, usage, and integration.**

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Reference](#api-reference)
4. [Usage Examples](#usage-examples)
5. [Integration Guide](#integration-guide)
6. [Performance Optimization](#performance-optimization)
7. [Troubleshooting](#troubleshooting)

## Overview

### Purpose

`ExpressionHandler` is a modular statement handler that encapsulates all expression evaluation logic from the monolithic interpreter. It:

- Evaluates all Gulf of Mexico expression types
- Provides optional performance caching
- Integrates with ExecutionContext for clean state management
- Supports reactive when-statement evaluation
- Enables independent testing and optimization

### Key Benefits

| Aspect | Benefit |
|--------|---------|
| **Modularity** | Expression evaluation isolated from other concerns |
| **Performance** | Optional caching for repeated expressions |
| **Testability** | Independent unit tests without full interpreter |
| **Maintainability** | Clear separation of concerns |
| **Extensibility** | Easy to add new expression types |

### Expression Types Supported

```
ExpressionTreeNode
├── FunctionNode          # func(), obj.method()
├── ListNode             # [1, 2, 3]
├── ValueNode            # x, "string", 42
├── IndexNode            # list[0], dict[key]
├── ExpressionNode       # x + y, a && b
└── SingleOperatorNode   # -x, !a
```

## Architecture

### Class Hierarchy

```python
StatementHandler (ABC)
    ↓
ExpressionHandler
    └─ ExpressionCache
        └─ ExpressionCacheEntry
```

### State Management

```
ExpressionHandler
├── cache: ExpressionCache
│   ├── enabled: bool
│   ├── cache: Dict[str, ExpressionCacheEntry]
│   ├── hits: int
│   ├── misses: int
│   └── max_size: int
├── eval_count: int
└── builtin_imports: Dict[str, Callable]
```

### Execution Flow Diagram

```
Input: ExpressionTreeNode
    ↓
[can_handle() check]
    ↓
execute(expr, context)
    ├─ _evaluate_expression_impl()
    │   ├─ get_built_expression()
    │   └─ Pattern Match
    │       ├─ FunctionNode → _handle_function_call()
    │       │   ├─ Lookup function
    │       │   ├─ Handle keywords (await, previous, next)
    │       │   ├─ Evaluate arguments
    │       │   ├─ Handle dotted calls
    │       │   └─ Evaluate function
    │       ├─ ListNode → _handle_list()
    │       ├─ ValueNode → _handle_value()
    │       ├─ IndexNode → _handle_index()
    │       ├─ ExpressionNode → _handle_binary_operation()
    │       └─ SingleOperatorNode → _handle_unary_operation()
    ├─ Cache Check
    │   ├─ Hit → Return cached value
    │   └─ Miss → Evaluate and cache
    └─ Output: GulfOfMexicoValue
```

## API Reference

### ExpressionHandler

#### Constructor

```python
def __init__(self, cache_enabled: bool = False):
    """Initialize expression handler.
    
    Args:
        cache_enabled: Enable expression result caching (default: False)
    """
```

**Parameters**:
- `cache_enabled` (bool): Optional caching for performance

**Example**:
```python
# Without caching (safe default)
handler = ExpressionHandler()

# With caching for performance
handler = ExpressionHandler(cache_enabled=True)
```

#### Methods

##### `set_interpreter_imports(imports: Dict[str, Callable]) -> None`

Set references to interpreter functions needed for evaluation.

```python
handler.set_interpreter_imports({
    "get_built_expression": interpreter.get_built_expression,
    "evaluate_escape_sequences": interpreter.evaluate_escape_sequences,
    # ... 13 more required imports
})
```

**Required Imports**:
```
get_built_expression
evaluate_escape_sequences
get_name_from_namespaces
get_value_from_namespaces
interpret_formatted_string
perform_two_value_operation
perform_single_value_operation
db_to_boolean
raise_error_at_line
raise_error_at_token
register_async_function
evaluate_normal_function
get_code_from_when_statement_watchers
execute_conditional
get_name_and_namespace_from_namespaces  # Optional
```

##### `can_handle(expr: ExpressionTreeNode) -> bool`

Check if handler can evaluate an expression type.

```python
if handler.can_handle(expr_node):
    result = handler.execute(expr_node, ctx)
```

**Returns**: `True` for any valid expression type

##### `execute(expr: ExpressionTreeNode, context: ExecutionContext) -> GulfOfMexicoValue`

Evaluate expression in execution context.

```python
result = handler.execute(expr_node, context)
```

**Parameters**:
- `expr`: Expression tree node to evaluate
- `context`: ExecutionContext with namespaces and state

**Returns**: Evaluated GulfOfMexicoValue

**Raises**: RuntimeError on evaluation errors (if imports missing)

##### `enable_caching(enabled: bool = True) -> None`

Enable or disable expression caching at runtime.

```python
handler.enable_caching(True)   # Enable
handler.enable_caching(False)  # Disable
```

##### `get_stats() -> Dict[str, Any]`

Get handler statistics including cache performance.

```python
stats = handler.get_stats()
# {
#   'total_evaluations': 1250,
#   'cache': {
#       'enabled': True,
#       'size': 342,
#       'max_size': 1000,
#       'hits': 950,
#       'misses': 300,
#       'hit_rate': '76.0%',
#       'total_accesses': 1250
#   }
# }
```

##### `get_debug_info() -> str`

Get detailed debug information about handler state.

```python
info = handler.get_debug_info()
print(info)
# ExpressionHandler Debug Info:
#   Total Evaluations: 1250
#   Cache Enabled: True
#   Cache Size: 342/1000
#   Cache Hit Rate: 76.0%
#   Total Accesses: 1250
```

### ExpressionCache

#### Constructor

```python
def __init__(self, enabled: bool = False, max_size: int = 1000):
    """Initialize expression cache.
    
    Args:
        enabled: Whether caching is enabled (default: False)
        max_size: Maximum number of cached expressions (default: 1000)
    """
```

#### Methods

##### `get(key: str) -> Optional[GulfOfMexicoValue]`

Retrieve cached expression result.

```python
result = cache.get("expr_key")
if result is not None:
    # Cache hit
    return result
else:
    # Cache miss - evaluate and set
    result = evaluate_expression()
    cache.set("expr_key", result)
```

##### `set(key: str, value: GulfOfMexicoValue, dependencies: set[str] = None) -> None`

Cache expression result with optional dependency tracking.

```python
cache.set("x + y", result, dependencies={"x", "y"})
```

**Parameters**:
- `key`: Cache key (typically expression hash)
- `value`: Evaluated result to cache
- `dependencies`: Set of variable names used in expression

##### `invalidate(dependency: str) -> None`

Invalidate all cache entries depending on a variable.

```python
cache.invalidate("x")  # Clear all expressions using x
```

##### `clear() -> None`

Clear entire cache and reset statistics.

```python
cache.clear()  # Reset for new evaluation context
```

##### `get_stats() -> Dict[str, Any]`

Get cache performance statistics.

```python
stats = cache.get_stats()
print(f"Hit Rate: {stats['hit_rate']}")
```

**Returns**:
```python
{
    'enabled': bool,
    'size': int,
    'max_size': int,
    'hits': int,
    'misses': int,
    'hit_rate': str,  # Formatted percentage
    'total_accesses': int
}
```

## Usage Examples

### Basic Expression Evaluation

```python
from gulfofmexico.handlers_impl.expression import ExpressionHandler
from gulfofmexico.context import ExecutionContext
from gulfofmexico.processor.syntax_tree import ValueNode, Token, TokenType

# Initialize
handler = ExpressionHandler()
ctx = ExecutionContext.create_root("test.gom", "x = 42")

# Create simple value expression
expr = ValueNode(
    name_or_value=Token(TokenType.NAME, "x", 1, 1)
)

# Evaluate (requires interpreter imports to be set)
try:
    result = handler.execute(expr, ctx)
    print(f"Result: {result}")
except RuntimeError as e:
    print(f"Imports not set: {e}")
```

### Function Call Evaluation

```python
from gulfofmexico.processor.syntax_tree import FunctionNode

# Function call expression: len([1, 2, 3])
func_expr = FunctionNode(
    name=Token(TokenType.NAME, "len", 1, 1),
    args=[
        ListNode(values=[
            ValueNode(Token(TokenType.NUMBER, "1", 1, 5)),
            ValueNode(Token(TokenType.NUMBER, "2", 1, 8)),
            ValueNode(Token(TokenType.NUMBER, "3", 1, 11)),
        ])
    ]
)

# With imports set
handler.set_interpreter_imports(imports_dict)
result = handler.execute(func_expr, ctx)
```

### Cache Performance Example

```python
# Create handler with caching
handler = ExpressionHandler(cache_enabled=True)
handler.set_interpreter_imports(imports)

# Evaluate same expression multiple times
expr = create_expression("x + 1")

# First evaluation - cache miss
result1 = handler.execute(expr, ctx)

# Second evaluation - cache hit
result2 = handler.execute(expr, ctx)

# Check performance
stats = handler.get_stats()
print(f"Cache Hit Rate: {stats['cache']['hit_rate']}")
# Cache Hit Rate: 50.0%  (1 hit, 1 miss)
```

### Cache Invalidation Pattern

```python
cache = handler.cache

# Track which variables expressions depend on
cache.set("x + y", result1, dependencies={"x", "y"})
cache.set("x * 2", result2, dependencies={"x"})
cache.set("z + 1", result3, dependencies={"z"})

# When x changes, invalidate dependent expressions
cache.invalidate("x")

# Now cache contains only z + 1
assert cache.get("x + y") is None
assert cache.get("x * 2") is None
assert cache.get("z + 1") is not None
```

### Integration with ExecutionContext

```python
from gulfofmexico.execution_context import ExecutionContext

# Create context with state
ctx = ExecutionContext.create_root("file.gom", code)

# Add variables to namespace
var = Variable("x", [], [])
var.add_lifetime(GulfOfMexicoNumber(42), 0, 1000, True, True)
ctx.set_variable("x", GulfOfMexicoNumber(42))

# Evaluate expressions in context
expr = ValueNode(Token(TokenType.NAME, "x", 1, 1))
result = handler.execute(expr, ctx)

# Result will be 42 from the context
assert result.value == 42
```

## Integration Guide

### Step 1: Set Up Handler Registry

```python
from gulfofmexico.handler_registry import create_production_registry
from gulfofmexico.handlers_impl.expression import ExpressionHandler

# Create registry
registry = create_production_registry()

# Create expression handler (Phase 2)
expr_handler = ExpressionHandler(cache_enabled=True)

# Set interpreter imports (from your interpreter instance)
expr_handler.set_interpreter_imports({
    "get_built_expression": interpreter.get_built_expression,
    "evaluate_escape_sequences": interpreter.evaluate_escape_sequences,
    # ... rest of imports
})

# Register with fallback for unmigrated statement types
registry.set_fallback_handler(interpreter.evaluate_expression)
```

### Step 2: Use in Statement Execution

```python
# During statement execution
if isinstance(statement, SomeExpressionStatement):
    # Route through handler
    result = registry.execute_statement(statement, context)
else:
    # Falls back to original interpreter function
    result = fallback_handler(statement, context)
```

### Step 3: Gradual Migration

```python
# Phase 1: ParallelExecution (both methods work)
# Phase 2: SwitchableExecution (via handler flag)
# Phase 3: FullExecution (only handlers used)
# Phase 4: Cleanup (remove original code)

# You can enable/disable handlers per-type
registry.enable_handler_type("ExpressionHandler", True)
registry.disable_handler_type("ExpressionHandler", False)
```

## Performance Optimization

### Cache Tuning

```python
# For small programs: default cache
handler = ExpressionHandler()

# For large programs: larger cache
handler = ExpressionHandler(cache_enabled=True)
handler.cache.max_size = 5000  # Increase from default 1000

# For memory-constrained: smaller cache
handler = ExpressionHandler(cache_enabled=True)
handler.cache.max_size = 100
```

### Profiling Cache Effectiveness

```python
# Before optimization
handler.enable_caching(False)
result1 = profile_evaluation()  # Baseline

# After optimization
handler.enable_caching(True)
result2 = profile_evaluation()  # With cache

# Compare
improvement = (result1 - result2) / result1 * 100
print(f"Performance improvement: {improvement:.1f}%")
```

### Memory Impact

```python
# Estimate cache memory usage
import sys

stats = handler.cache.get_stats()
entry_size = sys.getsizeof(GulfOfMexicoValue())  # ~100 bytes
estimated_memory = stats['size'] * entry_size / 1024  # KB

print(f"Cache Memory: {estimated_memory:.1f} KB")
```

## Troubleshooting

### Issue: "Missing get_built_expression import"

**Cause**: `set_interpreter_imports()` not called

**Solution**:
```python
handler.set_interpreter_imports(imports_dict)
# Before calling execute()
```

### Issue: "Cannot find token in namespace"

**Cause**: Variable or function not defined in context

**Check**:
```python
# Verify variable exists in context
var = ctx.get_variable("var_name")
if var is None:
    ctx.set_variable("var_name", GulfOfMexicoNumber(42))
```

### Issue: "Cache hit rate is 0%"

**Cause**: Expressions are not repeated or cache is disabled

**Solution**:
```python
# Verify cache is enabled
assert handler.cache.enabled is True

# Check if expressions repeat in your program
stats = handler.get_stats()
if stats['cache']['total_accesses'] < 100:
    # Few accesses - cache may not help
    handler.enable_caching(False)
```

### Issue: "Memory usage increasing"

**Cause**: Cache growing without bounds

**Solution**:
```python
# Check cache size
stats = handler.cache.get_stats()
print(f"Cache entries: {stats['size']}/{stats['max_size']}")

# Clear periodically
handler.cache.clear()

# Or reduce max size
handler.cache.max_size = 500
```

### Issue: "Async functions not executing"

**Cause**: Missing `register_async_function` import

**Check**:
```python
imports = {
    "register_async_function": interpreter.register_async_function,
    # ... other imports
}
handler.set_interpreter_imports(imports)
```

## Advanced Topics

### Custom Cache Keys

For optimal cache hits, expressions need consistent hashing:

```python
# Bad: Different hash for equivalent expressions
expr1 = "x + y"
expr2 = "y + x"
# Different keys → No cache hit

# Good: Normalize expressions
expr_key = normalize_expression(expr)
cache.set(expr_key, result)
```

### Thread Safety

Current implementation is single-threaded. For multi-threaded use:

```python
import threading

# Create separate handler per thread
handler_per_thread = threading.local()

def get_handler():
    if not hasattr(handler_per_thread, 'handler'):
        handler_per_thread.handler = ExpressionHandler(cache_enabled=True)
    return handler_per_thread.handler
```

### Dependency Tracking

Optimal performance requires tracking expression dependencies:

```python
# When caching, track what variables are used
expr_dependencies = extract_variable_references(expr)
cache.set(expr_key, result, dependencies=expr_dependencies)

# When variable changes, invalidate dependents
cache.invalidate("changed_var")
```

---

**Document Version**: 1.0  
**Last Updated**: December 21, 2025  
**Related Files**:
- PHASE_2_PROGRESS.md
- gulfofmexico/handlers_impl/expression.py
- tests/test_handlers.py
