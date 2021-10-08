from .lexer import Token
from .utils import TT
from .errors import InvalidSyntaxError


class NumberNode:
    def __init__(self, tok: Token):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f"{self.tok}"

class BoolNode:
    def __init__(self, tok: Token):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f"{self.tok}"

class StringNode:
    def __init__(self, tok: Token):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f"{self.tok}"

class VarAccessNode:
    def __init__(self, var_name_tok: Token):
        self.var_name_tok = var_name_tok

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end


class VarAssignNode:
    def __init__(self, var_name_tok: Token, value_node: NumberNode):
        self.var_name_tok = var_name_tok
        self.value_node = value_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end


class BinOpNode:
    def __init__(self, left_node: NumberNode, op_tok: Token, right_node: NumberNode):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f"({self.left_node}, {self.op_tok}, {self.right_node})"


class UnaryOpNode:
    def __init__(self, op_tok: Token, node: NumberNode):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f"({self.op_tok}, {self.node})"


class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0

    def register_advancement(self):
        self.advance_count += 1

    def register(self, res):
        self.advance_count += res.advance_count
        if res.error:
            self.error = res.error
        return res.node

    def success(self, node):
        self.node = node
        return self

    def faliure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self


class IfNode:
    def __init__(self, cases: list[tuple[BinOpNode]], else_case: BinOpNode):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[-1][0]).pos_end


class ForNode:
    def __init__(
        self,
        var_name_tok: Token,
        start_value_node: BinOpNode,
        end_value_node: BinOpNode,
        step_value_node: BinOpNode,
        body_node: BinOpNode,
    ):
        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end


class WhileNode:
    def __init__(self, condition_node: BinOpNode, body_node: BinOpNode):
        self.condition_node = condition_node
        self.body_node = body_node

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end

class FuncDefNode:
    def __init__(self, var_name_tok: Token, arg_name_toks: list[Token], body_node: BinOpNode):
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node

        if var_name_tok:
            self.pos_start = self.var_name_tok.pos_start
        elif len(self.arg_name_toks) > 0:
            self.pos_start = self.arg_name_toks[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end

class CallNode:
    def __init__(self, node_to_call: FuncDefNode, arg_nodes: list[BinOpNode]):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = self.node_to_call.pos_start

        if self.arg_nodes:
            self.pos_end = self.arg_nodes[-1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expr()
        if res.error and self.current_tok.type != TT.EOF:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    'Expected "+", "-", "*" or "/".',
                )
            )
        return res

    def power(self):
        return self.bin_op(self.call, (TT.POW,), self.factor)

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error: return res

        if self.current_tok.type == TT.LPAR:
            res.register_advancement()
            self.advance()

            if self.current_tok.type == TT.RPAR:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes = [res.register(self.expr())]

                if res.error: return res.faliure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ')', 'var', 'if', 'for', 'while', 'fun', int, float, bool, identifier or '("
                    )
                )

                while self.current_tok.type == TT.COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

            if self.current_tok.type != TT.RPAR:
                return res.faliure(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected ',' or ')'"
                )

            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT.INT, TT.FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type in (TT.BOOL):
            res.register_advancement()
            self.advance()
            return res.success(BoolNode(tok))

        elif tok.type in (TT.STRING):
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))

        elif tok.type == TT.IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.type == TT.LPAR:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type != TT.RPAR:
                return res.faliure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        'Expected ")"',
                    )
                )

            res.register_advancement()
            self.advance()
            return res.success(expr)

        elif tok.matches(TT.KEYWORD, "if"):
            if_expr = res.register(self.if_expr())
            if res.error:
                return res
            return res.success(if_expr)

        elif tok.matches(TT.KEYWORD, "for"):
            for_expr = res.register(self.for_expr())
            if res.error:
                return res
            return res.success(for_expr)

        elif tok.matches(TT.KEYWORD, "while"):
            while_expr = res.register(self.while_expr())
            if res.error:
                return res
            return res.success(while_expr)

        elif tok.matches(TT.KEYWORD, "func"):
            func_def = res.register(self.func_def())
            if res.error:
                return res
            return res.success(func_def)

        return res.faliure(
            InvalidSyntaxError(
                tok.pos_start,
                tok.pos_end,
                "Expected int, float, identifier, '+', '-', '(', 'if', 'for', 'while' or 'func'",
            )
        )

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT.PLUS, TT.MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))
        return self.power()

    def term(self):
        return self.bin_op(self.factor, (TT.MULT, TT.DIV, TT.FDIV, TT.MODU))

    def arith_expr(self):
        return self.bin_op(self.term, (TT.PLUS, TT.MINUS))

    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT.KEYWORD, "not"):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))

        node = res.register(
            self.bin_op(self.arith_expr, (TT.EE, TT.NE, TT.LT, TT.GT, TT.LTE, TT.GTE))
        )

        if res.error:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected int, float, identifier, '+', '-', '(' or 'not'",
                )
            )

        return res.success(node)

    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TT.KEYWORD, "if"):
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'if'",
                )
            )

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TT.KEYWORD, "then"):
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'then'",
                )
            )

        res.register_advancement()
        self.advance()

        expr = res.register(self.expr())
        if res.error:
            return res
        cases.append((condition, expr))

        while self.current_tok.matches(TT.KEYWORD, "elif"):
            res.register_advancement()
            self.advance()

            condition = res.register(self.expr())
            if res.error:
                return res

            if not self.current_tok.matches(TT.KEYWORD, "then"):
                return res.faliure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected 'then'",
                    )
                )

            res.register_advancement()
            self.advance()

            expr = res.register(self.expr())
            if res.error:
                return res
            cases.append((condition, expr))

        if self.current_tok.matches(TT.KEYWORD, "else"):
            res.register_advancement()
            self.advance()

            else_case = res.register(self.expr())
            if res.error:
                return res

        return res.success(IfNode(cases, else_case))

    def for_expr(self):
        res = ParseResult()
        if not self.current_tok.matches(TT.KEYWORD, "for"):
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'for'",
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT.IDENTIFIER:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected identifier",
                )
            )

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT.EQ:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected '='"
                )
            )

        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TT.KEYWORD, "to"):
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'to'",
                )
            )

        res.register_advancement()
        self.advance()

        end_value = res.register(self.expr())
        if res.error:
            return res

        if self.current_tok.matches(TT.KEYWORD, "step"):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expr())
            if res.error:
                return res
        else:
            step_value = None

        if not self.current_tok.matches(TT.KEYWORD, "then"):
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'then'",
                )
            )

        res.register_advancement()
        self.advance()

        body = res.register(self.expr())
        if res.error:
            return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body))

    def while_expr(self):
        res = ParseResult()
        if not self.current_tok.matches(TT.KEYWORD, "while"):
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'while'",
                )
            )

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.matches(TT.KEYWORD, "then"):
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected 'then'"
                )
            )

        res.register_advancement()
        self.advance()

        body = res.register(self.expr())
        if res.error: return res

        return res.success(WhileNode(condition, body))

    def func_def(self):
        res = ParseResult()

        if not self.current_tok.matches(TT.KEYWORD, "func"):
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Excpected 'func'"
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT.IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT.LPAR:
                return res.faliure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, "Expected '('"
                    )
                )
        else:
            var_name_tok = None
            if self.current_tok.type != TT.LPAR:
                return res.faliure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, "Expected identifier or '('"
                    )
                )

        res.register_advancement()
        self.advance()

        arg_name_toks = []

        if self.current_tok.type == TT.IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type == TT.COMMA:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TT.IDENTIFIER:
                    return res.faliure(
                        InvalidSyntaxError(
                            self.current_tok.pos_start, self.current_tok.pos_end, "Expected identifier"
                        )
                    )

                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TT.RPAR:
                return res.faliure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, "Expected ',' or  ')'"
                    )
                )

        elif self.current_tok.type != TT.RPAR:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected identifier or ')'"
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT.ARROW:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected '->'"
                )
            )

        res.register_advancement()
        self.advance()

        node_to_return = res.register(self.expr())
        if res.error: return res

        return res.success(
            FuncDefNode(
                var_name_tok, 
                arg_name_toks,
                node_to_return
            )
        )

    def expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT.KEYWORD, "var"):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT.IDENTIFIER:
                return res.faliure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected identifier",
                    )
                )

            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT.EQ:
                return res.faliure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected '='",
                    )
                )

            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            return res.success(VarAssignNode(var_name, expr))

        node = res.register(
            self.bin_op(self.comp_expr, ((TT.KEYWORD, "and"), (TT.KEYWORD, "or")))
        )

        if res.error:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'var', 'for', 'while', 'func', int, float, identifier, '+', '-' or '('",
                )
            )

        return res.success(node)

    def bin_op(self, func_a: callable, ops: tuple[Token], func_b=None):
        if func_b is None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        if res.error:
            return res

        while (
            self.current_tok.type in ops
            or (self.current_tok.type, self.current_tok.value) in ops
        ):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)