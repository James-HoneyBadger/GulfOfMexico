"""⚠️ EXPERIMENTAL - Integration tests for the experimental handler-based engine.

WARNING: These tests validate the EXPERIMENTAL gulfofmexico/engine/ package,
NOT the production interpreter (gulfofmexico/interpreter.py).

These tests verify that the experimental architecture works in isolation,
but this code is NOT integrated into the production execution path.

To test the production interpreter, you would run actual .gom files via
gulfofmexico.__init__.run_file() and verify the output.
"""

import unittest
from gulfofmexico.context import ExecutionContext, InterpreterConfig
from gulfofmexico.engine.core import InterpretEngine
from gulfofmexico.handlers import HandlerRegistry


class TestInterpretEngine(unittest.TestCase):
    """Test the new InterpretEngine."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = InterpreterConfig(
            enable_expression_cache=True,
            enable_namespace_cache=True,
        )
        self.engine = InterpretEngine(self.config)

    def test_engine_initialization(self):
        """Test that engine initializes correctly."""
        self.assertIsNotNone(self.engine.registry)
        self.assertIsNotNone(self.engine.evaluator)
        self.assertEqual(self.engine.config.enable_expression_cache, True)

    def test_handlers_registered(self):
        """Test that default handlers are registered."""
        stats = self.engine.get_stats()
        self.assertGreater(stats["registered_handlers"], 0)

    def test_handler_registry(self):
        """Test handler registry functionality."""
        from gulfofmexico.engine.handlers.variables import (
            VariableDeclarationHandler,
        )
        from gulfofmexico.processor.syntax_tree import (
            VariableDeclaration,
        )
        from gulfofmexico.base import Token, TokenType

        # Create a sample statement
        stmt = VariableDeclaration(
            name=Token(TokenType.NAME, "x", 1, 4),
            modifiers=[Token(TokenType.NAME, "var", 1, 0)],
            type_annotation=None,
            lifetime=None,
            expression=[],
            debug=0,
            confidence=1,
        )

        # Verify handler can be found
        handler = self.engine.registry.get_handler(stmt)
        self.assertIsNotNone(handler)
        self.assertIsInstance(handler, VariableDeclarationHandler)


class TestPerformanceFeatures(unittest.TestCase):
    """Test performance features."""

    def test_expression_cache_enabled(self):
        """Test that expression cache can be enabled."""
        config = InterpreterConfig(enable_expression_cache=True)
        engine = InterpretEngine(config)

        self.assertTrue(engine.evaluator.enable_cache)

    def test_expression_cache_disabled(self):
        """Test that expression cache can be disabled."""
        config = InterpreterConfig(enable_expression_cache=False)
        engine = InterpretEngine(config)

        self.assertFalse(engine.evaluator.enable_cache)

    def test_get_stats(self):
        """Test that statistics can be retrieved."""
        engine = InterpretEngine()
        stats = engine.get_stats()

        self.assertIn("expression_cache", stats)
        self.assertIn("registered_handlers", stats)


class TestPluginSystem(unittest.TestCase):
    """Test plugin system."""

    def test_plugin_manager_initialization(self):
        """Test that plugin manager initializes."""
        from gulfofmexico.plugin_system import PluginManager

        manager = PluginManager()
        self.assertEqual(len(manager.get_all_plugins()), 0)

    def test_plugin_registration(self):
        """Test plugin registration."""
        from gulfofmexico.plugin_system import (
            PluginManager,
            ExamplePlugin,
        )

        manager = PluginManager()
        plugin = ExamplePlugin()

        manager.register(plugin)

        self.assertEqual(len(manager.get_all_plugins()), 1)
        self.assertIsNotNone(manager.get_plugin("example-plugin"))

    def test_plugin_unregistration(self):
        """Test plugin unregistration."""
        from gulfofmexico.plugin_system import (
            PluginManager,
            ExamplePlugin,
        )

        manager = PluginManager()
        plugin = ExamplePlugin()

        manager.register(plugin)
        manager.unregister("example-plugin")

        self.assertEqual(len(manager.get_all_plugins()), 0)


if __name__ == "__main__":
    unittest.main()
