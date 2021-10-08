from .utils import Position, TT
from .errors import RTError
from .lexer import Lexer
from .parser import (
    CallNode,
    FuncDefNode,
    Parser,
    NumberNode,
    BinOpNode,
    UnaryOpNode,
    VarAccessNode,
    VarAssignNode,
    IfNode,
    ForNode,
    WhileNode,
)


class RTResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        if res.error:
            self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self

    def faliure(self, error):
        self.error = error
        return self


class DataType:
    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start: Position = None, pos_end: Position = None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def copy(self):
        raise Exception("NO COPIES")

    def get_type_from_value(self):
        str_value = str(self.value)
        if str_value.isnumeric():
            return Number(self.value)
        elif str_value in {"True", "False"}:
            return Bool(self.value)

    def is_true(self):
        return False

    def illegal_operation(self, other=None):
        if not other:
            other = self
        return RTError(self.pos_start, other.pos_end, "Illegal operation", self.context)

class Number(DataType):
    def __init__(self, value: int):
        self.value = value
        super().__init__()

    def copy(self):
        return Number(self.value).set_context(self.context).set_pos(self.pos_start, self.pos_end)

    def __add__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __sub__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __mul__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __truediv__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Division by zero", self.context
            )
        return Number(self.value / other.value).set_context(self.context), None

    def __floordiv__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Division by zero", self.context
            )
        return Number(self.value // other.value).set_context(self.context), None

    def __mod__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Modulo by zero", self.context
            )
        return Number(self.value % other.value).set_context(self.context), None

    def __neg__(self):
        return Number(-self.value)

    def __pow__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __eq__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value == other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __ne__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value != other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __lt__(self, other):
        if isinstance(other, (Number, Bool)):
            return Bool(self.value < other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __le__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value <= other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __gt__(self, other):
        if isinstance(other, (Number, Bool)):
            return Bool(self.value > other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __ge__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value >= other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __and__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value and other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __or__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                bool(self.value or other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __not__(self):
        return Bool(not self.value).set_context(self.context), None

    def __repr__(self):
        return str(self.value)


class Bool(DataType):
    def __init__(self, value: bool):
        self.value = value
        super().__init__()

    def __add__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __sub__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __mul__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __truediv__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Division by zero", self.context
            )
        return Number(self.value / other.value).set_context(self.context), None

    def __floordiv__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Division by zero", self.context
            )
        return Number(self.value // other.value).set_context(self.context), None

    def __mod__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Modulo by zero", self.context
            )
        return Number(self.value % other.value).set_context(self.context), None

    def __neg__(self):
        return Number(-self.value)

    def __pow__(self, other):
        return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __eq__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value == other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __ne__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value != other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __lt__(self, other):
        if isinstance(other, (Number, Bool)):
            return Bool(self.value < other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __le__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value <= other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __gt__(self, other):
        if isinstance(other, (Number, Bool)):
            return Bool(self.value > other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __ge__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value >= other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __and__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value and other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __or__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                bool(self.value or other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __not__(self):
        return Bool(not self.value).set_context(self.context), None

    def is_true(self):
        return self.value

    def copy(self):
        return Bool(self.value).set_context(self.context).set_pos(self.pos_start, self.pos_end)

    def __repr__(self):
        return str(self.value).lower()

class String(DataType):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __add__(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __mul__(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def is_true(self):
        return bool(self.value)

    def copy(self):
        return String(self.value).set_context(self.context).set_pos(self.pos_start, self.pos_end)

    def __repr__(self) -> str:
        return f"{self.value!r}"

class Function(DataType):
    def __init__(self, name, body_node: BinOpNode, arg_names: list):
        super().__init__()
        self.name = name
        self.body_node = body_node
        self.arg_names = arg_names

    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()

        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)

        if len(args) != len(self.arg_names):
            return res.faliure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    f"Function {self.name} takes in {len(self.arg_names)} but {len(args)} passed instead.",
                )
            )

        for i, arg in enumerate(args):
            arg_name = self.arg_names[i]
            arg_value = arg
            arg_value.set_context(new_context)
            new_context.symbol_table.set(arg_name, arg_value)

        value = res.register(interpreter.visit(self.body_node, new_context))
        if res.error:
            return res

        return res.success(value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"


class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent: dict = None

    def get(self, name):
        value = self.symbols.get(name)
        if value is None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name: str, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]


class Context:
    def __init__(self, display_name: str, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table: SymbolTable = None


class Interpreter:
    def visit(self, node, context: Context) -> RTResult:
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node):
        raise Exception(f"No visit_{type(node).__name__}")

    def visit_NumberNode(self, node: NumberNode, context: Context):
        return RTResult().success(
            Number(node.tok.value)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_BoolNode(self, node: NumberNode, context: Context):
        return RTResult().success(
            Bool(node.tok.value)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_StringNode(self, node: NumberNode, context: Context):
        return RTResult().success(
            String(node.tok.value)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_VarAccessNode(self, node: VarAccessNode, context: Context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.faliure(
                RTError(
                    node.pos_start,
                    node.pos_end,
                    f"'{var_name}' is not defined",
                    context,
                )
            )

        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(value)

    def visit_VarAssignNode(self, node: VarAssignNode, context: Context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error:
            return res

        context.symbol_table.set(var_name, value)
        return res.success(None)

    def visit_BinOpNode(
        self, node: BinOpNode, context: Context
    ) -> Number:  # sourcery no-metrics
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error:
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.error:
            return res

        if node.op_tok.type == TT.PLUS:
            result, error = left + right
        elif node.op_tok.type == TT.MINUS:
            result, error = left - right
        elif node.op_tok.type == TT.MULT:
            result, error = left * right
        elif node.op_tok.type == TT.DIV:
            result, error = left / right
        elif node.op_tok.type == TT.FDIV:
            result, error = left // right
        elif node.op_tok.type == TT.MODU:
            result, error = left % right
        elif node.op_tok.type == TT.POW:
            result, error = left ** right
        elif node.op_tok.type == TT.EE:
            result, error = left == right
        elif node.op_tok.type == TT.NE:
            result, error = left != right
        elif node.op_tok.type == TT.LT:
            result, error = left < right
        elif node.op_tok.type == TT.GT:
            result, error = left > right
        elif node.op_tok.type == TT.LTE:
            result, error = left <= right
        elif node.op_tok.type == TT.GTE:
            result, error = left >= right
        elif node.op_tok.matches(TT.KEYWORD, "and"):
            result, error = left.__and__(right)
        elif node.op_tok.matches(TT.KEYWORD, "or"):
            result, error = left.__or__(right)

        if error:
            return res.faliure(error)

        return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node: UnaryOpNode, context: Context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error:
            return res

        error = None

        if node.op_tok.type == TT.MINUS:
            number, error = -number
        elif node.op_tok.matches(TT.KEYWORD, "not"):
            number, error = number.__not__()

        if error:
            return res
        return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_IfNode(self, node: IfNode, context=None):
        res = RTResult()

        for condition, expr in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error:
                return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.error:
                    return res
                return res.success(expr_value)

        if node.else_case:
            else_value = res.register(self.visit(node.else_case, context))
            if res.error:
                return res
            return res.success(else_value)

        return res.success(None)

    def visit_ForNode(self, node: ForNode, context: Context):
        res = RTResult()

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.error:
            return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.error:
            return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.error:
                return res
        else:
            step_value = Number(1)

        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value

            res.register(self.visit(node.body_node, context))
            if res.error:
                return res

        return res.success(None)

    def visit_WhileNode(self, node: WhileNode, context: Context):
        res = RTResult()

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.error:
                return res

            if not condition.is_true():
                break

            res.register(self.visit(node.body_node, context))
            if res.error:
                return res

        return res.success(None)

    def visit_FuncDefNode(self, node: FuncDefNode, context: Context):
        res = RTResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        func_value = (
            Function(func_name, body_node, arg_names)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)

    def visit_CallNode(self, node: CallNode, context: Context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.error:
            return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.error:
                return res

        return_value = res.register(value_to_call.execute(args))
        if res.error:
            return res
        return res.success(return_value)


global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))


def run(fn: str, text: str):
    # Generate Tokens
    lexer = Lexer(text, fn)
    tokens, error = lexer.make_tokens()
    # return tokens, error
    if error:
        return None, error
    if not tokens:
        return None, error

    # Generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    # return ast.node, ast.error
    if ast.error:
        return None, ast.error

    # Get Interpreter
    interpreter = Interpreter()
    context = Context("<program>")
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    if str(result.value) in {"True", "False"}:
        result.value = str(result.value).lower()

    return result.value, result.error