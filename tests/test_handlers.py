"""
Test Suite for Handler System

Tests for the new handler-based architecture, ensuring correctness
before integrating into the production interpreter.

Test Organization:
    - test_execution_context.py: ExecutionContext behavior
    - test_variable_declaration_handler.py: Variable declaration handler
    - test_variable_assignment_handler.py: Variable assignment handler
    - test_watcher_manager.py: When-statement watcher management
    - test_handler_integration.py: Full integration tests
"""

import pytest
from typing import Optional, Union

from gulfofmexico.builtin import (
    GulfOfMexicoNumber,
    GulfOfMexicoString,
    GulfOfMexicoList,
    GulfOfMexicoBoolean,
    GulfOfMexicoUndefined,
    Name,
    Variable,
    VariableLifetime,
)
from gulfofmexico.execution_context import ExecutionContext
from gulfofmexico.watcher_manager import WatcherRegistry, Watcher


class TestExecutionContext:
    """Test ExecutionContext functionality."""

    def test_create_root_context(self):
        """Test creating a root execution context."""
        ctx = ExecutionContext.create_root("test.gom", "x = 5")
        assert ctx.filename == "test.gom"
        assert ctx.code == "x = 5"
        assert len(ctx.namespaces) == 1  # Global scope created
        assert len(ctx.when_statement_watchers) == 1

    def test_get_variable_simple_name(self):
        """Test getting a simple variable."""
        ctx = ExecutionContext.create_root()
        var = Variable("x", [], [])
        var.add_lifetime(GulfOfMexicoNumber(42), 0, 1000, True, True)
        ctx.get_current_namespace()["x"] = var

        retrieved = ctx.get_variable("x")
        assert retrieved == var

    def test_get_variable_undefined(self):
        """Test getting a non-existent variable."""
        ctx = ExecutionContext.create_root()
        assert ctx.get_variable("undefined") is None

    def test_set_variable_new(self):
        """Test setting a new variable."""
        ctx = ExecutionContext.create_root()
        value = GulfOfMexicoString("hello")

        ctx.set_variable("greeting", value, confidence=50)

        retrieved = ctx.get_variable("greeting")
        assert retrieved is not None
        assert isinstance(retrieved, Variable)
        assert retrieved.value == value

    def test_set_variable_existing(self):
        """Test updating an existing variable."""
        ctx = ExecutionContext.create_root()

        ctx.set_variable("x", GulfOfMexicoNumber(1))
        ctx.set_variable("x", GulfOfMexicoNumber(2))

        var = ctx.get_variable("x")
        assert isinstance(var, Variable)
        assert var.value == GulfOfMexicoNumber(2)

    def test_push_pop_scope(self):
        """Test scope management."""
        ctx = ExecutionContext.create_root()
        assert len(ctx.namespaces) == 1

        ctx.push_scope()
        assert len(ctx.namespaces) == 2

        ctx.pop_scope()
        assert len(ctx.namespaces) == 1

    def test_delete_variable(self):
        """Test variable deletion."""
        ctx = ExecutionContext.create_root()
        ctx.set_variable("temp", GulfOfMexicoNumber(99))

        assert ctx.get_variable("temp") is not None
        deleted = ctx.delete_variable("temp")
        assert deleted is True
        assert ctx.get_variable("temp") is None

    def test_clone_for_scope(self):
        """Test context cloning."""
        ctx = ExecutionContext.create_root("test.gom", "code")
        ctx.set_variable("x", GulfOfMexicoNumber(1))

        cloned = ctx.clone_for_scope()
        assert cloned.filename == ctx.filename
        assert len(cloned.namespaces) == len(ctx.namespaces)

        # Modifying clone doesn't affect original
        cloned.set_variable("x", GulfOfMexicoNumber(2))
        assert ctx.get_variable("x").value == GulfOfMexicoNumber(1)

    def test_debug_info(self):
        """Test debug information generation."""
        ctx = ExecutionContext.create_root()
        ctx.set_variable("x", GulfOfMexicoNumber(42))

        debug = ctx.get_debug_info()
        assert "ExecutionContext Debug Info" in debug
        assert "x" in debug


class TestWatcherManager:
    """Test WatcherManager functionality."""

    def test_register_watcher(self):
        """Test registering a watcher."""
        registry = WatcherRegistry()
        var_id = id({"x": 1})

        watcher_id = registry.register_watcher(
            variable_id=var_id,
            condition=None,  # Would be ExpressionTreeNode in real use
            code=[],
            captured_namespaces=[],
        )

        assert watcher_id >= 0
        watchers = registry.get_watchers(var_id)
        assert len(watchers) == 1

    def test_get_watchers_not_found(self):
        """Test getting watchers for non-existent variable."""
        registry = WatcherRegistry()
        watchers = registry.get_watchers(999999)
        assert watchers == []

    def test_unregister_watcher(self):
        """Test unregistering a watcher."""
        registry = WatcherRegistry()
        var_id = id({"x": 1})

        watcher_id = registry.register_watcher(
            variable_id=var_id,
            condition=None,
            code=[],
            captured_namespaces=[],
        )

        assert len(registry.get_watchers(var_id)) == 1
        removed = registry.unregister_watcher(watcher_id)
        assert removed is True
        assert len(registry.get_watchers(var_id)) == 0

    def test_clear_watchers(self):
        """Test clearing all watchers for a variable."""
        registry = WatcherRegistry()
        var_id = id({"x": 1})

        # Register multiple watchers
        for i in range(3):
            registry.register_watcher(
                variable_id=var_id,
                condition=None,
                code=[],
                captured_namespaces=[],
            )

        assert len(registry.get_watchers(var_id)) == 3
        cleared = registry.clear_watchers(var_id)
        assert cleared == 3
        assert len(registry.get_watchers(var_id)) == 0

    def test_get_stats(self):
        """Test statistics collection."""
        registry = WatcherRegistry()
        var_id1 = id({"x": 1})
        var_id2 = id({"y": 2})

        registry.register_watcher(var_id1, None, [], [])
        registry.register_watcher(var_id1, None, [], [])
        registry.register_watcher(var_id2, None, [], [])

        stats = registry.get_stats()
        assert stats["total_watchers"] == 3
        assert stats["active_watchers"] == 3
        assert stats["variables_watched"] == 2

    def test_mark_watcher_executing(self):
        """Test marking watcher as executing."""
        registry = WatcherRegistry()
        var_id = id({})

        watcher_id = registry.register_watcher(var_id, None, [], [])
        registry.mark_watcher_executing(watcher_id)

        assert watcher_id in registry._active_executions

        registry.mark_watcher_done(watcher_id)
        assert watcher_id not in registry._active_executions


class TestVariableDeclarationHandler:
    """Test VariableDeclarationHandler."""

    def test_handler_can_recognize_declarations(self):
        """Test that handler recognizes variable declarations."""
        from gulfofmexico.handlers_impl.variable_declaration import (
            VariableDeclarationHandler,
        )
        from gulfofmexico.processor.syntax_tree import VariableDeclaration
        from gulfofmexico.base import Token, TokenType

        handler = VariableDeclarationHandler()
        name_token = Token(TokenType.NAME, "x", 1, 0)
        stmt = VariableDeclaration(
            name=name_token,
            expression=[],
            confidence=0,
            lifetime=None,
            modifiers=[Token(TokenType.NAME, "const", 1, 0)],
            type_annotation=None,
            debug=0,
        )

        assert handler.can_handle(stmt)

    def test_handler_rejects_non_declarations(self):
        """Test that handler rejects non-declarations."""
        from gulfofmexico.handlers_impl.variable_declaration import (
            VariableDeclarationHandler,
        )
        from gulfofmexico.processor.syntax_tree import ExpressionStatement
        from gulfofmexico.base import Token, TokenType

        handler = VariableDeclarationHandler()
        stmt = ExpressionStatement(expression=[], debug=0)

        assert not handler.can_handle(stmt)


# Integration tests would go in test_handler_integration.py
class TestHandlerIntegration:
    """Integration tests for the handler system."""

    def test_variable_lifecycle(self):
        """Test complete variable declaration and assignment lifecycle."""
        # This would use both VariableDeclarationHandler and VariableAssignmentHandler
        # in sequence with ExecutionContext
        pass

    def test_when_statement_with_assignment(self):
        """Test when-statement triggering on variable assignment."""
        # This would test WatcherManager with actual variable changes
        pass

    def test_scope_management_with_handlers(self):
        """Test scope entry/exit with handlers."""
        # This would test push/pop scope with variable resolution
        pass


class TestExpressionHandler:
    """Test ExpressionHandler functionality."""

    def test_handler_can_recognize_expressions(self):
        """Test that handler recognizes expression types."""
        from gulfofmexico.handlers_impl.expression import ExpressionHandler
        from gulfofmexico.processor.syntax_tree import (
            FunctionNode,
            ListNode,
            ValueNode,
            IndexNode,
            ExpressionNode,
            SingleOperatorNode,
            Token,
            TokenType,
        )
        
        handler = ExpressionHandler()
        
        # Test function node recognition
        func_node = FunctionNode(
            name=Token(TokenType.NAME, "func", 1, 1),
            args=[]
        )
        assert handler.can_handle(func_node)
        
        # Test list node recognition
        list_node = ListNode(values=[])
        assert handler.can_handle(list_node)
        
        # Test value node recognition
        value_node = ValueNode(
            name_or_value=Token(TokenType.NUMBER, "42", 1, 1)
        )
        assert handler.can_handle(value_node)

    def test_expression_cache_basic_operations(self):
        """Test basic expression cache operations."""
        from gulfofmexico.handlers_impl.expression import ExpressionCache
        
        cache = ExpressionCache(enabled=True, max_size=10)
        
        # Test cache miss
        assert cache.get("key1") is None
        assert cache.misses == 1
        
        # Test cache set and get
        value = GulfOfMexicoNumber(42)
        cache.set("key1", value)
        assert cache.get("key1") == value
        assert cache.hits == 1

    def test_expression_cache_invalidation(self):
        """Test cache invalidation based on dependencies."""
        from gulfofmexico.handlers_impl.expression import ExpressionCache
        
        cache = ExpressionCache(enabled=True)
        
        # Add entries with dependencies
        val1 = GulfOfMexicoNumber(42)
        val2 = GulfOfMexicoNumber(100)
        
        cache.set("expr1", val1, dependencies={"x"})
        cache.set("expr2", val2, dependencies={"y"})
        
        # Invalidate dependency x
        cache.invalidate("x")
        
        # expr1 should be cleared, expr2 should remain
        assert cache.get("expr1") is None
        assert cache.get("expr2") == val2

    def test_expression_cache_statistics(self):
        """Test cache statistics collection."""
        from gulfofmexico.handlers_impl.expression import ExpressionCache
        
        cache = ExpressionCache(enabled=True)
        
        # Generate some hits and misses
        cache.get("key1")  # miss
        cache.set("key1", GulfOfMexicoNumber(42))
        cache.get("key1")  # hit
        cache.get("key1")  # hit
        
        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert "hit_rate" in stats

    def test_expression_cache_max_size(self):
        """Test cache respects max_size limit."""
        from gulfofmexico.handlers_impl.expression import ExpressionCache
        
        cache = ExpressionCache(enabled=True, max_size=3)
        
        # Fill cache to max size
        for i in range(3):
            cache.set(f"key{i}", GulfOfMexicoNumber(i))
        
        assert len(cache.cache) == 3
        
        # Add one more - should evict oldest
        cache.set("key3", GulfOfMexicoNumber(3))
        assert len(cache.cache) == 3  # Still at max

    def test_expression_handler_statistics(self):
        """Test expression handler statistics collection."""
        from gulfofmexico.handlers_impl.expression import ExpressionHandler
        
        handler = ExpressionHandler(cache_enabled=False)
        
        # Handler should track evaluation counts
        assert handler.eval_count == 0
        
        stats = handler.get_stats()
        assert "total_evaluations" in stats
        assert "cache" in stats
        assert stats["cache"]["enabled"] is False

    def test_expression_handler_caching_toggle(self):
        """Test toggling expression handler caching."""
        from gulfofmexico.handlers_impl.expression import ExpressionHandler
        
        handler = ExpressionHandler(cache_enabled=False)
        assert handler.cache.enabled is False
        
        handler.enable_caching(True)
        assert handler.cache.enabled is True
        
        handler.enable_caching(False)
        assert handler.cache.enabled is False

    def test_expression_handler_debug_info(self):
        """Test expression handler debug information."""
        from gulfofmexico.handlers_impl.expression import ExpressionHandler
        
        handler = ExpressionHandler()
        debug_info = handler.get_debug_info()
        
        assert "ExpressionHandler Debug Info" in debug_info
        assert "Total Evaluations" in debug_info
        assert "Cache" in debug_info

    def test_expression_handler_interpreter_imports(self):
        """Test setting interpreter imports."""
        from gulfofmexico.handlers_impl.expression import ExpressionHandler
        
        handler = ExpressionHandler()
        
        # Create mock imports
        imports = {
            "get_built_expression": lambda x: x,
            "evaluate_escape_sequences": lambda x: x,
            "get_name_from_namespaces": lambda n, ns: None,
        }
        
        handler.set_interpreter_imports(imports)
        
        assert "get_built_expression" in handler.builtin_imports
        assert handler.builtin_imports["evaluate_escape_sequences"] is not None


class TestPhase2Integration:
    """Integration tests for Phase 2 handlers and caching."""

    def test_handler_registry_with_expression_handler(self):
        """Test handler registry integration with ExpressionHandler."""
        from gulfofmexico.handler_registry import create_production_registry
        from gulfofmexico.handlers_impl.expression import ExpressionHandler
        
        registry = create_production_registry()
        expr_handler = ExpressionHandler(cache_enabled=True)
        
        # Handler should be properly initialized
        assert expr_handler.cache.enabled is True
        assert expr_handler.eval_count == 0

    def test_cache_efficiency_tracking(self):
        """Test cache efficiency improves with reused expressions."""
        from gulfofmexico.handlers_impl.expression import ExpressionCache
        
        cache = ExpressionCache(enabled=True)
        val = GulfOfMexicoNumber(42)
        
        # Simulate expression evaluation pattern
        for _ in range(10):
            result = cache.get("common_expr")
            if result is None:
                cache.set("common_expr", val)
        
        stats = cache.get_stats()
        # Should have multiple hits from repeated get calls
        assert stats["hits"] > 0

    def test_variable_lifetime_with_expression_handler(self):
        """Test variable lifetimes interact correctly with expression evaluation."""
        ctx = ExecutionContext.create_root("test.gom", "")
        
        # Create variable with lifetime
        var = Variable("x", [], [])
        var.add_lifetime(GulfOfMexicoNumber(42), 0, 100, True, True)
        
        ctx.get_current_namespace()["x"] = var
        
        # Variable should be retrievable
        retrieved = ctx.get_variable("x")
        assert isinstance(retrieved, Variable)


class TestReturnStatementHandler:
    """Test ReturnStatementHandler functionality."""

    def test_handler_can_recognize_return_statements(self):
        """Test that handler recognizes return statements."""
        from gulfofmexico.handlers_impl.return_statement import ReturnStatementHandler
        from gulfofmexico.processor.syntax_tree import Token, TokenType
        
        handler = ReturnStatementHandler()
        
        # Create return statement
        return_stmt = ReturnStatement(
            keyword=Token(TokenType.KEYWORD, "return", 1, 1),
            expression=[Token(TokenType.NUMBER, "42", 1, 8)],
            debug=0
        )
        
        assert handler.can_handle(return_stmt)

    def test_return_statement_statistics(self):
        """Test return statement handler statistics."""
        from gulfofmexico.handlers_impl.return_statement import ReturnStatementHandler
        
        handler = ReturnStatementHandler()
        
        # Handler should track return count
        assert handler.return_count == 0
        
        stats = handler.get_stats()
        assert "total_returns" in stats
        assert stats["total_returns"] == 0

    def test_return_statement_debug_info(self):
        """Test return statement handler debug information."""
        from gulfofmexico.handlers_impl.return_statement import ReturnStatementHandler
        
        handler = ReturnStatementHandler()
        debug_info = handler.get_debug_info()
        
        assert "ReturnStatementHandler Debug Info" in debug_info
        assert "Total Return Statements" in debug_info

    def test_return_statement_interpreter_imports(self):
        """Test setting interpreter imports for return handler."""
        from gulfofmexico.handlers_impl.return_statement import ReturnStatementHandler
        
        handler = ReturnStatementHandler()
        
        # Create mock imports
        imports = {
            "evaluate_expression": lambda e, ns, asyncs, watchers: GulfOfMexicoNumber(42),
            "raise_error_at_line": lambda f, c, l, msg: None,
        }
        
        handler.set_interpreter_imports(imports)
        
        assert "evaluate_expression" in handler.builtin_imports
        assert handler.builtin_imports["raise_error_at_line"] is not None

    def test_return_statement_with_promise(self):
        """Test return statement resolves promise correctly."""
        from gulfofmexico.handlers_impl.return_statement import ReturnStatementHandler
        from gulfofmexico.processor.syntax_tree import Token, TokenType
        
        handler = ReturnStatementHandler()
        ctx = ExecutionContext.create_root("test.gom", "return 42")
        
        # Create promise to resolve
        promise = GulfOfMexicoPromise(None)
        
        # Create return statement
        return_stmt = ReturnStatement(
            keyword=Token(TokenType.KEYWORD, "return", 1, 1),
            expression=[Token(TokenType.NUMBER, "42", 1, 8)],
            debug=0
        )
        
        # Set up mock imports
        handler.set_interpreter_imports({
            "evaluate_expression": lambda e, ns, asyncs, watchers: GulfOfMexicoNumber(42),
            "raise_error_at_line": lambda f, c, l, msg: None,
        })
        
        # Execute return statement
        result = handler.execute(return_stmt, ctx, promise)
        
        # Promise should be resolved
        assert promise.value is not None
        assert isinstance(result, GulfOfMexicoValue)

    def test_return_statement_without_promise_raises_error(self):
        """Test return statement raises error without promise context."""
        from gulfofmexico.handlers_impl.return_statement import ReturnStatementHandler
        from gulfofmexico.processor.syntax_tree import Token, TokenType
        
        handler = ReturnStatementHandler()
        ctx = ExecutionContext.create_root("test.gom", "return 42")
        
        # Create return statement
        return_stmt = ReturnStatement(
            keyword=Token(TokenType.KEYWORD, "return", 1, 1),
            expression=[Token(TokenType.NUMBER, "42", 1, 8)],
            debug=0
        )
        
        # Set up mock imports
        handler.set_interpreter_imports({
            "evaluate_expression": lambda e, ns, asyncs, watchers: GulfOfMexicoNumber(42),
            "raise_error_at_line": lambda f, c, l, msg: None,
        })
        
        # Should raise error when no promise provided
        with pytest.raises(RuntimeError, match="Return statement outside function context"):
            handler.execute(return_stmt, ctx, promise=None)

    def test_return_handler_factory_function(self):
        """Test return handler factory function."""
        from gulfofmexico.handlers_impl.return_statement import create_return_handler
        
        handler = create_return_handler()
        
        assert handler is not None
        assert handler.return_count == 0


class TestConditionalHandler:
    """Test ConditionalHandler functionality."""

    def test_handler_can_recognize_conditionals(self):
        """Test that handler recognizes conditional statements."""
        from gulfofmexico.handlers_impl.conditional import ConditionalHandler
        from gulfofmexico.processor.syntax_tree import Token, TokenType, Conditional
        
        handler = ConditionalHandler()
        
        # Create conditional statement
        cond = Conditional(
            keyword=Token(TokenType.KEYWORD, "if", 1, 1),
            expression=[Token(TokenType.NAME, "x", 1, 4)],
            code=[]
        )
        
        assert handler.can_handle(cond)

    def test_conditional_handler_statistics(self):
        """Test conditional handler statistics tracking."""
        from gulfofmexico.handlers_impl.conditional import ConditionalHandler
        
        handler = ConditionalHandler()
        
        # Handler should track conditional count
        assert handler.conditional_count == 0
        
        stats = handler.get_stats()
        assert "total_conditionals" in stats
        assert stats["total_conditionals"] == 0

    def test_conditional_handler_debug_info(self):
        """Test conditional handler debug information."""
        from gulfofmexico.handlers_impl.conditional import ConditionalHandler
        
        handler = ConditionalHandler()
        debug_info = handler.get_debug_info()
        
        assert "ConditionalHandler Debug Info" in debug_info
        assert "Total Conditional Statements" in debug_info

    def test_conditional_handler_interpreter_imports(self):
        """Test setting interpreter imports for conditional handler."""
        from gulfofmexico.handlers_impl.conditional import ConditionalHandler
        
        handler = ConditionalHandler()
        
        # Create mock imports
        imports = {
            "evaluate_expression": lambda e, ns, asyncs, watchers: GulfOfMexicoBoolean(True),
            "db_to_boolean": lambda v: GulfOfMexicoBoolean(True),
            "interpret_code_statements": lambda s, ns, a, w, i, e: None,
        }
        
        handler.set_interpreter_imports(imports)
        
        assert "evaluate_expression" in handler.builtin_imports
        assert "db_to_boolean" in handler.builtin_imports
        assert "interpret_code_statements" in handler.builtin_imports

    def test_conditional_determines_true_execution(self):
        """Test that true condition executes block."""
        from gulfofmexico.handlers_impl.conditional import ConditionalHandler
        
        handler = ConditionalHandler()
        
        # Mock the boolean converter
        from gulfofmexico.builtin import GulfOfMexicoBoolean
        true_value = GulfOfMexicoBoolean(True)
        
        ctx = ExecutionContext.create_root("test.gom", "if true { }")
        
        # Determine execution for true value
        should_execute = handler._determine_execution(true_value, ctx)
        
        assert should_execute is True

    def test_conditional_determines_false_execution(self):
        """Test that false condition skips block."""
        from gulfofmexico.handlers_impl.conditional import ConditionalHandler
        
        handler = ConditionalHandler()
        
        # Mock the boolean converter
        from gulfofmexico.builtin import GulfOfMexicoBoolean
        false_value = GulfOfMexicoBoolean(False)
        
        ctx = ExecutionContext.create_root("test.gom", "if false { }")
        
        # Set up imports to handle boolean conversion
        handler.set_interpreter_imports({
            "db_to_boolean": lambda v: GulfOfMexicoBoolean(False),
        })
        
        # Determine execution for false value
        should_execute = handler._determine_execution(false_value, ctx)
        
        assert should_execute is False

    def test_conditional_handler_factory_function(self):
        """Test conditional handler factory function."""
        from gulfofmexico.handlers_impl.conditional import create_conditional_handler
        
        handler = create_conditional_handler()
        
        assert handler is not None
        assert handler.conditional_count == 0


# ===== PHASE 3 WEEK 2: WHEN-STATEMENT, FOR-LOOP, WHILE-LOOP HANDLERS =====


class TestWhenStatementHandler:
    """Test suite for WhenStatementHandler."""

    def test_when_handler_recognition(self):
        """Test that handler recognizes when-statements."""
        from gulfofmexico.handlers_impl.when_statement import create_when_handler
        from gulfofmexico.base import WhenStatement, Token, ExpressionTreeNode

        handler = create_when_handler()
        mock_when = WhenStatement(
            expression=[],  # Empty expression list for testing
            code=[],  # Empty code for testing
        )

        assert handler.can_handle(mock_when)

    def test_when_handler_initialization(self):
        """Test when handler initializes with correct state."""
        from gulfofmexico.handlers_impl.when_statement import create_when_handler

        handler = create_when_handler()

        assert handler.execution_count == 0
        assert handler.triggered_count == 0
        assert len(handler.watchers_by_name) == 0

    def test_when_handler_stats(self):
        """Test when handler statistics tracking."""
        from gulfofmexico.handlers_impl.when_statement import create_when_handler

        handler = create_when_handler()
        handler.execution_count = 5
        handler.triggered_count = 3

        stats = handler.get_stats()

        assert stats["total_executions"] == 5
        assert stats["total_triggers"] == 3
        assert stats["total_watchers"] == 0

    def test_when_handler_debug_info(self):
        """Test when handler debug information."""
        from gulfofmexico.handlers_impl.when_statement import create_when_handler

        handler = create_when_handler()
        debug_info = handler.get_debug_info()

        assert "WhenStatementHandler" in debug_info
        assert "executed=0" in debug_info
        assert "triggered=0" in debug_info
        assert "watchers=0" in debug_info

    def test_when_handler_imports(self):
        """Test when handler validates required imports."""
        from gulfofmexico.handlers_impl.when_statement import create_when_handler
        from gulfofmexico.base import WhenStatement

        handler = create_when_handler()
        handler.builtin_imports = {}  # No imports set

        mock_when = WhenStatement(expression=[], code=[])
        context = ExecutionContext()

        with pytest.raises(RuntimeError, match="missing required import"):
            handler.execute(mock_when, context)

    def test_when_handler_factory(self):
        """Test when handler factory function."""
        from gulfofmexico.handlers_impl.when_statement import create_when_handler

        handler = create_when_handler()

        assert handler is not None
        assert handler.execution_count == 0
        assert handler.triggered_count == 0


class TestForLoopHandler:
    """Test suite for ForLoopHandler."""

    def test_for_loop_handler_recognition(self):
        """Test that handler recognizes for-loops."""
        from gulfofmexico.handlers_impl.for_loop import create_for_loop_handler
        from gulfofmexico.base import ForLoop, Name, Token

        handler = create_for_loop_handler()
        mock_for = ForLoop(
            variable=Name("x", None),
            iterable=[],  # Empty iterable for testing
            code=[],  # Empty code for testing
        )

        assert handler.can_handle(mock_for)

    def test_for_loop_handler_initialization(self):
        """Test for loop handler initializes with correct state."""
        from gulfofmexico.handlers_impl.for_loop import create_for_loop_handler

        handler = create_for_loop_handler()

        assert handler.execution_count == 0
        assert handler.items_processed == 0

    def test_for_loop_handler_stats(self):
        """Test for loop handler statistics tracking."""
        from gulfofmexico.handlers_impl.for_loop import create_for_loop_handler

        handler = create_for_loop_handler()
        handler.execution_count = 3
        handler.items_processed = 12

        stats = handler.get_stats()

        assert stats["total_loops_executed"] == 3
        assert stats["total_items_processed"] == 12

    def test_for_loop_handler_debug_info(self):
        """Test for loop handler debug information."""
        from gulfofmexico.handlers_impl.for_loop import create_for_loop_handler

        handler = create_for_loop_handler()
        debug_info = handler.get_debug_info()

        assert "ForLoopHandler" in debug_info
        assert "loops_executed=0" in debug_info
        assert "items_processed=0" in debug_info

    def test_for_loop_handler_imports(self):
        """Test for loop handler validates required imports."""
        from gulfofmexico.handlers_impl.for_loop import create_for_loop_handler
        from gulfofmexico.base import ForLoop, Name

        handler = create_for_loop_handler()
        handler.builtin_imports = {}  # No imports set

        mock_for = ForLoop(variable=Name("x", None), iterable=[], code=[])
        context = ExecutionContext()

        with pytest.raises(RuntimeError, match="missing required import"):
            handler.execute(mock_for, context)

    def test_for_loop_handler_factory(self):
        """Test for loop handler factory function."""
        from gulfofmexico.handlers_impl.for_loop import create_for_loop_handler

        handler = create_for_loop_handler()

        assert handler is not None
        assert handler.execution_count == 0
        assert handler.items_processed == 0


class TestWhileLoopHandler:
    """Test suite for WhileLoopHandler."""

    def test_while_loop_handler_recognition(self):
        """Test that handler recognizes while-loops."""
        from gulfofmexico.handlers_impl.while_loop import create_while_loop_handler
        from gulfofmexico.base import WhileLoop

        handler = create_while_loop_handler()
        mock_while = WhileLoop(
            condition=[],  # Empty condition for testing
            code=[],  # Empty code for testing
        )

        assert handler.can_handle(mock_while)

    def test_while_loop_handler_initialization(self):
        """Test while loop handler initializes with correct state."""
        from gulfofmexico.handlers_impl.while_loop import create_while_loop_handler

        handler = create_while_loop_handler()

        assert handler.execution_count == 0
        assert handler.iterations_total == 0
        assert handler.max_iterations_per_loop == 1000000

    def test_while_loop_handler_stats(self):
        """Test while loop handler statistics tracking."""
        from gulfofmexico.handlers_impl.while_loop import create_while_loop_handler

        handler = create_while_loop_handler()
        handler.execution_count = 2
        handler.iterations_total = 50

        stats = handler.get_stats()

        assert stats["total_loops_executed"] == 2
        assert stats["total_iterations"] == 50

    def test_while_loop_handler_debug_info(self):
        """Test while loop handler debug information."""
        from gulfofmexico.handlers_impl.while_loop import create_while_loop_handler

        handler = create_while_loop_handler()
        debug_info = handler.get_debug_info()

        assert "WhileLoopHandler" in debug_info
        assert "loops_executed=0" in debug_info
        assert "total_iterations=0" in debug_info

    def test_while_loop_handler_imports(self):
        """Test while loop handler validates required imports."""
        from gulfofmexico.handlers_impl.while_loop import create_while_loop_handler
        from gulfofmexico.base import WhileLoop

        handler = create_while_loop_handler()
        handler.builtin_imports = {}  # No imports set

        mock_while = WhileLoop(condition=[], code=[])
        context = ExecutionContext()

        with pytest.raises(RuntimeError, match="missing required import"):
            handler.execute(mock_while, context)

    def test_while_loop_handler_factory(self):
        """Test while loop handler factory function."""
        from gulfofmexico.handlers_impl.while_loop import create_while_loop_handler

        handler = create_while_loop_handler()

        assert handler is not None
        assert handler.execution_count == 0
        assert handler.iterations_total == 0


# ===== PHASE 3 WEEK 3: FUNCTION, CLASS, AND ADVANCED HANDLERS =====


class TestFunctionDefinitionHandler:
    """Test suite for FunctionDefinitionHandler."""

    def test_function_handler_recognition(self):
        """Test that handler recognizes function definitions."""
        from gulfofmexico.handlers_impl.function_definition import (
            create_function_definition_handler,
        )
        from gulfofmexico.base import FunctionDefinition, Name

        handler = create_function_definition_handler()
        mock_func = FunctionDefinition(
            name=Name("test_func", None),
            args=[],  # No args for testing
            code=[],  # Empty code for testing
            is_async=False,
        )

        assert handler.can_handle(mock_func)

    def test_function_handler_initialization(self):
        """Test function handler initializes with correct state."""
        from gulfofmexico.handlers_impl.function_definition import (
            create_function_definition_handler,
        )

        handler = create_function_definition_handler()

        assert handler.execution_count == 0
        assert handler.functions_defined == 0

    def test_function_handler_stats(self):
        """Test function handler statistics tracking."""
        from gulfofmexico.handlers_impl.function_definition import (
            create_function_definition_handler,
        )

        handler = create_function_definition_handler()
        handler.execution_count = 4
        handler.functions_defined = 4

        stats = handler.get_stats()

        assert stats["total_executions"] == 4
        assert stats["functions_defined"] == 4

    def test_function_handler_debug_info(self):
        """Test function handler debug information."""
        from gulfofmexico.handlers_impl.function_definition import (
            create_function_definition_handler,
        )

        handler = create_function_definition_handler()
        debug_info = handler.get_debug_info()

        assert "FunctionDefinitionHandler" in debug_info
        assert "executed=0" in debug_info
        assert "functions_defined=0" in debug_info

    def test_function_handler_imports(self):
        """Test function handler validates required imports."""
        from gulfofmexico.handlers_impl.function_definition import (
            create_function_definition_handler,
        )
        from gulfofmexico.base import FunctionDefinition, Name

        handler = create_function_definition_handler()
        handler.builtin_imports = {}  # No imports set

        mock_func = FunctionDefinition(
            name=Name("test", None), args=[], code=[], is_async=False
        )
        context = ExecutionContext()

        with pytest.raises(RuntimeError, match="missing required import"):
            handler.execute(mock_func, context)

    def test_function_handler_factory(self):
        """Test function handler factory function."""
        from gulfofmexico.handlers_impl.function_definition import (
            create_function_definition_handler,
        )

        handler = create_function_definition_handler()

        assert handler is not None
        assert handler.execution_count == 0
        assert handler.functions_defined == 0


class TestClassDeclarationHandler:
    """Test suite for ClassDeclarationHandler."""

    def test_class_handler_recognition(self):
        """Test that handler recognizes class declarations."""
        from gulfofmexico.handlers_impl.class_declaration import (
            create_class_declaration_handler,
        )
        from gulfofmexico.base import ClassDeclaration, Name

        handler = create_class_declaration_handler()
        mock_class = ClassDeclaration(
            name=Name("TestClass", None),
            code=[],  # Empty code for testing
        )

        assert handler.can_handle(mock_class)

    def test_class_handler_initialization(self):
        """Test class handler initializes with correct state."""
        from gulfofmexico.handlers_impl.class_declaration import (
            create_class_declaration_handler,
        )

        handler = create_class_declaration_handler()

        assert handler.execution_count == 0
        assert handler.classes_defined == 0

    def test_class_handler_stats(self):
        """Test class handler statistics tracking."""
        from gulfofmexico.handlers_impl.class_declaration import (
            create_class_declaration_handler,
        )

        handler = create_class_declaration_handler()
        handler.execution_count = 2
        handler.classes_defined = 2

        stats = handler.get_stats()

        assert stats["total_executions"] == 2
        assert stats["classes_defined"] == 2

    def test_class_handler_debug_info(self):
        """Test class handler debug information."""
        from gulfofmexico.handlers_impl.class_declaration import (
            create_class_declaration_handler,
        )

        handler = create_class_declaration_handler()
        debug_info = handler.get_debug_info()

        assert "ClassDeclarationHandler" in debug_info
        assert "executed=0" in debug_info
        assert "classes_defined=0" in debug_info

    def test_class_handler_imports(self):
        """Test class handler validates required imports."""
        from gulfofmexico.handlers_impl.class_declaration import (
            create_class_declaration_handler,
        )
        from gulfofmexico.base import ClassDeclaration, Name

        handler = create_class_declaration_handler()
        handler.builtin_imports = {}  # No imports set

        mock_class = ClassDeclaration(name=Name("TestClass", None), code=[])
        context = ExecutionContext()

        with pytest.raises(RuntimeError, match="missing required import"):
            handler.execute(mock_class, context)

    def test_class_handler_factory(self):
        """Test class handler factory function."""
        from gulfofmexico.handlers_impl.class_declaration import (
            create_class_declaration_handler,
        )

        handler = create_class_declaration_handler()

        assert handler is not None
        assert handler.execution_count == 0
        assert handler.classes_defined == 0


class TestAdvancedStatementHandlers:
    """Test suite for advanced statement handlers (After, Delete, Import/Export)."""

    def test_after_handler_recognition(self):
        """Test that after handler recognizes after-statements."""
        from gulfofmexico.handlers_impl.advanced_statements import create_after_handler
        from gulfofmexico.base import AfterStatement

        handler = create_after_handler()
        mock_after = AfterStatement(expression=[], code=[])

        assert handler.can_handle(mock_after)

    def test_after_handler_stats(self):
        """Test after handler statistics."""
        from gulfofmexico.handlers_impl.advanced_statements import create_after_handler

        handler = create_after_handler()
        handler.execution_count = 3
        handler.events_triggered = 1

        stats = handler.get_stats()

        assert stats["total_executions"] == 3
        assert stats["events_triggered"] == 1

    def test_delete_handler_recognition(self):
        """Test that delete handler recognizes delete-statements."""
        from gulfofmexico.handlers_impl.advanced_statements import (
            create_delete_handler,
        )
        from gulfofmexico.base import DeleteStatement, Name

        handler = create_delete_handler()
        mock_delete = DeleteStatement(name=Name("x", None))

        assert handler.can_handle(mock_delete)

    def test_delete_handler_stats(self):
        """Test delete handler statistics."""
        from gulfofmexico.handlers_impl.advanced_statements import (
            create_delete_handler,
        )

        handler = create_delete_handler()
        handler.execution_count = 5
        handler.deletions_performed = 5

        stats = handler.get_stats()

        assert stats["total_executions"] == 5
        assert stats["deletions_performed"] == 5

    def test_import_export_handler_recognition(self):
        """Test that import/export handler recognizes import/export statements."""
        from gulfofmexico.handlers_impl.advanced_statements import (
            create_import_export_handler,
        )
        from gulfofmexico.base import ImportStatement

        handler = create_import_export_handler()
        mock_import = ImportStatement(module="math", names=["pi"])

        assert handler.can_handle(mock_import)

    def test_import_export_handler_stats(self):
        """Test import/export handler statistics."""
        from gulfofmexico.handlers_impl.advanced_statements import (
            create_import_export_handler,
        )

        handler = create_import_export_handler()
        handler.execution_count = 8
        handler.imports_loaded = 3
        handler.exports_registered = 2

        stats = handler.get_stats()

        assert stats["total_executions"] == 8
        assert stats["imports_loaded"] == 3
        assert stats["exports_registered"] == 2

    def test_advanced_handlers_debug_info(self):
        """Test debug info for all advanced handlers."""
        from gulfofmexico.handlers_impl.advanced_statements import (
            create_after_handler,
            create_delete_handler,
            create_import_export_handler,
        )

        after_handler = create_after_handler()
        delete_handler = create_delete_handler()
        import_handler = create_import_export_handler()

        assert "AfterStatementHandler" in after_handler.get_debug_info()
        assert "DeleteStatementHandler" in delete_handler.get_debug_info()
        assert "ImportExportHandler" in import_handler.get_debug_info()


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/test_handlers.py -v
    pytest.main([__file__, "-v"])
