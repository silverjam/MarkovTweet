# -*- python -*-

import urllib
import random

from pprint import pprint
from heapq import heappush

from itertools import islice

try:
    from py.test import raises
except:
    def raises(*a, **kw): pass


def debugBreak():

    import pdb
    import sys

    pdb.post_mortem(sys.exc_info()[2])


def nextEntry(order, entry, ch):
    if entry[0] and len(entry[1] + ch) < order:
        return (True, entry[1] + ch)
    return (False, (entry[1] + ch)[-order:])


def makeTableN(order, data, table):

    prev = (True, "")

    for next in data:

        pdf = table.setdefault(prev, [])
        pdf.append(next)

        prev = nextEntry(order, prev, next)

    pdf = table.setdefault(prev, [])
    pdf.append('\0')

    return table 


def test_makeTableN():

    datas = [
        ( 1, "abcdef", { (True, "")   : ['a'],
                         (False, "a") : ['b'],
                         (False, "b") : ['c'],
                         (False, "c") : ['d'],
                         (False, "d") : ['e'],
                         (False, "e") : ['f'], 
                         (False, "f") : ['\0'], 
        }),
        ( 2, "abcdef", { (True, "")    : ['a'],
                         (True, "a")   : ['b'],
                         (False, "ab") : ['c'],
                         (False, "bc") : ['d'],
                         (False, "cd") : ['e'],
                         (False, "de") : ['f'], 
                         (False, "ef") : ['\0'], 
        }),
        ( 2, "abcddefabd", 
            { (True, "" )   : ['a'],
              (True, "a")   : ['b'],
              (False, "ab") : ['c', 'd'],
              (False, "bc") : ['d'],
              (False, "cd") : ['d'],
              (False, "dd") : ['e'],
              (False, "de") : ['f'],
              (False, "ef") : ['a'], 
              (False, "fa") : ['b'], 
              (False, "bd") : ['\0'], 
        }),
 
    ]

    for data in datas:
        result = makeTableN(data[0], data[1], {})
        assert result == data[2] 
    

def filterNewline(data):
    def iter(data):
        for x in data:
            if x.isspace() and x != ' ':
                yield ' '
                continue
            yield x
    if not data: return
    it = iter(data) 
    x = it.next()
    yield x
    while True:
        y = it.next()
        if not y.isspace() or x != y: yield y
        x = y


def test_filterNewline():

    s = str.join('', filterNewline("a\n\t\rb"))
    assert s == "a b"

    s = str.join('', filterNewline("   a            \n\t\rb    c "))
    assert s == " a b c "

    s = str.join('', filterNewline(""))
    assert s == ""


def markov(order, table):

    accum = []
    entry = (True, "")

    while True:

        stop = yield accum
        if stop: return 

        el = random.choice(table[entry])
        if el == '\0':
            break

        entry = nextEntry(order, entry, el)
        accum.append(el)

    yield accum


if __name__ == '__main__':

    from data_story import data

    table = {}
    order = 7

    #for data in file('tweet.txt'):
    #    table = makeTableN(order, filterNewline(data), table)

    table = makeTableN(order, filterNewline(data), table)

    for x in markov(order, table):
        print u''.join(x)
        raw_input()

# vim: et:sts=4:sw=4:ts=4:tw=999:bs=2:
