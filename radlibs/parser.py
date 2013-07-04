from __future__ import unicode_literals

from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


grammar = Grammar("""
    contents     = rad*
    rad          = text / lib
    lib          = "<" lib_name ">"
    lib_name     = ~"[A-Z]" ~"[a-z_]*"
    text         = letter+
    letter       = anglebracket / ~"[^<>]"
    anglebracket = "\\<" / "\\>"
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
        letters = []
        for child in node.children:
            character_node = child.children[0]
            if character_node.expr_name == 'anglebracket':
                letters.append(character_node.text.replace('\\', ''))
            else:
                letters.append(character_node.text)
        self.rad.append(Text(''.join(letters)))

    def visit_lib_name(self, node, visited_children):
        self.rad.append(Lib(node.text))


def parse(plaintext):
    return RadParser(plaintext).rad
