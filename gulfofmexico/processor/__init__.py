"""
Gulf of Mexico Processor Package

Front-end pipeline: source code → tokens → syntax tree → expression trees.

Modules:
    lexer           – Tokenizer (source text → Token list)
    syntax_tree     – Statement parser (tokens → CodeStatement AST)
    expression_tree – Expression parser (token spans → ExpressionTreeNode trees)
"""

from .lexer import tokenize
from .syntax_tree import generate_syntax_tree

__all__ = [
    "tokenize",
    "generate_syntax_tree",
]
