"""
Expression Tree Nodes for Gulf of Mexico

Represents expressions as abstract syntax trees for evaluation.
Each node type corresponds to a different expression construct.

Node Types:
    - ValueNode: Literals (numbers, strings, names)
    - FunctionNode: Function calls with arguments
    - ExpressionNode: Binary operations (+ - * / == etc.)
    - SingleOperatorNode: Unary operations (- for negation, ; for not)
    - IndexNode: Array/object indexing
    - ListNode: List literals [1, 2, 3]

Expression Building:
    build_expression_tree() converts token lists into trees using
    operator precedence and parentheses grouping. The tree is then
    evaluated by evaluate_expression() in interpreter.py.

Operator Precedence (highest to lowest):
    1. Indexing: []
    2. Function calls: ()
    3. Exponentiation: ^
    4. Unary: -, ;
    5. Multiplication/Division: *, /
    6. Addition/Subtraction: +, -
    7. Comparison: <, >, <=, >=
    8. Equality: =, ==, ===, ====
    9. Logical AND: &
    10. Logical OR: |

Special Features:
    - Short-circuit evaluation for & and |
    - String interpolation: "${expression}" within strings
    - Approximate equality with fuzzy matching
    - Multiple equality levels (=, ==, ===, ====)
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Optional

from gulfofmexico.base import (
    STR_TO_OPERATOR,
    OperatorType,
    Token,
    TokenType,
    raise_error_at_token,
)


class ExpressionTreeNode(metaclass=ABCMeta):
    """Base class for all expression tree nodes."""

    @abstractmethod
    def to_string(self, tabs: int = 0) -> str:
        """Convert node to indented string representation for debugging."""


class SingleOperatorNode(ExpressionTreeNode):
    """Unary operator node (negation, logical not).

    Operators:
        - (minus): Negation for numbers, reverse for lists/strings
        ; (semicolon): Logical NOT
    """

    def __init__(self, expression: ExpressionTreeNode, operator: Token) -> None:
        self.expression = expression
        self.operator = operator

    def to_string(self, tabs: int = 0) -> str:
        return (
            f"{'  ' * tabs}Single Operator: \n"
            + f"{'  ' * (tabs + 1)}Operator: {self.operator.value}\n"
            + f"{'  ' * (tabs + 1)}Expression: \n"
            + f"{self.expression.to_string(tabs + 2)}"
        )


class ListNode(ExpressionTreeNode):
    def __init__(self, values: list[ExpressionTreeNode]):
        self.values = values

    def to_string(self, tabs: int = 0) -> str:
        return (
            f"{'  ' * tabs}List: \n"
            + f"{'  ' * (tabs + 1)}Values: \n"
            + "\n".join([f"{v.to_string(tabs + 2)}" for v in self.values])
        )


class ExpressionNode(ExpressionTreeNode):
    def __init__(
        self,
        left: ExpressionTreeNode,
        right: ExpressionTreeNode,
        operator: OperatorType,
        operator_token: Token,
    ):
        self.left = left
        self.right = right
        self.operator = operator
        self.operator_token = operator_token

    def to_string(self, tabs: int = 0) -> str:
        return (
            f"{'  ' * tabs}Expression: \n"
            + f"{'  ' * (tabs + 1)}Operator: {self.operator}\n"
            + f"{'  ' * (tabs + 1)}Left: \n"
            + f"{self.left.to_string(tabs + 2)}\n"
            + f"{'  ' * (tabs + 1)}Right: \n"
            + f"{self.right.to_string(tabs + 2)}"
        )


class FunctionNode(ExpressionTreeNode):
    def __init__(self, name: Token, args: list[ExpressionTreeNode]):
        self.name = name
        self.args = args

    def to_string(self, tabs: int = 0) -> str:
        return (
            f"{'  ' * tabs}Function: \n"
            + f"{'  ' * (tabs + 1)}Name: {self.name}\n"
            + f"{'  ' * (tabs + 1)}Arguments: \n"
            + "\n".join([f"{arg.to_string(tabs + 2)}" for arg in self.args])
        )


class IndexNode(ExpressionTreeNode):
    def __init__(self, value: ExpressionTreeNode, index: ExpressionTreeNode):
        self.value = value
        self.index = index

    def to_string(self, tabs: int = 0) -> str:
        return (
            f"{'  ' * tabs}Index: \n"
            + f"{'  ' * (tabs + 1)}Of: \n"
            + f"{self.value.to_string(tabs + 2)}\n"
            + f"{'  ' * (tabs + 1)}At: \n"
            + f"{self.index.to_string(tabs + 2)}"
        )


class MethodCallNode(ExpressionTreeNode):
    """A method call on a value that is not a plain name: ``"a,b".split(",")``."""

    def __init__(self, receiver: ExpressionTreeNode, name: Token, args: list[ExpressionTreeNode]):
        self.receiver = receiver
        self.name = name
        self.args = args

    def to_string(self, tabs: int = 0) -> str:
        return (
            f"{'  ' * tabs}Method call: {self.name.value}\n"
            f"{'  ' * (tabs + 1)}Receiver: \n{self.receiver.to_string(tabs + 2)}\n"
            f"{'  ' * (tabs + 1)}Arguments: \n"
            + "\n".join(arg.to_string(tabs + 2) for arg in self.args)
        )


class MemberAccessNode(ExpressionTreeNode):
    """Property access on a value that is not a plain name: ``"abc".length``."""

    def __init__(self, receiver: ExpressionTreeNode, name: Token):
        self.receiver = receiver
        self.name = name

    def to_string(self, tabs: int = 0) -> str:
        return (
            f"{'  ' * tabs}Member: {self.name.value}\n"
            f"{self.receiver.to_string(tabs + 1)}"
        )


class MapLiteralNode(ExpressionTreeNode):
    """An object/map literal such as ``{ name: "Lu" }``."""

    def __init__(self, pairs: list[tuple[str, ExpressionTreeNode]]):
        self.pairs = pairs

    def to_string(self, tabs: int = 0) -> str:
        return (
            f"{'  ' * tabs}Map: \n"
            + "\n".join(
                f"{'  ' * (tabs + 1)}{key}: \n{value.to_string(tabs + 2)}"
                for key, value in self.pairs
            )
        )


class ValueNode(ExpressionTreeNode):
    def __init__(self, name_or_value: Token):
        self.name_or_value = name_or_value

    def to_string(self, tabs: int = 0) -> str:
        return f"{'  ' * tabs}Value: {self.name_or_value}"


def get_expr_first_token(expr: ExpressionTreeNode) -> Optional[Token]:
    match expr:
        case SingleOperatorNode():
            return expr.operator
        case ExpressionNode():
            return get_expr_first_token(expr.left) or get_expr_first_token(expr.right)
        case FunctionNode():
            return expr.name
        case ListNode():
            return None if not expr.values else get_expr_first_token(expr.values[0])
        case MapLiteralNode():
            return None if not expr.pairs else get_expr_first_token(expr.pairs[0][1])
        case MethodCallNode():
            return get_expr_first_token(expr.receiver) or expr.name
        case MemberAccessNode():
            return get_expr_first_token(expr.receiver) or expr.name
        case ValueNode():
            return expr.name_or_value
        case IndexNode():
            return get_expr_first_token(expr.value) or get_expr_first_token(expr.index)
    return None


def _blank_value_node(line: int, col: int) -> ValueNode:
    """The value of () - a blank name that resolves to the empty value."""
    return ValueNode(Token(TokenType.NAME, "", line, col))


def _split_top_level_commas(tokens: list[Token]) -> list[list[Token]]:
    """Split *tokens* on commas that are not nested in brackets or parens."""
    parts: list[list[Token]] = [[]]
    depth = 0
    for token in tokens:
        if token.type in (TokenType.L_PAREN, TokenType.L_SQUARE):
            depth += 1
        elif token.type in (TokenType.R_PAREN, TokenType.R_SQUARE):
            depth = max(0, depth - 1)
        if token.type == TokenType.COMMA and depth == 0:
            parts.append([])
        else:
            parts[-1].append(token)
    return parts


def _match_parens(tokens: list[Token]) -> dict[int, int]:
    """Map the index of each matched opening paren to its closing paren."""
    stack: list[int] = []
    matched: dict[int, int] = {}
    for i, token in enumerate(tokens):
        if token.type == TokenType.L_PAREN:
            stack.append(i)
        elif token.type == TokenType.R_PAREN and stack:
            matched[stack.pop()] = i
    return matched


def _group_token(node: ExpressionTreeNode, source: Token, value: str = "(...)") -> Token:
    return Token(TokenType.PAREN_GROUP, value, source.line, source.col, tree=node)


def _normalise_new_empty_call(tokens: list[Token]) -> list[Token]:
    """Turn ``new Class()`` into ``new Class``.

    The empty-value tokenisation of ``()`` makes ``new Class()`` look like a
    call to ``Class`` with a blank argument, which would try to call a class
    object. Dropping the empty argument keeps the intended ``new`` behaviour.
    """
    meaningful = [i for i, t in enumerate(tokens) if t.type != TokenType.WHITESPACE]
    if len(meaningful) < 3:
        return tokens
    new_idx, cls_idx, blank_idx = meaningful[-3], meaningful[-2], meaningful[-1]
    if not (
        tokens[new_idx].type == TokenType.NAME
        and tokens[new_idx].value == "new"
        and tokens[cls_idx].type == TokenType.NAME
        and tokens[blank_idx].type == TokenType.NAME
        and tokens[blank_idx].value == ""
    ):
        return tokens
    return tokens[: cls_idx + 1]


def _collapse_parens(filename: str, tokens: list[Token], code: str) -> list[Token]:
    """Replace parenthesised groups with single PAREN_GROUP tokens.

    A group that directly follows a name is a function call (its contents are
    the comma-separated arguments). Any other group is a grouped expression.
    Stray, unmatched parentheses are treated as whitespace, matching the
    spec's "parentheses do nothing" rule.
    """
    if not any(t.type in (TokenType.L_PAREN, TokenType.R_PAREN) for t in tokens):
        return tokens

    matched = _match_parens(tokens)
    closing = set(matched.values())
    out: list[Token] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.type == TokenType.R_PAREN:
            if i not in closing:  # stray closing paren -> whitespace
                i += 1
                continue
            out.append(token)
            i += 1
            continue
        if token.type != TokenType.L_PAREN:
            out.append(token)
            i += 1
            continue
        if i not in matched:  # stray opening paren -> whitespace
            i += 1
            continue

        close = matched[i]
        inner = tokens[i + 1 : close]
        j = len(out) - 1
        while j >= 0 and out[j].type == TokenType.WHITESPACE:
            j -= 1
        attached = j >= 0 and out[j].type == TokenType.NAME

        if attached and j - 1 >= 0 and out[j - 1].type == TokenType.DOT:
            # "receiver".method(args) - the receiver is everything before the dot.
            name_token = out[j]
            receiver_tokens = [t for t in out[: j - 1] if t.type != TokenType.WHITESPACE]
            receiver_node: ExpressionTreeNode = (
                build_expression_tree(filename, receiver_tokens, code)
                if receiver_tokens
                else ValueNode(Token(TokenType.NAME, "undefined", name_token.line, name_token.col))
            )
            segments = _split_top_level_commas(inner)
            arg_tokens = [seg for seg in segments if any(t.type != TokenType.WHITESPACE for t in seg)]
            args = [build_expression_tree(filename, seg, code) for seg in arg_tokens] if arg_tokens else []
            node = MethodCallNode(receiver_node, name_token, args)
            source = receiver_tokens[0] if receiver_tokens else name_token
            out = [_group_token(node, source, "method(...)")]
            i = close + 1
            continue

        if attached:
            name_token = out[j]
            segments = _split_top_level_commas(inner)
            arg_tokens = [seg for seg in segments if any(t.type != TokenType.WHITESPACE for t in seg)]
            if not arg_tokens:
                args = [_blank_value_node(token.line, token.col)]
            else:
                args = [build_expression_tree(filename, seg, code) for seg in arg_tokens]

            k = j - 1
            while k >= 0 and out[k].type == TokenType.WHITESPACE:
                k -= 1
            if k >= 0 and out[k].type == TokenType.NAME and out[k].value == "new":
                node = FunctionNode(out[k], [ValueNode(name_token)] + args)
                del out[k:]
            else:
                node = FunctionNode(name_token, args)
                del out[j:]
            out.append(_group_token(node, name_token, name_token.value + "(...)"))
        else:
            node = build_expression_tree(filename, inner, code)
            out.append(_group_token(node, token))
        i = close + 1
    return out


# Lower value = binds more loosely = becomes the root of the expression.
# Used only to break ties when two operators have the same surrounding
# whitespace (Gulf of Mexico's primary precedence mechanism).
_OPERATOR_BINDING_POWER = {
    OperatorType.COM: 0,
    OperatorType.OR: 1,
    OperatorType.AND: 2,
    OperatorType.E: 3,
    OperatorType.EE: 3,
    OperatorType.EEE: 3,
    OperatorType.EEEE: 3,
    OperatorType.NE: 3,
    OperatorType.NEE: 3,
    OperatorType.NEEE: 3,
    OperatorType.TE: 3,
    OperatorType.TEE: 3,
    OperatorType.TEEE: 3,
    OperatorType.GT: 4,
    OperatorType.GE: 4,
    OperatorType.LT: 4,
    OperatorType.LE: 4,
    OperatorType.ADD: 5,
    OperatorType.SUB: 5,
    OperatorType.MUL: 6,
    OperatorType.DIV: 6,
    OperatorType.EXP: 7,
}


def _build_map_literal(filename: str, tokens: list[Token], code: str) -> MapLiteralNode:
    """Build a map literal from the tokens between braces."""
    depth = 0
    entries: list[list[Token]] = [[]]
    for token in tokens:
        if token.type in (TokenType.L_CURLY, TokenType.L_PAREN, TokenType.L_SQUARE):
            depth += 1
        elif token.type in (TokenType.R_CURLY, TokenType.R_PAREN, TokenType.R_SQUARE):
            depth -= 1
        if token.type == TokenType.COMMA and depth == 0:
            entries.append([])
        else:
            entries[-1].append(token)

    pairs: list[tuple[str, ExpressionTreeNode]] = []
    for entry in entries:
        colon = next(
            (i for i, t in enumerate(entry) if t.type == TokenType.COLON),
            -1,
        )
        if colon == -1:
            continue
        key_tokens = [t for t in entry[:colon] if t.type not in (TokenType.WHITESPACE,)]
        value_tokens = entry[colon + 1 :]
        if not key_tokens:
            continue
        key = key_tokens[-1].value
        pairs.append((key, build_expression_tree(filename, value_tokens, code)))
    return MapLiteralNode(pairs)


def build_expression_tree(filename: str, tokens: list[Token], code: str) -> ExpressionTreeNode:
    """
    This language has significant whitespace, so the biggest split happens where there is most space
     - func a, b  +  c becomes func(a, b) + c but func a, b+c  becomes func(a, b + c)
     - a + func   b  ,  c + d is not legal because it translates to (a + func)(b, c + d)
     - 2 * 1+3 becomes 2 * (1 + 3)
    """

    if not tokens:
        # Empty expression returns undefined
        return ValueNode(Token(TokenType.NAME, "undefined", 1, 0))

    # tabs at the beginning or end do not matter
    for token in tokens[1:-1]:
        if token.type == TokenType.WHITESPACE and "\t" in token.value:
            raise_error_at_token(filename, code, "Tabs are not allowed in expressions.", token)
        elif token.type == TokenType.NEWLINE:
            raise_error_at_token(
                filename,
                code,
                "Due to the laws of significant whitespace, no newline characters are permitted"
                " in expressions. If your code is so long that it needs newlines,"
                " consider rewriting it :)",
                token,
            )

    # Parentheses become grouped expressions / function-call argument lists.
    tokens = _collapse_parens(filename, _normalise_new_empty_call(tokens), code)

    # create a new list consisting and tokens and a brand new type: the list
    tokens_without_whitespace = [token for token in tokens if token.type != TokenType.WHITESPACE]
    if not tokens_without_whitespace:
        # All whitespace — return undefined
        return ValueNode(Token(TokenType.NAME, "undefined", tokens[0].line if tokens else 1, 0))
    if (
        len(tokens_without_whitespace) == 2
        and tokens_without_whitespace[0].type == TokenType.L_SQUARE
        and tokens_without_whitespace[1].type == TokenType.R_SQUARE
    ):
        return ListNode([])  # easy way out xD
    if (
        len(tokens_without_whitespace) >= 2
        and tokens_without_whitespace[0].type == TokenType.L_CURLY
        and tokens_without_whitespace[-1].type == TokenType.R_CURLY
    ):
        return _build_map_literal(
            filename,
            tokens_without_whitespace[1:-1],
            code,
        )
    starts_with_whitespace = tokens[0].type == TokenType.WHITESPACE
    ends_with_whitespace = tokens[-1].type == TokenType.WHITESPACE

    # transform a list of tokens to include operators
    # find the operator with the maximum whitespace between it and other things
    updated_list = [
        STR_TO_OPERATOR.get(token.value, token) if token.type != TokenType.STRING else token
        for token in tokens
    ]
    max_width, max_index = -1, -1
    bracket_layers = 0
    for i in range(len(updated_list)):
        if tokens[i].type == TokenType.L_SQUARE:
            bracket_layers += 1
        elif tokens[i].type == TokenType.R_SQUARE:
            bracket_layers -= 1
        if isinstance(updated_list[i], OperatorType) and bracket_layers == 0:
            try:
                # first check for negative sign -- this is horrible :D
                if (
                    i == 0
                    or tokens[i - 1].type == TokenType.WHITESPACE
                    and tokens[i + 1].type != TokenType.WHITESPACE
                    and updated_list[i] == OperatorType.SUB
                ):  # l_len greater than zero no matter what fr
                    continue

                # make sure whitespace is equal and then determine maxes
                l_len, r_len = 0, 0
                if tokens[i - 1].type == TokenType.WHITESPACE:
                    l_len = len(tokens[i - 1].value)
                if tokens[i + 1].type == TokenType.WHITESPACE:
                    r_len = len(tokens[i + 1].value)
                if l_len != r_len and updated_list[i] != OperatorType.COM:
                    raise_error_at_token(
                        filename,
                        code,
                        "Whitespace must be equal on either side of an operator.",
                        tokens[i],
                    )
                if r_len > max_width or (
                    r_len == max_width
                    and max_index != -1
                    and _OPERATOR_BINDING_POWER.get(updated_list[i], 0)
                    < _OPERATOR_BINDING_POWER.get(updated_list[max_index], 0)
                ):
                    max_width = r_len
                    max_index = i

            except IndexError:
                raise_error_at_token(
                    filename,
                    code,
                    "Operator cannot be at the end of an expression.",
                    tokens[i],
                )

    # detecting single argument function
    # this doesn't seem to adhere to my standards 100%, so its not a bug, its a feature
    starts_with_operator = int(tokens_without_whitespace[0].type in {TokenType.SEMICOLON, TokenType.SUBTRACT, TokenType.INCREMENT, TokenType.DECREMENT})
    first_name_index = int(starts_with_whitespace) + int(starts_with_operator)
    if (
        len(tokens) >= 3 + first_name_index
        and tokens[first_name_index].type == TokenType.NAME
        and tokens[first_name_index + 1].type == TokenType.WHITESPACE
        and tokens[first_name_index + 2].type
        in [
            TokenType.NAME,
            TokenType.L_SQUARE,
            TokenType.STRING,
            TokenType.PAREN_GROUP,
            TokenType.SUBTRACT,
            TokenType.SEMICOLON,
            TokenType.INCREMENT,
            TokenType.DECREMENT,
        ]
        and len(tokens[first_name_index + 1].value) > max_width
    ):
        function_node = FunctionNode(
            tokens[first_name_index],
            [build_expression_tree(filename, tokens[first_name_index + 1 :], code)],
        )
        if starts_with_operator:
            return SingleOperatorNode(function_node, tokens_without_whitespace[0])
        return function_node

    # check if there is an operator at the beginning of the thing
    if starts_with_operator and (
        max_index == -1
        or (t := tokens[int(starts_with_whitespace) + 1]).type == TokenType.WHITESPACE
        and len(t.value) > max_width
        or updated_list[max_index] == OperatorType.COM
    ):
        return SingleOperatorNode(
            build_expression_tree(filename, tokens[int(starts_with_whitespace) + 1 :], code),
            tokens_without_whitespace[0],
        )

    # value, like a list, name, or anything else
    if max_index == -1:
        # "value".property / "value".method() - receiver is not a name.
        # A zero-argument call is tokenised as a trailing blank name.
        meaningful = tokens_without_whitespace
        zero_arg_call = (
            len(meaningful) >= 2
            and meaningful[-1].type == TokenType.NAME
            and meaningful[-1].value == ""
        )
        if zero_arg_call:
            meaningful = meaningful[:-1]
        if (
            len(meaningful) >= 3
            and meaningful[-2].type == TokenType.DOT
            and meaningful[-1].type == TokenType.NAME
        ):
            receiver = build_expression_tree(filename, meaningful[:-2], code)
            member = meaningful[-1]
            if zero_arg_call:
                return MethodCallNode(receiver, member, [])
            return MemberAccessNode(receiver, member)

        # just making sure the input is correct
        try:
            name_or_value = tokens_without_whitespace[0]
            if name_or_value.type == TokenType.PAREN_GROUP and name_or_value.tree is not None:
                return name_or_value.tree
            if name_or_value.type not in [
                TokenType.NAME,
                TokenType.L_SQUARE,
                TokenType.STRING,
                TokenType.PAREN_GROUP,
            ]:
                raise_error_at_token(
                    filename,
                    code,
                    "Expected name or value.",
                    tokens_without_whitespace[0],
                )
        except IndexError:
            raise_error_at_token(filename, code, "Expected name or value.", tokens_without_whitespace[0])

        # this is a list :)
        if name_or_value.type == TokenType.L_SQUARE:
            bracket_layers = 1
            for i, token in enumerate(tokens_without_whitespace[1:], start=1):
                if token.type == TokenType.L_SQUARE:
                    bracket_layers += 1
                elif token.type == TokenType.R_SQUARE:
                    bracket_layers -= 1

                # this means the closing happen, signifying the end of the list
                if bracket_layers == 0:
                    if i == len(tokens_without_whitespace) - 1:
                        # let's find the most significant comma, and split by that
                        # if there's a function in the middle of the list, too bad :)
                        # [func a, b]  == [func(a), b] and also [func(a, b)]  # literally how do i tell them apart

                        # need to consider the width of whitespace from either side fr
                        l_width = (
                            len(token.value)
                            if (token := tokens[int(starts_with_whitespace) + 1]).type == TokenType.WHITESPACE
                            else 0
                        )
                        r_width = (
                            len(token.value)
                            if (token := tokens[len(tokens) - int(ends_with_whitespace) - 2]).type
                            == TokenType.WHITESPACE
                            else 0
                        )
                        if l_width != r_width:
                            raise_error_at_token(
                                filename,
                                code,
                                "Whitespace between either bracket of a list must be equal in length.",
                                tokens[len(tokens) - int(ends_with_whitespace) - 2],
                            )

                        # now go through all the commas and check if the whitespace is significant
                        all_commas = []
                        bracket_layers = 0  # yes i'm setting this damn thing twice
                        for i, (token, tok_or_op) in enumerate(
                            zip(tokens[:-1], updated_list)
                        ):  # stop here to avoid angry errors
                            if token.type == TokenType.L_SQUARE:
                                bracket_layers += 1
                            elif token.type == TokenType.R_SQUARE:
                                bracket_layers -= 1
                            if (
                                tok_or_op == OperatorType.COM
                                and bracket_layers == 1
                                and (
                                    l_width == 0
                                    or l_width == len(tokens[i + 1].value)
                                    and tokens[i + 1].type == TokenType.WHITESPACE
                                )
                            ):
                                all_commas.append(i)

                        # not single element
                        if all_commas:
                            return ListNode(
                                [
                                    build_expression_tree(filename, t, code)
                                    for t in [
                                        tokens[comma_index + 1 : next_index]
                                        for comma_index, next_index in zip(
                                            [int(starts_with_whitespace), *all_commas],
                                            [
                                                *all_commas,
                                                len(tokens) - 1 - int(ends_with_whitespace),
                                            ],
                                        )  # adjusting here in order to avoid the bracket tokens
                                    ]
                                ]
                            )

                        # single element :)
                        return ListNode(
                            [
                                build_expression_tree(
                                    filename,
                                    tokens[
                                        int(starts_with_whitespace) + 1 : len(tokens) - int(ends_with_whitespace) - 1
                                    ],
                                    code,
                                )
                            ]
                        )
                    break

        # now we need to handle indexes
        # let's go from the back of the list and find the first fully closing sequence
        # i am sure that this guarantees there is an index (i think)
        if tokens_without_whitespace[-1].type == TokenType.R_SQUARE:
            bracket_layers = -1
            end_index = len(tokens) - int(ends_with_whitespace) - 1
            for i, token in reversed(list(enumerate(tokens[:end_index]))):  # i don't like this one bit  :(
                if token.type == TokenType.L_SQUARE:
                    bracket_layers += 1
                elif token.type == TokenType.R_SQUARE:
                    bracket_layers -= 1

                # first index!!!!!!!!!!!!!!!!!!!!
                if bracket_layers == 0:
                    return IndexNode(
                        build_expression_tree(filename, tokens[int(starts_with_whitespace) : i], code),
                        build_expression_tree(filename, tokens[i + 1 : end_index], code),
                    )

        # finally end this vicious cycle
        return ValueNode(name_or_value)

    # max_index is the token with the maximum surrouding whitespace
    if updated_list[max_index] == OperatorType.COM:
        # this means it is a function
        # we need to find every other comma as they become the arguments of the function
        # additionally, there needs to be a spacing of equal length between
        # the name of the function and the next argument

        if tokens_without_whitespace[0].type != TokenType.NAME or tokens_without_whitespace[1].type not in [
            TokenType.NAME,
            TokenType.L_SQUARE,
            TokenType.STRING,
        ]:
            raise_error_at_token(
                filename,
                code,
                "Expected function call. This is likely an issue of whitespace,"
                " as Gulf of Mexico replaces parentheses with spaces"
                " and has significant whitespace.",
                tokens_without_whitespace[0],
            )

        all_commas = []
        for i in range(len(updated_list)):
            if updated_list[i].value == ",":  # okay this is weird because enums have .value and tokens have .value
                if (
                    max_width == 0
                    or (tokens[i + 1].type == TokenType.WHITESPACE and len(tokens[i + 1].value)) == max_width
                ):
                    all_commas.append(i)

        # i have no idea what the hell im doin
        return FunctionNode(
            tokens_without_whitespace[0],
            [
                build_expression_tree(filename, t, code)
                for t in [
                    tokens[comma_index + 1 : next_index]
                    for comma_index, next_index in zip(
                        [int(starts_with_whitespace), *all_commas],
                        [*all_commas, len(tokens)],
                    )
                ]
            ],
        )

    else:
        operator = updated_list[max_index]
        if not isinstance(operator, OperatorType):
            raise_error_at_token(filename, code, "Something went wrong. My bad.", tokens[max_index])
        return ExpressionNode(
            build_expression_tree(filename, tokens[:max_index], code),
            build_expression_tree(filename, tokens[max_index + 1 :], code),
            operator=operator,
            operator_token=tokens[max_index],
        )
