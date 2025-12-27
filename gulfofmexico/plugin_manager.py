"""
Production-Ready Plugin System - Phase 5

Full-featured plugin architecture for extending Gulf of Mexico interpreter.

Features:
    - Custom statement handlers
    - Built-in function registration
    - Custom operators
    - Plugin lifecycle management
    - Plugin discovery and loading
    - Dependency resolution
    - Plugin metadata and versioning
"""

import importlib
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Any, Type
import logging

from gulfofmexico.builtin import GulfOfMexicoValue, BuiltinFunction
from gulfofmexico.handlers import StatementHandler
from gulfofmexico.processor.syntax_tree import CodeStatement

logger = logging.getLogger(__name__)


@dataclass
class PluginMetadata:
    """Plugin metadata and information."""
    
    name: str
    version: str
    description: str = ""
    author: str = ""
    dependencies: list[str] = None
    supported_gom_versions: list[str] = None
    
    def __post_init__(self):
        """Initialize fields."""
        if self.dependencies is None:
            self.dependencies = []
        if self.supported_gom_versions is None:
            self.supported_gom_versions = ["*"]


class ProductionPlugin(ABC):
    """Base class for production-ready Gulf of Mexico plugins.
    
    Plugins can extend the interpreter with:
        - Custom statement handlers
        - Built-in functions
        - Custom operators
        - Type extensions
    
    Example:
        class MyPlugin(ProductionPlugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="my_plugin",
                    version="1.0.0",
                    description="My custom plugin"
                )
            
            def get_statement_handlers(self) -> list[StatementHandler]:
                return [MyCustomHandler()]
            
            def get_builtin_functions(self) -> dict[str, BuiltinFunction]:
                return {
                    "my_func": BuiltinFunction(...)
                }
    """
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata.
        
        Returns:
            PluginMetadata object
        """
        pass
    
    def get_statement_handlers(self) -> list[StatementHandler]:
        """Get custom statement handlers.
        
        Returns:
            List of statement handlers
        """
        return []
    
    def get_builtin_functions(self) -> dict[str, BuiltinFunction]:
        """Get custom built-in functions.
        
        Returns:
            Dictionary mapping function names to BuiltinFunction objects
        """
        return {}
    
    def get_custom_operators(self) -> dict[str, Callable]:
        """Get custom operators.
        
        Returns:
            Dictionary mapping operator symbols to implementations
        """
        return {}
    
    def get_type_extensions(self) -> dict[str, Type]:
        """Get custom type definitions.
        
        Returns:
            Dictionary mapping type names to type classes
        """
        return {}
    
    def on_load(self) -> None:
        """Called when plugin is loaded.
        
        Use for initialization and resource setup.
        """
        pass
    
    def on_unload(self) -> None:
        """Called when plugin is unloaded.
        
        Use for cleanup and resource teardown.
        """
        pass
    
    def validate(self) -> bool:
        """Validate plugin integrity.
        
        Returns:
            True if valid, False otherwise
        """
        return True


class PluginManager:
    """Manages plugin discovery, loading, and execution.
    
    Capabilities:
        - Dynamic plugin loading
        - Dependency resolution
        - Lifecycle management
        - Handler registration
        - Function registration
    """
    
    def __init__(self):
        """Initialize plugin manager."""
        self._plugins: dict[str, ProductionPlugin] = {}
        self._plugin_dirs: list[Path] = []
        self._loaded_modules: dict[str, Any] = {}
    
    def add_plugin_directory(self, directory: Path) -> None:
        """Add directory to plugin search path.
        
        Args:
            directory: Path to plugin directory
        """
        if directory not in self._plugin_dirs:
            self._plugin_dirs.append(directory)
            if str(directory) not in sys.path:
                sys.path.insert(0, str(directory))
    
    def discover_plugins(self) -> list[PluginMetadata]:
        """Discover available plugins in plugin directories.
        
        Returns:
            List of discovered plugin metadata
        """
        discovered = []
        
        for plugin_dir in self._plugin_dirs:
            if not plugin_dir.exists():
                continue
            
            for item in plugin_dir.iterdir():
                if item.is_dir():
                    # Look for plugins in subdirectories
                    init_file = item / "__init__.py"
                    if init_file.exists():
                        try:
                            plugin = self._load_plugin_from_module(item.name, item)
                            if plugin:
                                discovered.append(plugin.metadata)
                        except Exception as e:
                            logger.warning(f"Could not discover plugin in {item}: {e}")
                
                elif item.suffix == ".py" and item.name != "__init__.py":
                    # Look for plugins in Python files
                    try:
                        plugin = self._load_plugin_from_file(item)
                        if plugin:
                            discovered.append(plugin.metadata)
                    except Exception as e:
                        logger.warning(f"Could not discover plugin in {item}: {e}")
        
        return discovered
    
    def load_plugin(self, plugin_name: str) -> Optional[ProductionPlugin]:
        """Load a plugin by name.
        
        Args:
            plugin_name: Name of plugin to load
            
        Returns:
            Loaded plugin or None if not found
        """
        # Check if already loaded
        if plugin_name in self._plugins:
            return self._plugins[plugin_name]
        
        # Try to find and load from plugin directories
        for plugin_dir in self._plugin_dirs:
            plugin_path = plugin_dir / f"{plugin_name}.py"
            if plugin_path.exists():
                try:
                    plugin = self._load_plugin_from_file(plugin_path)
                    if plugin:
                        self._validate_and_register(plugin)
                        return plugin
                except Exception as e:
                    logger.error(f"Failed to load plugin {plugin_name}: {e}")
            
            # Try directory form
            plugin_dir_path = plugin_dir / plugin_name
            if plugin_dir_path.is_dir():
                try:
                    plugin = self._load_plugin_from_module(plugin_name, plugin_dir_path)
                    if plugin:
                        self._validate_and_register(plugin)
                        return plugin
                except Exception as e:
                    logger.error(f"Failed to load plugin {plugin_name}: {e}")
        
        logger.error(f"Plugin not found: {plugin_name}")
        return None
    
    def load_plugin_file(self, file_path: str) -> Optional[ProductionPlugin]:
        """Load a plugin from file.
        
        Args:
            file_path: Path to plugin file
            
        Returns:
            Loaded plugin or None
        """
        try:
            return self._load_plugin_from_file(Path(file_path))
        except Exception as e:
            logger.error(f"Failed to load plugin from {file_path}: {e}")
            return None
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin.
        
        Args:
            plugin_name: Name of plugin to unload
            
        Returns:
            True if successful
        """
        if plugin_name not in self._plugins:
            return False
        
        plugin = self._plugins[plugin_name]
        try:
            plugin.on_unload()
            del self._plugins[plugin_name]
            logger.info(f"Unloaded plugin: {plugin_name}")
            return True
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_name}: {e}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[ProductionPlugin]:
        """Get a loaded plugin.
        
        Args:
            plugin_name: Name of plugin
            
        Returns:
            Plugin or None if not loaded
        """
        return self._plugins.get(plugin_name)
    
    def get_all_plugins(self) -> dict[str, ProductionPlugin]:
        """Get all loaded plugins.
        
        Returns:
            Dictionary mapping plugin names to plugin objects
        """
        return dict(self._plugins)
    
    def get_all_statement_handlers(self) -> list[StatementHandler]:
        """Get statement handlers from all plugins.
        
        Returns:
            List of statement handlers
        """
        handlers = []
        for plugin in self._plugins.values():
            try:
                handlers.extend(plugin.get_statement_handlers())
            except Exception as e:
                logger.error(f"Error getting handlers from {plugin.metadata.name}: {e}")
        return handlers
    
    def get_all_builtin_functions(self) -> dict[str, BuiltinFunction]:
        """Get built-in functions from all plugins.
        
        Returns:
            Dictionary mapping function names to BuiltinFunction objects
        """
        functions = {}
        for plugin in self._plugins.values():
            try:
                functions.update(plugin.get_builtin_functions())
            except Exception as e:
                logger.error(f"Error getting functions from {plugin.metadata.name}: {e}")
        return functions
    
    def get_all_custom_operators(self) -> dict[str, Callable]:
        """Get custom operators from all plugins.
        
        Returns:
            Dictionary mapping operator symbols to implementations
        """
        operators = {}
        for plugin in self._plugins.values():
            try:
                operators.update(plugin.get_custom_operators())
            except Exception as e:
                logger.error(f"Error getting operators from {plugin.metadata.name}: {e}")
        return operators
    
    def _load_plugin_from_file(self, file_path: Path) -> Optional[ProductionPlugin]:
        """Load plugin from Python file.
        
        Args:
            file_path: Path to plugin file
            
        Returns:
            Plugin instance or None
        """
        if not file_path.exists():
            return None
        
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        if spec is None or spec.loader is None:
            return None
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find ProductionPlugin subclass in module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and
                issubclass(attr, ProductionPlugin) and
                attr is not ProductionPlugin):
                
                plugin = attr()
                self._loaded_modules[plugin.metadata.name] = module
                return plugin
        
        return None
    
    def _load_plugin_from_module(self, module_name: str, module_dir: Path) -> Optional[ProductionPlugin]:
        """Load plugin from module directory.
        
        Args:
            module_name: Name of module
            module_dir: Path to module directory
            
        Returns:
            Plugin instance or None
        """
        init_file = module_dir / "__init__.py"
        if not init_file.exists():
            return None
        
        return self._load_plugin_from_file(init_file)
    
    def _validate_and_register(self, plugin: ProductionPlugin) -> None:
        """Validate and register a plugin.
        
        Args:
            plugin: Plugin to validate and register
            
        Raises:
            ValueError: If plugin validation fails
        """
        if not plugin.validate():
            raise ValueError(f"Plugin {plugin.metadata.name} failed validation")
        
        # Check dependencies
        for dep in plugin.metadata.dependencies:
            if dep not in self._plugins:
                logger.warning(f"Plugin {plugin.metadata.name} has unmet dependency: {dep}")
        
        # Register plugin
        self._plugins[plugin.metadata.name] = plugin
        
        # Call lifecycle hook
        try:
            plugin.on_load()
        except Exception as e:
            logger.error(f"Error in plugin on_load: {e}")
        
        logger.info(f"Loaded plugin: {plugin.metadata.name} v{plugin.metadata.version}")


# Global plugin manager instance
_global_plugin_manager = PluginManager()


def get_plugin_manager() -> PluginManager:
    """Get global plugin manager instance.
    
    Returns:
        Global PluginManager
    """
    return _global_plugin_manager
