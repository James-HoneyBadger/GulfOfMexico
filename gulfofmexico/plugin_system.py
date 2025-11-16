"""
EXPERIMENTAL Plugin System for Gulf of Mexico

⚠️ WARNING: This module is NOT used in production! ⚠️

The production Gulf of Mexico interpreter does NOT support plugins.
All code execution flows through the monolithic interpreter.py.

This experimental module demonstrates how a plugin architecture COULD work
with the experimental handler-based engine in gulfofmexico/engine/, but:
    - The handler-based engine is not used
    - Plugins are not loaded
    - No plugin APIs are exposed

Purpose:
    Proof-of-concept for future extensibility if the interpreter is
    refactored to use the handler pattern instead of pattern matching.

Theoretical Plugin Capabilities:
    - Custom statement handlers
    - Built-in function registration
    - Custom operators
    - Type definitions
    - Syntax extensions

Reality:
    This code exists but is never executed. The production interpreter
    is monolithic and does not have a plugin system.
"""

from abc import ABC, abstractmethod
from gulfofmexico.handlers import StatementHandler


class Plugin(ABC):
    """Base class for EXPERIMENTAL Gulf of Mexico interpreter plugins.

    ⚠️ WARNING: Plugins are NOT supported in production! ⚠️

    This class demonstrates how plugins could work with the experimental
    handler-based engine. The production interpreter does not support plugins
    and will never load or execute plugin code.

    Theoretical plugin capabilities:
        - Custom statement handlers for new syntax
        - Built-in functions like print() or Math functions
        - Custom operators beyond +, -, *, /
        - Type definitions beyond Number, String, List
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin identifier name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version.

        Returns:
            Version string (e.g., "1.0.0")
        """
        pass

    @property
    def description(self) -> str:
        """Plugin description.

        Returns:
            Description of what the plugin provides
        """
        return ""

    def get_statement_handlers(self) -> list[StatementHandler]:
        """Get custom statement handlers provided by this plugin.

        Returns:
            List of statement handlers
        """
        return []

    def get_builtin_functions(
        self,
    ) -> dict[str, Callable[..., GulfOfMexicoValue]]:
        """Get custom built-in functions provided by this plugin.

        Returns:
            Dictionary mapping function names to implementations
        """
        return {}

    def on_load(self) -> None:
        """Called when the plugin is loaded.

        Use this to perform initialization, register resources, etc.
        """
        pass

    def on_unload(self) -> None:
        """Called when the plugin is unloaded.

        Use this to perform cleanup, release resources, etc.
        """
        pass


class PluginManager:
    """Manages plugins for the interpreter.

    Handles loading, unloading, and querying plugins.
    """

    def __init__(self):
        """Initialize the plugin manager."""
        self._plugins: dict[str, Plugin] = {}
        self._loaded: set[str] = set()

    def register(self, plugin: Plugin) -> None:
        """Register a plugin.

        Args:
            plugin: Plugin to register

        Raises:
            ValueError: If plugin with same name already registered
        """
        if plugin.name in self._plugins:
            raise ValueError(f"Plugin '{plugin.name}' is already registered")

        self._plugins[plugin.name] = plugin
        plugin.on_load()
        self._loaded.add(plugin.name)

        print(f"Loaded plugin: {plugin.name} v{plugin.version}")
        if plugin.description:
            print(f"  {plugin.description}")

    def unregister(self, plugin_name: str) -> None:
        """Unregister a plugin.

        Args:
            plugin_name: Name of plugin to unregister

        Raises:
            ValueError: If plugin not found
        """
        if plugin_name not in self._plugins:
            raise ValueError(f"Plugin '{plugin_name}' not found")

        plugin = self._plugins[plugin_name]
        plugin.on_unload()
        del self._plugins[plugin_name]
        self._loaded.discard(plugin_name)

        print(f"Unloaded plugin: {plugin_name}")

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get a plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin if found, None otherwise
        """
        return self._plugins.get(name)

    def get_all_plugins(self) -> list[Plugin]:
        """Get all registered plugins.

        Returns:
            List of all plugins
        """
        return list(self._plugins.values())

    def get_all_statement_handlers(self) -> list[StatementHandler]:
        """Get all statement handlers from all plugins.

        Returns:
            List of statement handlers from all plugins
        """
        handlers = []
        for plugin in self._plugins.values():
            handlers.extend(plugin.get_statement_handlers())
        return handlers

    def get_all_builtin_functions(
        self,
    ) -> dict[str, Callable[..., GulfOfMexicoValue]]:
        """Get all built-in functions from all plugins.

        Returns:
            Dictionary of all built-in functions
        """
        functions = {}
        for plugin in self._plugins.values():
            functions.update(plugin.get_builtin_functions())
        return functions

    def list_plugins(self) -> None:
        """Print information about all loaded plugins."""
        if not self._plugins:
            print("No plugins loaded")
            return

        print(f"\nLoaded Plugins ({len(self._plugins)}):")
        print("-" * 60)
        for plugin in self._plugins.values():
            print(f"  {plugin.name} v{plugin.version}")
            if plugin.description:
                print(f"    {plugin.description}")

            handlers = plugin.get_statement_handlers()
            if handlers:
                print(f"    Statement handlers: {len(handlers)}")

            funcs = plugin.get_builtin_functions()
            if funcs:
                print(f"    Built-in functions: {len(funcs)}")


# Example plugin implementation
class ExamplePlugin(Plugin):
    """Example plugin demonstrating the plugin system."""

    @property
    def name(self) -> str:
        return "example-plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Example plugin demonstrating custom functionality"

    def get_statement_handlers(self) -> list[StatementHandler]:
        """Return custom handlers."""
        # In a real plugin, you'd return actual handler instances
        return []

    def get_builtin_functions(
        self,
    ) -> dict[str, Callable[..., GulfOfMexicoValue]]:
        """Return custom built-in functions."""
        from gulfofmexico.builtin import GulfOfMexicoString

        def hello(name: GulfOfMexicoValue) -> GulfOfMexicoString:
            """Custom hello function."""
            from gulfofmexico.builtin import db_to_string

            name_str = db_to_string(name).value
            return GulfOfMexicoString(f"Hello from plugin, {name_str}!")

        return {"plugin_hello": hello}

    def on_load(self) -> None:
        """Initialize the plugin."""
        print(f"  Initializing {self.name}...")

    def on_unload(self) -> None:
        """Clean up the plugin."""
        print(f"  Cleaning up {self.name}...")


if __name__ == "__main__":
    # Demonstrate plugin system
    manager = PluginManager()

    # Register example plugin
    plugin = ExamplePlugin()
    manager.register(plugin)

    # List plugins
    manager.list_plugins()

    # Get built-in functions
    functions = manager.get_all_builtin_functions()
    print(f"\nAvailable functions: {list(functions.keys())}")

    # Unregister plugin
    manager.unregister("example-plugin")
