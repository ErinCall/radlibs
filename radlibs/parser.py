from __future__ import unicode_literals

from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor

from radlibs.lib import load_lib

grammar = Grammar("""
    contents     = rad*
    rad          = letter+ / lib
    lib          = "<" lib_name ">"
    lib_name     = ~"[A-Z]" ~"[a-z_]*"
    letter       = anglebracket / ~"[^<>]"
    anglebracket = "\\<" / "\\>"
""")


class Node(object):
    def append(self, child):
        raise NotImplementedError('append')

    def __str__(self):
        raise NotImplementedError('__str__')

    def __eq__(self, other):
        return str(self) == other

    def __repr__(self):
        return "{0}: '{1}'".format(type(self), str(self))


class Rad(Node):
    children = None

    def __init__(self):
        self.children = []

    def append(self, child):
        if self.children and \
                type(child) == Text and \
                type(self.children[-1]) == Text:
            self.children[-1].append(child)
        else:
            self.children.append(child)

    def __str__(self):
        return ''.join([str(child) for child in self.children])


class Text(Node):
    characters = None

    def __init__(self, initial):
        self.characters = [initial]

    def append(self, text):
        self.characters.append(str(text))

    def __str__(self):
        return ''.join(self.characters)


class Lib(Node):
    lib = None
    lib_name = None

    def __init__(self, lib_name):
        self.lib_name = lib_name
        self.lib = load_lib(lib_name)

    def __str__(self):
        return self.lib_name


class RadParser(NodeVisitor):
    def __init__(self, text):
        self.rad = Rad()
        ast = grammar.parse(text)
        self.visit(ast)

    def visit_contents(self, node, visited_children):
        pass

    def generic_visit(self, node, visited_children):
        pass

    def visit_letter(self, node, visited_children):
        character_node = node.children[0]
        if character_node.expr_name == 'anglebracket':
            self.rad.append(Text(character_node.text.replace('\\', '')))
        else:
            self.rad.append(Text(character_node.text))

    def visit_lib_name(self, node, visited_children):
        self.rad.append(Lib(node.text))


def parse(plaintext):
    return RadParser(plaintext).rad
