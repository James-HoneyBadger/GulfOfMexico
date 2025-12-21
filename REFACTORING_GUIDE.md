# Gulf of Mexico Interpreter Refactoring Guide

**Status**: In Progress - Critical Infrastructure Phase
**Last Updated**: December 21, 2025

## Overview

This document tracks the systematic refactoring of the monolithic interpreter (3,466 lines in `interpreter.py`) into a modular, maintainable handler-based architecture.

## Motivation

**Problem**: The single `interpret_code_statements()` function uses pattern matching with 1000+ lines of nested match statements, making:
- Code difficult to test (can't test individual statement types in isolation)
- Bugs hard to locate (entire control flow must be understood)
- Contributions challenging (new statement types require understanding all logic)
- Performance optimization difficult (can't optimize per-statement-type)

**Solution**: Handler pattern + ExecutionContext class

## Architecture

### 1. Handler Pattern
Each statement type gets its own handler implementing `StatementHandler`:

```python
class StatementHandler(ABC):
    def can_handle(self, statement: CodeStatement) -> bool
    def execute(self, statement: CodeStatement, context: ExecutionContext) -> Optional[GulfOfMexicoValue]
    @property
    def statement_type(self) -> Type[CodeStatement]
```

### 2. ExecutionContext Class
Replaces passing 10+ parameters through function calls:

```python
@dataclass
class ExecutionContext:
    """Complete execution context for handlers."""
    namespaces: list[Namespace]
    async_statements: AsyncStatements
    when_statement_watchers: WhenStatementWatchers  # Or use WatcherRegistry
    filename: str
    code: str
    current_line: int
    importable_names: dict
    exported_names: list
    deleted_values: set
    
    # Helpers
    def get_variable(self, name: str) -> Optional[Union[Variable, Name]]
    def set_variable(self, name: str, value: GulfOfMexicoValue)
    def push_scope(self) -> None
    def pop_scope(self) -> None
```

### 3. WatcherManager
Replaces tuple-based when-statement watchers:

```python
registry = WatcherRegistry()
watcher_id = registry.register_watcher(
    variable_id=id(my_var),
    condition=expr,
    code=statements,
    captured_namespaces=namespaces
)
to_execute = registry.trigger_watchers(variable_id, evaluator_func)
```

## Implementation Plan

### Phase 1: Core Infrastructure ✅ STARTED

- [x] Create `handlers_impl/` package structure
- [x] Extract `VariableDeclarationHandler` 
- [x] Extract `VariableAssignmentHandler`
- [x] Create `WatcherManager` for when-statement refactoring
- [ ] Create `ExecutionContext` dataclass
- [ ] Create handler factory/registry

### Phase 2: Handler Extraction (Planned)

Statement handlers to extract:
- [ ] `ExpressionStatementHandler` - Evaluate and print expressions
- [ ] `ReturnStatementHandler` - Handle return statements  
- [ ] `ConditionalHandler` - Handle if statements
- [ ] `WhenStatementHandler` - Handle when (reactive) statements
- [ ] `AfterStatementHandler` - Handle event listeners
- [ ] `FunctionDefinitionHandler` - Handle function definitions
- [ ] `ClassDeclarationHandler` - Handle class definitions
- [ ] `DeleteStatementHandler` - Handle variable deletion
- [ ] `ImportStatementHandler` - Handle imports/exports

### Phase 3: Caching & Performance

- [ ] Extract `ExpressionHandler` with built-in caching
- [ ] Benchmark pure expression evaluation
- [ ] Enable caching for suitable expressions

### Phase 4: Testing & Validation

- [ ] Unit tests for each handler
- [ ] Integration tests with ExecutionContext
- [ ] Regression tests against existing test suite
- [ ] Performance benchmarks

### Phase 5: Integration

- [ ] Dual-mode interpreter (handlers + fallback to pattern matching)
- [ ] Gradual migration of production code
- [ ] Complete deprecation of pattern matching paths

## File Structure

```
gulfofmexico/
├── handlers.py                 # Base classes (existing)
├── handlers_impl/              # NEW: Concrete handlers
│   ├── __init__.py
│   ├── variable_declaration.py
│   ├── variable_assignment.py
│   ├── expression_statement.py (planned)
│   ├── control_flow.py         (planned)
│   └── function_definitions.py (planned)
├── watcher_manager.py          # NEW: When-statement management
├── execution_context.py        # NEW: Unified context object
├── handler_registry.py         # NEW: Handler coordination
└── interpreter.py              # Existing (will be refactored)
```

## Key Design Decisions

### 1. ExecutionContext vs Parameter Explosion
**Decision**: Use `ExecutionContext` dataclass instead of passing 10+ parameters

**Rationale**:
- Cleaner handler signatures: `execute(statement, context)`
- Easier to add new state without changing all handlers
- Built-in debugging (can print context.get_debug_info())
- Enables context cloning for scope management

### 2. Handler Registration vs Manual Dispatch
**Decision**: Use `HandlerRegistry` with auto-discovery

**Rationale**:
- Plugins can register handlers dynamically
- New statement types don't require modifying dispatcher
- Handlers can be enabled/disabled at runtime

### 3. WatcherManager vs Tuple-Based System
**Decision**: Replace `dict[Union[str, int], list[tuple[...]]]` with `WatcherRegistry`

**Rationale**:
- Type-safe (can't accidentally construct wrong tuple)
- Deadlock detection built-in
- Execution tracking for debugging
- Clears up cognitive load (no need to memorize tuple structure)

### 4. Gradual Migration vs Big Rewrite
**Decision**: Support both handlers and pattern matching during transition

**Rationale**:
- Can test each handler independently
- Existing code continues working
- Can measure performance improvements incrementally
- Reduces risk of introducing bugs

## Testing Strategy

### Unit Tests
Each handler has its own test file:
```python
# tests/handlers/test_variable_declaration.py
class TestVariableDeclarationHandler:
    def test_simple_declaration()
    def test_const_var_modifiers()
    def test_lifetime_parsing()
    def test_type_annotations()
    def test_when_statement_triggering()
```

### Integration Tests
```python
# tests/test_handler_integration.py
class TestHandlerIntegration:
    def test_variable_lifecycle()
    def test_when_statement_with_assignment()
    def test_scope_management()
    def test_execution_context_cloning()
```

### Regression Tests
All existing programs in `programs/` directory continue to work.

## Migration Checklist

- [ ] Phase 1 handlers extraction complete
- [ ] ExecutionContext class created and tested
- [ ] Handler registry working with auto-dispatch
- [ ] WatcherManager integrated for when-statements
- [ ] Unit test suite with >90% coverage
- [ ] Integration tests passing
- [ ] All existing tests passing with handlers
- [ ] Performance benchmarks show no regression
- [ ] Documentation updated
- [ ] Code review and approval
- [ ] Merged to main branch

## Performance Targets

- **Build time**: No increase
- **Startup time**: <5% slower (due to handler registration)
- **Execution speed**: 0-5% improvement (due to better caching)
- **Memory usage**: No increase in typical cases
- **Test suite**: Runs 20-30% faster (smaller test units)

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Breaking changes | Dual-mode operation, extensive tests |
| Performance regression | Benchmarks before/after each change |
| Handler explosion | Composite handlers for related types |
| Context object too large | Split into concerns (VariableContext, AsyncContext) |
| Migration complexity | Start with expression handling (simpler) |

## Next Steps

1. **Immediate** (next session):
   - Complete WatcherManager implementation
   - Create ExecutionContext class
   - Implement handler registry

2. **Short term** (1-2 weeks):
   - Extract expression and control flow handlers
   - Create integration tests
   - Benchmark performance

3. **Medium term** (3-4 weeks):
   - Extract remaining handlers
   - Merge handlers into production code
   - Remove pattern matching code

## References

- Original handler base classes: `gulfofmexico/handlers.py`
- Experimental engine proof-of-concept: `gulfofmexico/engine/core.py`
- Current interpreter: `gulfofmexico/interpreter.py`
- When-statement implementation: Lines 2800-3100 in interpreter.py

## Questions & Notes

- Should ExecutionContext be mutable or immutable during handler execution?
  - **Answer**: Mutable (handlers need to modify namespaces), but with scope management
  
- How to handle exceptions in handlers?
  - **Answer**: Let them propagate, use try/whatever statements for error handling
  
- Should handlers be async-aware?
  - **Answer**: Yes, handlers should yield control to async_statements queue
  
- Can handlers have side effects?
  - **Answer**: Yes (they modify namespaces), unlike pure expressions
