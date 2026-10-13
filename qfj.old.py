#!/usr/bin/env python3

# Quantum Foremost Journey

import argparse
import re
from math import inf

VERTEXRE = r'[a-zA-Z]+'
MOMENTRE = r'[0-9]+'
CONTACTRE = r'({})\s+({})\s+({})'.format(VERTEXRE, VERTEXRE, MOMENTRE)

def read_contacts(infile):
    return [(m.group(1), m.group(2), int(m.group(3)))
            for l in infile
            if (m := re.match(CONTACTRE, l.strip()))]

parser = argparse.ArgumentParser()
parser.add_argument('root',
                    help='Vértice raiz da procura')
parser.add_argument('contacts',
                    help='Lista de triplas dirigidas de_vértice, para_vértice e momento')
args = parser.parse_args()

with open(args.contacts) as infile:
    contacts = read_contacts(infile)

# É aqui que entra a parte quântica.  Ordenar a lista de contatos, que
# são tuplas, pelo momento.
contacts.sort(key=lambda x: x[2])

a = {args.root:0}

for u,v,m in contacts:
    if m >= a.get(u, inf):
        if m < a.get(v, inf):
            a[v] = m

print(a)
