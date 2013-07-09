from __future__ import unicode_literals

import re
from random import choice
from parsimonious.exceptions import IncompleteParseError
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from inflector import Inflector

from radlibs.lib import load_lib
from radlibs.english.irregular_past_verbs import irregular_past_verbs
from radlibs.english.indefinite_article import indefinite_article_for_noun

recursion = {'depth': 0}

grammar = Grammar("""
    contents = rad*
    rad       = (word indicator?) / (lib indicator?) / whitespace
    lib       = "<" modifier* lib_name ">" inflector?
    modifier  = "!"
    lib_name  = ~"[A-Z]" ~"[a-z_]*"
    word      = literal / letter+
    whitespace = ~"[\s]"
    indicator = "^"
    inflector = "d" / "s"
    letter    = ~"[^^<>\s\\\\\\]"
    literal   = "\\<" / "\\>" / "\\d" / "\\^" / "\\s"
""")


class ParseError(StandardError):
    pass


class Node(object):
    indicated = False

    def append(self, child):
        raise NotImplementedError('append')

    def __str__(self):
        raise NotImplementedError('__str__')

    def __eq__(self, other):
        return unicode(self) == other

    def __repr__(self):
        return "{0}: '{1}'".format(type(self), unicode(self))

    def indicate(self):
        self.indicated = True

    def past_tense(self):
        raise NotImplementedError('past_tense')

    def plural(self):
        raise NotImplementedError('plural')


class Rad(Node):
    children = None
    modifier = None

    def __init__(self):
        self.children = []

    def append(self, child):
        self.children.append(child)
        if self.modifier:
            child.modify(self.modifier)
            self.modifier = None

    def __str__(self):
        terms = []
        for child in self.children:
            if self.modifier is not None:
                child.modify(self.modifier)
            expanded = unicode(child)
            if type(child) == Lib:
                try:
                    antecedent = terms[-2]
                    if antecedent in ['a', 'an']:
                        terms[-2] = indefinite_article_for_noun(expanded)
                except IndexError:
                    pass
            terms.append(expanded)
        return ''.join(terms)

    def __repr__(self):
        return ''.join([repr(child) for child in self.children])

    def indicated_or_last(self):
        for i, child in enumerate(self.children):
            if child.indicated or (i + 1 == len(self.children)):
                return child

    def modify(self, modifier):
        self.modifier = modifier


class Text(Node):
    characters = None

    def __init__(self, initial):
        self.characters = [initial]

    def append(self, text):
        self.characters.append(unicode(text))

    def __str__(self):
        return ''.join(self.characters)

    def __repr__(self):
        return ''.join(self.characters)

    def __hash__(self):
        return unicode(self).__hash__()

    def override(self, new_text):
        self.characters = [new_text]

    def past_tense(self):
        if self in irregular_past_verbs:
            self.override(irregular_past_verbs[self])
        else:
            last_letter = self.characters[-1][-1]
            if re.match(r'[bcdfghjklmnpqrstvwxz]', last_letter):
                self.append('ed')
            elif last_letter == 'y':
                self.override(re.sub('y$', 'ied', unicode(self)))
            else:
                self.append('d')

    def plural(self):
        self.override(Inflector().pluralize(unicode(self)))

    def modify(self, modifier):
        if modifier == '!':
            self.override(unicode(self).upper())


PAST_TENSE = 'past'
PRESENT_TENSE = 'present'


class Lib(Node):
    lib = None
    lib_name = None
    tense = PRESENT_TENSE
    is_plural = False
    modifier = None

    def __init__(self, lib_name):
        self.lib_name = lib_name

    def __str__(self):
        if recursion['depth'] > 20:
            return self.lib_name
        lib = load_lib(self.lib_name)
        try:
            recursion['depth'] += 1
            sub_rad = parse(choice(lib))
            if self.modifier is not None:
                sub_rad.modify(self.modifier)

            if self.tense == PAST_TENSE:
                word = sub_rad.indicated_or_last()
                word.past_tense()

            if self.is_plural:
                word = sub_rad.indicated_or_last()
                word.plural()

            return unicode(sub_rad)
        except ParseError as e:
            error = "{0} (found inside {1})".format(e.message, self.lib_name)
            raise ParseError(error)
        finally:
            recursion['depth'] -= 1

    def past_tense(self):
        self.tense = PAST_TENSE

    def plural(self):
        self.is_plural = True

    def __repr__(self):
        return '<{0}>'.format(self.lib_name)

    def modify(self, modifier):
        self.modifier = modifier


class RadParser(NodeVisitor):
    def __init__(self, text):
        self.rad = Rad()
        ast = grammar.parse(text)
        self.visit(ast)

    def generic_visit(self, node, visited_children):
        pass

    def visit_word(self, node, visited_children):
        if node.children[0].expr_name != 'literal':
            self.rad.append(Text(node.text))

    def visit_literal(self, node, visited_children):
        literal = node.text.replace('\\', '')
        self.rad.append(Text(literal))

    def visit_whitespace(self, node, visited_children):
        self.rad.append(Text(node.text))

    def visit_lib_name(self, node, visited_children):
        self.rad.append(Lib(node.text))

    def visit_modifier(self, node, visited_children):
        self.rad.modify(node.text)

    def visit_inflector(self, node, visited_children):
        if node.text == 'd':
            self.rad.children[-1].past_tense()
        elif node.text == 's':
            self.rad.children[-1].plural()
        else:
            raise ParseError("Unknown inflector '{0}'".format(node.text))

    def visit_indicator(self, node, visited_children):
        self.rad.children[-1].indicate()


def parse(plaintext):
    try:
        return RadParser(plaintext).rad
    except IncompleteParseError as e:
        lines = e.text.split("\n")
        error = "Unexpected token '{0}' at line {1} character {2} of '{3}'".\
            format(lines[e.line() - 1][e.pos],
                   e.line(),
                   e.pos + 1,
                   e.text)
        raise ParseError(error)
