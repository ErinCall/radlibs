from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


grammar = Grammar("""
    contents = text* lib* text*
    lib      = "<" lib_name ">"
    lib_name = ~"[A-Z]" ~"[a-z_]*"
    text     = ~"[A-Z 0-9,']*"i
""")


class Rad(list):
    pass


class Text(str):
    pass


class Lib(str):
    pass


class RadParser(NodeVisitor):
    def __init__(self, text):
        self.rad = Rad()
        ast = grammar.parse(text)
        self.visit(ast)

    def visit_contents(self, node, visited_children):
        pass

    def generic_visit(self, node, visited_children):
        pass

    def visit_text(self, node, visited_children):
        self.rad.append(Text(node.text))

    def visit_lib_name(self, node, visited_children):
        self.rad.append(Lib(node.text))


def parse(plaintext):
    return RadParser(plaintext).rad
