import ast
import inspect
import textwrap
from types import FunctionType

from TeaLeaf.Magic.JSCode import JSCode

console = JSCode("console")
document = JSCode("document")
false = False
true = True
window = JSCode("window")
alert = JSCode("alert")


class JSFunction():
    def __init__(self,name: str, raw: str):
        super().__init__()
        self.name = name
        self.raw = raw

    def __str__(self):
        return self.raw

    def __call__(self, *args):
        return JSCode(f"{self.name}")(*args)


class PythonToJS(ast.NodeVisitor):

    def __init__(self) -> None:
        super().__init__()
        self.declarations = []


    def generic_visit(self, node):
         ast.NodeVisitor.generic_visit(self, node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        header = f"function {node.name}({', '.join([arg.arg for arg in node.args.args])}) {{"
        body = ""
        for stmt in node.body:
            string_stmt = self.visit(stmt)
            if string_stmt:
                body += "\t" + string_stmt + "\n"
            else:
                print(stmt)
        return header + "\n" + body + "}\n"

    def visit_arg(self, node: ast.arg):
        return node.arg


    def visit_arguments(self, node: ast.arguments):
        for arg in node.args:
                self.visit(arg)


    def visit_Name(self, node: ast.Name):
        return node.id

    def visit_If(self, node: ast.If):
        test = self.visit(node.test)
        body = ""
        for stmt in node.body:
            self.visit(stmt)
            body += "\n\t" + self.visit(stmt)
        orelse = "\n\t".join([self.visit(stmt) for stmt in node.orelse])
        return f"if ({test}) {{\n\t{body}\n}} else {{\n\t{orelse}\n}}"

    def visit_Compare(self, node: ast.Compare):
        left = self.visit(node.left)
        ops = [self.visit(op) for op in node.ops]
        comparators = [self.visit(comp) for comp in node.comparators]
        return f"{left} {' '.join(ops)} {' '.join(comparators)}"


    def visit_Gt(self, node: ast.Gt):
        return ">"

    def visit_Lt(self, node: ast.Lt):
        return "<"

    def visit_Eq(self, node: ast.Eq):
        return "=="

    def visit_NotEq(self, node: ast.NotEq):
        return "!="



    def visit_Constant(self, node: ast.Constant):
        kind = type(node.value).__name__
        if kind == "str":
            return f'"{node.value}"'
        elif kind == "bool":
            return str(node.value).lower()
        elif kind == "int":
            return str(node.value)
        elif kind == "float":
            return str(node.value)

    def visit_Dict(self, node: ast.Dict):
        keys = [self.visit(key) if key else "null" for key in node.keys]
        values = [self.visit(value) for value in node.values]
        return f"{{{', '.join([f'{k}: {v}' for k, v in zip(keys, values)])}}}"

    def visit_Expr(self, node: ast.Expr):
        return self.visit(node.value)



    def visit_Assign(self, node: ast.Assign):
        name = self.visit(node.targets[0])
        value = self.visit(node.value)
        prefix = ""
        if isinstance(node.targets[0], ast.Name):
            if name not in self.declarations:
                prefix = "let   "
                self.declarations.append(name)
        return f"{prefix}{name} = {value};"


    def visit_Attribute(self, node: ast.Attribute):
        return f"{self.visit(node.value)}.{node.attr}"

    def visit_Call(self, node: ast.Call):
        args = [self.visit(arg) for arg in node.args] or []
        call =  f"{self.visit(node.func)}({', '.join(args)})"
        return call


    # visit_If, visit_BoolOp, etc...

def js(fn: FunctionType):
    src = textwrap.dedent(inspect.getsource(fn))
    lines = src.splitlines()
    lines = [l for l in lines if not l.strip().startswith("@js")]
    src = "\n".join(lines)


    tree = ast.parse(src).body[0]


    visitor = PythonToJS()
    visitor.declarations = ["console", "document"]
    result = visitor.visit(tree)
    return JSFunction(fn.__name__, result)

    # js_code = transformer.generate(tree)
    # return JSCode(js_code)



@js
def test_fn(mensaje: str):
    saludo = "hello"
    edad = 30
    admin = True
    console.log(saludo)
    document.getElementById("test").value = ""
    value = "hello"
    if edad > 18:
        console.log(saludo)
    else:
        console.log("hello")




if __name__ == "__main__":
    print(test_fn)
