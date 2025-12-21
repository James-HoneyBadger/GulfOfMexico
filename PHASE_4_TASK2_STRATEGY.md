# Phase 4 Task 2: Interpreter Integration Strategy

## Integration Approach

The interpreter.py has a large match statement in `interpret_code_statements()` that dispatches based on statement type. The integration will:

1. **Create a handler-based dispatch pathway** without removing existing code
2. **Start with 2-3 high-value handlers** (Variable Declaration, Return, Conditional)
3. **Verify these work** before expanding to others
4. **Keep fallback to legacy code** for safety

## Key Decisions

### Why Gradual Integration?
- Minimize risk of breaking existing functionality
- Allow testing of each handler independently
- Can verify backwards compatibility
- Easier to debug if issues arise

### Handler Registration
- All handlers already registered in create_production_registry()
- Handlers are dependency-injected with interpreter functions
- Each handler has proper error handling

### Dispatch Strategy
Create a new helper function `try_execute_with_handlers()` that:
1. Tries to find matching handler
2. Falls back to legacy pattern matching if handler not available
3. Logs which path was taken (handler vs legacy)

## Implementation Phases

### Phase 4.2.1: Create Handler Dispatch Helper
- New function: `execute_statement_with_handler_dispatch()`
- Wraps the handler registry
- Manages error handling and fallback

### Phase 4.2.2: Integrate Simple Handlers First
- ReturnStatement (has minimal dependencies)
- VariableDeclaration (well-tested)
- Conditional (well-tested)

### Phase 4.2.3: Expand to Other Handlers  
- WhenStatement
- FunctionDefinition
- Other handlers as needed

### Phase 4.2.4: Testing & Validation
- Run existing interpreter tests
- Run all programs in /programs directory
- Verify no regressions

## Handler Dependencies

Each handler needs access to interpreter functions via dependency injection:
- evaluate_expression
- declare_new_variable
- assign_variable
- execute_conditional
- register_when_statement
- execute_after_statement
- print_expression_debug

## Success Criteria for Task 2

1. ✓ Handlers can be called from interpreter
2. ✓ Statement dispatch works for at least 3 handlers
3. ✓ Fallback to legacy code works
4. ✓ Existing tests pass
5. ✓ Error handling is correct
