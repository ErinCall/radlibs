from __future__ import unicode_literals

# this is a port of perl's Lingua::EN::Inflect indefinite article logic.
#c.f. http://cpansearch.perl.org/src/DCONWAY/Lingua-EN-Inflect-1.895/lib/Lingua/EN/Inflect.pm

import re


def enclose(partial_regex):
    return r'(?:{0})'.format(partial_regex)

A_ordinal_a = enclose(r"[bcdgjkpqtuvwyz]-?th")
A_ordinal_an = enclose(r"[aefhilmnorsx]-?th")
A_explicit_an = enclose('|'.join([
    r'euler',
    r'hour(?!i)',
    r'heir',
    r'honest',
    r'hono']))
A_abbrev = r"""
(?! FJO | [HLMNS]Y.  | RY[EO] | SQU
  | ( F[LR]? | [HL] | MN? | N | RH? | S[CHKLMNPTVW]? | X(YL)?) [AEIOU])
[FHLMNRSX][A-Z]
"""
A_y_cons = r'y(b[lor]|cl[ea]|fere|gg|p[ios]|rou|tt)'


def indefinite_article_for_noun(noun):
    # # HANDLE USER-DEFINED VARIANTS
    # not (yet) implemented in this port

    # my $value;
    # return "$value $word"
    #     if defined($value = ud_match($word, @A_a_user_defined));

    # HANDLE ORDINAL FORMS

    if re.match(A_ordinal_a, noun, re.IGNORECASE):
        return "a"
    if re.match(A_ordinal_an, noun, re.IGNORECASE):
        return "an"

    # HANDLE SPECIAL CASES

    if re.match(A_explicit_an, noun, re.IGNORECASE):
        return 'an'

    if re.match(r'[aefhilmnorsx]$', noun, re.IGNORECASE):
        return 'an'
    if re.match(r'[bcdgjkpqtuvwyz]$', noun, re.IGNORECASE):
        return 'a'


    # HANDLE ABBREVIATIONS

    if re.match(A_abbrev, noun, re.VERBOSE):
        return 'an'
    if re.match(r'[aefhilmnorsx][.-]', noun, re.IGNORECASE):
        return 'an'
    if re.match(r'[a-z][.-]', noun, re.IGNORECASE):
        return 'a'

    # HANDLE CONSONANTS

    if re.match(r'[^aeiouy]', noun, re.IGNORECASE):
        return 'a'

    # HANDLE SPECIAL VOWEL-FORMS

    if re.match(r'e[uw]', noun, re.IGNORECASE):
        return 'a'

    if re.match(r'onc?e\b', noun, re.IGNORECASE):
        return 'a'

    if re.match(r'uni([^nmd]|mo)', noun, re.IGNORECASE):
        return 'a'

    if re.match(r'ut[th]', noun, re.IGNORECASE):
        return 'an'

    if re.match(r'u[bcfhjkqrst][aeiou]', noun, re.IGNORECASE):
        return 'a'

    # HANDLE SPECIAL CAPITALS

    if re.match(r'^U[NK][AIEO]?', noun):
        return 'a'

    # HANDLE VOWELS

    if re.match(r'[aeiou]', noun, re.IGNORECASE):
        return 'an'

    # HANDLE y... (BEFORE CERTAIN CONSONANTS IMPLIES (UNNATURALIZED) "i.." SOUND)

    if re.match('({0})'.format(A_y_cons), noun, re.IGNORECASE):
        return "an"

    return "a"
