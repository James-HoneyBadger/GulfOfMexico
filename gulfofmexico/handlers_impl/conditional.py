"""
Conditional Handler for Gulf of Mexico Interpreter.

Handles if/conditional statements which execute code blocks based on
boolean condition evaluation.

Supports:
- Deterministic execution (true/false conditions)
- Probabilistic execution (maybe/probabilistic values)
- Scope management for conditional blocks
- Expression evaluation for conditions
"""

from __future__ import annotations

import logging
import random
from typing import Any, Callable, Dict, Optional

from gulfofmexico.base import StatementHandler
from gulfofmexico.builtin import GulfOfMexicoValue
from gulfofmexico.context import ExecutionContext
from gulfofmexico.processor.syntax_tree import Conditional, CodeStatement


logger = logging.getLogger(__name__)


class ConditionalHandler(StatementHandler):
    """Handler for conditional (if) statements in Gulf of Mexico.
    
    Conditionals evaluate an expression to a boolean and execute code blocks
    conditionally. Gulf of Mexico supports deterministic booleans (true/false)
    and probabilistic booleans (maybe) which execute with probability.
    
    Features:
    - Condition evaluation to boolean values
    - Deterministic execution for true/false
    - Probabilistic execution for maybe/uncertain values
    - New scope creation for conditional blocks
    - Full expression evaluation
    """

    def __init__(self):
        """Initialize conditional handler."""
        super().__init__()
        self.conditional_count = 0
        self.builtin_imports = {}  # Imported from interpreter scope

    def set_interpreter_imports(self, imports: Dict[str, Callable]) -> None:
        """Set references to interpreter functions needed for conditional execution.
        
        Required imports:
        - evaluate_expression: Evaluate the condition expression
        - db_to_boolean: Convert value to boolean for evaluation
        - interpret_code_statements: Execute statements in new scope
        """
        self.builtin_imports.update(imports)

    def can_handle(self, stmt: Conditional) -> bool:
        """Conditional handler handles all conditional statements."""
        return isinstance(stmt, Conditional)

    def execute(
        self,
        stmt: Conditional,
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute conditional statement based on condition evaluation.
        
        Args:
            stmt: Conditional statement to execute
            context: Execution context with namespaces and state
            
        Returns:
            Return value from conditional block if executed, None otherwise
        """
        self.conditional_count += 1

        if context.debug_level >= 2:
            logger.info(f"[Conditional] Executing if statement (#{self.conditional_count})")

        # Evaluate the condition expression
        condition_value = self._evaluate_condition(stmt, context)

        if context.debug_level >= 3:
            logger.debug(f"[Conditional] Condition value: {condition_value}")

        # Determine if we should execute the block
        should_execute = self._determine_execution(condition_value, context)

        if context.debug_level >= 2:
            logger.info(f"[Conditional] Should execute: {should_execute}")

        if should_execute:
            return self._execute_block(stmt, context)
        
        return None

    def _evaluate_condition(
        self,
        stmt: Conditional,
        context: ExecutionContext,
    ) -> GulfOfMexicoValue:
        """Evaluate the condition expression.
        
        Args:
            stmt: Conditional statement with expression
            context: Execution context
            
        Returns:
            Evaluated condition value
        """
        evaluate_expr = self.builtin_imports.get("evaluate_expression")
        if not evaluate_expr:
            raise RuntimeError("Missing evaluate_expression import")

        condition_value = evaluate_expr(
            stmt.expression,
            context.namespaces,
            context.async_statements,
            context.when_statement_watchers,
        )

        if context.debug_level >= 3:
            logger.debug(f"[Conditional] Evaluated condition to: {type(condition_value).__name__}")

        return condition_value

    def _determine_execution(
        self,
        condition_value: GulfOfMexicoValue,
        context: ExecutionContext,
    ) -> bool:
        """Determine if conditional block should execute.
        
        Gulf of Mexico supports three types of boolean values:
        - true: Always execute
        - false: Never execute
        - maybe: Execute with 50% probability
        
        Args:
            condition_value: Evaluated condition
            context: Execution context
            
        Returns:
            True if block should execute, False otherwise
        """
        db_bool = self.builtin_imports.get("db_to_boolean")
        if not db_bool:
            raise RuntimeError("Missing db_to_boolean import")

        # Convert to boolean representation
        condition = db_bool(condition_value)

        # Determine execution based on boolean value
        if condition.value is True:
            return True
        elif condition.value is False:
            return False
        else:
            # Maybe/uncertain value: execute with 50% probability
            should_execute = random.random() < 0.50
            
            if context.debug_level >= 2:
                logger.info(
                    f"[Conditional] Maybe value, probabilistic execution: {should_execute}"
                )
            
            return should_execute

    def _execute_block(
        self,
        stmt: Conditional,
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute the conditional block in a new scope.
        
        Conditionals create a new scope to isolate variable definitions
        within the conditional from the outer scope.
        
        Args:
            stmt: Conditional statement with code block
            context: Execution context
            
        Returns:
            Return value from executed statements, if any
        """
        interpret_stmts = self.builtin_imports.get("interpret_code_statements")
        if not interpret_stmts:
            raise RuntimeError("Missing interpret_code_statements import")

        if context.debug_level >= 2:
            logger.info(f"[Conditional] Executing {len(stmt.code)} statements in new scope")

        # Create new scope for conditional block
        # Pass empty async statements and new watcher scope
        result = interpret_stmts(
            stmt.code,
            context.namespaces + [{}],  # New scope
            [],  # Empty async statements for this block
            context.when_statement_watchers + [{}],  # New watcher scope
            {},  # Empty importable_names
            [],  # Empty exported_names
        )

        if context.debug_level >= 3:
            logger.debug(f"[Conditional] Block execution result: {type(result).__name__ if result else 'None'}")

        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get handler statistics.
        
        Returns:
            Dictionary with:
            - total_conditionals: Total conditional statements executed
        """
        return {
            "total_conditionals": self.conditional_count,
        }

    def get_debug_info(self) -> str:
        """Get debug information about conditional handler state.
        
        Returns:
            Formatted debug information string
        """
        return (
            f"ConditionalHandler Debug Info:\n"
            f"  Total Conditional Statements: {self.conditional_count}\n"
        )


def create_conditional_handler() -> ConditionalHandler:
    """Factory function to create a configured conditional handler.
    
    Returns:
        Initialized ConditionalHandler ready for use
    """
    return ConditionalHandler()
