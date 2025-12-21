# Phase 4 Task 2 Detailed Implementation Guide

## Overview

Task 2 integrates the 10 registered handlers into the production interpreter's statement dispatch system in `interpret_code_statements()`.

## Current State

- ✅ All 10 handlers registered in `create_production_registry()`
- ✅ Handler initialization code added to interpreter.py
- ⏳ Statement dispatch needs integration

## Implementation Strategy

### Why This Approach?

The handlers require dependency injection of interpreter functions. Rather than modifying 3,466+ lines of interpreter.py immediately, we:

1. **Keep existing pattern matching intact** - ensures backwards compatibility
2. **Add handler dispatch attempt BEFORE match** - handlers are tried first
3. **Fall back to legacy code** if handler unavailable
4. **Gradually migrate handlers** - start with simple ones

### Key Technical Decisions

1. **Don't remove existing code yet** - Phase 5 will be cleanup
2. **Inject dependencies via helper** - minimize changes to handlers
3. **Use logging to track usage** - understand which handlers are being called
4. **Preserve exact same execution semantics** - no behavioral changes

## Implementation Steps

### Step 1: Create Handler Dispatcher Helper

Create a new helper function in interpreter.py that:

```python
def execute_with_handler_if_available(
    statement: CodeStatement,
    context: ExecutionContext,
) -> tuple[bool, Optional[GulfOfMexicoValue]]:
    """Try to execute statement using registered handler.
    
    Returns:
        (handled, result) - True if handler executed, False if should use legacy
    """
```

This function:
- Gets the handler registry
- Tries to find handler for statement type  
- Injects required interpreter functions
- Handles errors gracefully
- Returns (True, result) if handler executed
- Returns (False, None) if no handler (fallback to legacy)

### Step 2: Inject Interpreter Dependencies

Create a setup function that gives handlers access to:
- `evaluate_expression` - core expression evaluator
- `raise_error_at_line` - error reporting
- `print_expression_debug` - debug output
- Other helpers as needed

### Step 3: Modify interpret_code_statements()

In the main loop, add handler dispatch:

```python
for statement_tuple in statements:
    statement = determine_statement_type(statement_tuple, namespaces)
    if statement is None:
        continue
    
    # Try handler-based execution first
    handled, result = execute_with_handler_if_available(...)
    if handled:
        return result  # Handler executed successfully
    
    # Fall back to legacy pattern matching
    match statement:
        # ... existing code ...
```

### Step 4: Test Incrementally

#### Phase 1: Test Simple Handlers
- ReturnStatement (returns immediately, no side effects)
- VariableDeclaration (well-tested)
- ExpressionStatement (simple)

#### Phase 2: Expand to Control Flow
- Conditional (if statements)
- WhenStatement (reactive)

#### Phase 3: Complete Coverage
- All remaining handlers

## Handler Dependency Injection Matrix

| Handler | Dependencies | Complexity |
|---------|------------|-----------|
| ReturnStatement | evaluate_expr, raise_error | ★☆☆ |
| VariableDeclaration | evaluate_expr, declare_variable | ★☆☆ |
| VariableAssignment | evaluate_expr, assign_variable | ★☆☆ |
| ExpressionStatement | evaluate_expr | ★☆☆ |
| Conditional | evaluate_expr, execute_conditional | ★★☆ |
| WhenStatement | register_when_statement | ★★★ |
| ForLoop | loop logic, break/continue handling | ★★★ |
| FunctionDefinition | namespace management | ★★☆ |
| ClassDeclaration | namespace management | ★★☆ |
| AfterStatement | event registration | ★★☆ |

## Success Criteria

- [ ] Handler dispatcher function created and works
- [ ] ReturnStatement handler executes via handler path
- [ ] All existing tests still pass
- [ ] Program files run without errors
- [ ] Logging shows handler usage
- [ ] No performance regression
- [ ] Error handling works correctly
- [ ] Fallback to legacy code works

## File Changes Needed

### Modified Files
- `gulfofmexico/interpreter.py` - Add dispatcher, integrate into statement loop
- `gulfofmexico/handlers_impl/*.py` - May need small adjustments
- Tests may need updates to verify handler path

### New Files
- None needed - integration is within existing files

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Break existing functionality | Keep legacy code intact, fallback mechanism |
| Performance regression | Minimal overhead from handler lookup |
| Circular imports | Lazy initialization already implemented |
| Missing dependencies | Error handling in dispatcher |
| Incompatible handler code | Test incrementally, verify each handler |

## Timeline Estimate

- Dispatcher function: 1-2 hours
- Dependency injection setup: 30-60 minutes
- integrate into interpret_code_statements: 1-1.5 hours
- Testing & validation: 2-3 hours

**Total**: 4-7 hours (within 2-3 hour estimate buffer)

## Next Steps After Task 2

- Task 3: Run full integration tests
- Task 4: Performance benchmarking
- Task 5: Legacy code cleanup (remove pattern matching)
- Task 6: Final validation

---

## Implementation Checklist

- [ ] Create `execute_with_handler_if_available()` function
- [ ] Create dependency injection helper
- [ ] Update `interpret_code_statements()` main loop
- [ ] Test with ReturnStatement
- [ ] Test with VariableDeclaration
- [ ] Test with Conditional
- [ ] Verify all existing tests pass
- [ ] Document findings in PHASE_4_PROGRESS.md
- [ ] Commit changes to git

