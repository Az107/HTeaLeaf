import ast
from typing import Optional

# ---------------------------------------------------------------------------
# Scope
# ---------------------------------------------------------------------------

class Scope:
    """Tracks declared variables per lexical scope."""

    def __init__(self, parent: Optional["Scope"] = None):
        self.parent = parent
        self.declared: set[str] = set()

    def is_declared(self, name: str) -> bool:
        if name in self.declared:
            return True
        return self.parent.is_declared(name) if self.parent else False

    def declare(self, name: str) -> None:
        self.declared.add(name)


# ---------------------------------------------------------------------------
# Transpiler
# ---------------------------------------------------------------------------

class PythonToJS(ast.NodeVisitor):

    def __init__(self, replace_map: dict[str, str] = {}) -> None:
        super().__init__()
        self.replace_map = replace_map
        self.scope = Scope()

    # -- Scope helpers -------------------------------------------------------

    def _push_scope(self) -> None:
        self.scope = Scope(parent=self.scope)

    def _pop_scope(self) -> None:
        assert self.scope.parent is not None, "Cannot pop root scope"
        self.scope = self.scope.parent

    def _declare(self, name: str) -> str:
        """Return 'let ' if first declaration in current scope, else ''."""
        if not self.scope.is_declared(name):
            self.scope.declare(name)
            return "let "
        return ""

    # -- Indentation helper --------------------------------------------------

    def _indent(self, code: str, level: int = 1) -> str:
        pad = "\t" * level
        return "\n".join(pad + line for line in code.splitlines())

    # -- Body helper ---------------------------------------------------------

    def _emit_body(self, stmts: list[ast.stmt]) -> str:
        lines = []
        for stmt in stmts:
            result = self.visit(stmt)
            if result is not None:
                lines.append(result)
            else:
                # Useful during development to catch unhandled nodes
                lines.append(f"/* TODO: {type(stmt).__name__} */")
        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # Fallback
    # -----------------------------------------------------------------------

    def generic_visit(self, node: ast.AST):
        raise NotImplementedError(
            f"Unhandled node type: {type(node).__name__}\n{ast.dump(node)}"
        )

    # -----------------------------------------------------------------------
    # Statements
    # -----------------------------------------------------------------------

    def visit_Expr(self, node: ast.Expr) -> str:
        return self.visit(node.value) + ";"

    def visit_Assign(self, node: ast.Assign) -> str:
        target = node.targets[0]
        name = self.visit(target)
        value = self.visit(node.value)

        prefix = self._declare(name) if isinstance(target, ast.Name) else ""
        return f"{prefix}{name} = {value};"

    def visit_AugAssign(self, node: ast.AugAssign) -> str:
        target = self.visit(node.target)
        op = self.visit(node.op)
        value = self.visit(node.value)
        return f"{target} {op}= {value};"

    def visit_AnnAssign(self, node: ast.AnnAssign) -> str:
        # Type annotations are discarded; treat as plain assignment
        name = self.visit(node.target)
        if node.value is None:
            return f"let {name};"
        value = self.visit(node.value)
        prefix = self._declare(name) if isinstance(node.target, ast.Name) else ""
        return f"{prefix}{name} = {value};"

    def visit_Return(self, node: ast.Return) -> str:
        if node.value is None:
            return "return;"
        return f"return {self.visit(node.value)};"

    def visit_If(self, node: ast.If) -> str:
        test = self.visit(node.test)
        body = self._indent(self._emit_body(node.body))
        result = f"if ({test}) {{\n{body}\n}}"
        if node.orelse:
            # elif becomes a nested If in the AST
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                result += f" else {self.visit(node.orelse[0])}"
            else:
                orelse = self._indent(self._emit_body(node.orelse))
                result += f" else {{\n{orelse}\n}}"
        return result

    def visit_While(self, node: ast.While) -> str:
        test = self.visit(node.test)
        body = self._indent(self._emit_body(node.body))
        return f"while ({test}) {{\n{body}\n}}"

    def visit_For(self, node: ast.For) -> str:
        target = self.visit(node.target)
        iter_ = self.visit(node.iter)
        self._push_scope()
        self.scope.declare(target)
        body = self._indent(self._emit_body(node.body))
        self._pop_scope()
        return f"for (const {target} of {iter_}) {{\n{body}\n}}"

    def visit_Break(self, node: ast.Break) -> str:
        return "break;"

    def visit_Continue(self, node: ast.Continue) -> str:
        return "continue;"

    def visit_FunctionDef(self, node: ast.FunctionDef) -> str:
        params = ", ".join(arg.arg for arg in node.args.args)
        self._push_scope()
        # Parameters count as declared in function scope
        for arg in node.args.args:
            self.scope.declare(arg.arg)
        body = self._indent(self._emit_body(node.body))
        self._pop_scope()
        return f"function {node.name}({params}) {{\n{body}\n}}\n"

    # Async functions — emit as async JS functions
    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    # -----------------------------------------------------------------------
    # Expressions
    # -----------------------------------------------------------------------

    def visit_Name(self, node: ast.Name) -> str:
        if node.id in self.replace_map:
            return self.replace_map[node.id]
        return node.id

    def visit_Attribute(self, node: ast.Attribute) -> str:
        return f"{self.visit(node.value)}.{node.attr}"

    def visit_Call(self, node: ast.Call) -> str:
        func = self.visit(node.func)
        args = [self.visit(arg) for arg in node.args]
        # keyword args as trailing object literal
        if node.keywords:
            kwargs = ", ".join(
                f"{kw.arg}: {self.visit(kw.value)}" for kw in node.keywords if kw.arg
            )
            args.append(f"{{{kwargs}}}")
        return f"{func}({', '.join(args)})"

    def visit_Constant(self, node: ast.Constant) -> str:
        return self._emit_constant(node, raw=False)

    def _emit_constant(self, node: ast.Constant, raw: bool) -> str:
        kind = type(node.value).__name__
        if kind == "str":
            return str(node.value) if raw else f'"{node.value}"'
        if kind == "bool":
            return str(node.value).lower()
        if kind == "NoneType":
            return "null"
        return str(node.value)  # int, float

    def visit_JoinedStr(self, node: ast.JoinedStr) -> str:
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant):
                parts.append(self._emit_constant(value, raw=True))
            elif isinstance(value, ast.FormattedValue):
                parts.append(self.visit(value))
            else:
                parts.append(self.visit(value))
        return f"`{''.join(parts)}`"

    def visit_FormattedValue(self, node: ast.FormattedValue) -> str:
        return f"${{{self.visit(node.value)}}}"

    # -- Collections ---------------------------------------------------------

    def visit_List(self, node: ast.List) -> str:
        elts = ", ".join(self.visit(e) for e in node.elts)
        return f"[{elts}]"

    def visit_Tuple(self, node: ast.Tuple) -> str:
        # Tuples become arrays in JS
        return self.visit_List(node)  # type: ignore[arg-type]

    def visit_Dict(self, node: ast.Dict) -> str:
        pairs = []
        for key, value in zip(node.keys, node.values):
            k = "null" if key is None else self.visit(key)
            pairs.append(f"{k}: {self.visit(value)}")
        return f"{{{', '.join(pairs)}}}"

    def visit_Subscript(self, node: ast.Subscript) -> str:
        return f"{self.visit(node.value)}[{self.visit(node.slice)}]"

    # -- Operators -----------------------------------------------------------

    def visit_BinOp(self, node: ast.BinOp) -> str:
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = self.visit(node.op)
        if isinstance(node.op, ast.FloorDiv):
            return f"Math.floor({left} / {right})"
        if isinstance(node.op, ast.Pow):
            return f"Math.pow({left}, {right})"
        return f"{left} {op} {right}"

    def visit_UnaryOp(self, node: ast.UnaryOp) -> str:
        op = self.visit(node.op)
        operand = self.visit(node.operand)
        return f"{op}{operand}"

    def visit_BoolOp(self, node: ast.BoolOp) -> str:
        op = self.visit(node.op)
        return f" {op} ".join(self.visit(v) for v in node.values)

    def visit_Compare(self, node: ast.Compare) -> str:
        parts = [self.visit(node.left)]
        for op, comp in zip(node.ops, node.comparators):
            parts.append(self.visit(op))
            parts.append(self.visit(comp))
        return " ".join(parts)

    # Arithmetic ops
    def visit_Add(self, node: ast.Add) -> str:         return "+"
    def visit_Sub(self, node: ast.Sub) -> str:         return "-"
    def visit_Mult(self, node: ast.Mult) -> str:       return "*"
    def visit_Div(self, node: ast.Div) -> str:         return "/"
    def visit_Mod(self, node: ast.Mod) -> str:         return "%"
    def visit_FloorDiv(self, node: ast.FloorDiv) -> str: return "/"  # handled in BinOp
    def visit_Pow(self, node: ast.Pow) -> str:         return "**"   # handled in BinOp

    # Unary ops
    def visit_USub(self, node: ast.USub) -> str:       return "-"
    def visit_UAdd(self, node: ast.UAdd) -> str:       return "+"
    def visit_Not(self, node: ast.Not) -> str:         return "!"
    def visit_Invert(self, node: ast.Invert) -> str:   return "~"

    # Comparison ops
    def visit_Eq(self, node: ast.Eq) -> str:           return "==="
    def visit_NotEq(self, node: ast.NotEq) -> str:     return "!=="
    def visit_Lt(self, node: ast.Lt) -> str:           return "<"
    def visit_LtE(self, node: ast.LtE) -> str:        return "<="
    def visit_Gt(self, node: ast.Gt) -> str:           return ">"
    def visit_GtE(self, node: ast.GtE) -> str:        return ">="
    def visit_Is(self, node: ast.Is) -> str:           return "==="
    def visit_IsNot(self, node: ast.IsNot) -> str:    return "!=="

    # Boolean ops
    def visit_And(self, node: ast.And) -> str:         return "&&"
    def visit_Or(self, node: ast.Or) -> str:           return "||"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def transpile(source: str, replace_map: dict[str, str] = {}) -> str:
    tree = ast.parse(source)
    visitor = PythonToJS(replace_map)
    parts = []
    for node in tree.body:
        result = visitor.visit(node)
        if result:
            parts.append(result)
    return "\n".join(parts)



# if __name__ == "__main__":
#     import sys
#     src = sys.stdin.read() if len(sys.argv) == 1 else open(sys.argv[1]).read()
#     print(transpile(src))
