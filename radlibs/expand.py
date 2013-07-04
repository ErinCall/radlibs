from __future__ import unicode_literals

from random import choice
from radlibs.parser import parse, Lib


def expand(plaintext, depth=0):
    rad = parse(plaintext)
    chunks = []
    for node in rad.children:
        if type(node) == Lib:
            if depth > 20:
                chunks.append(node)
                continue
            subtext = choice(node.lib)
            chunks.append(expand(subtext, depth=depth+1))
        else:
            chunks.append(node)
    return ''.join([str(c) for c in chunks])
