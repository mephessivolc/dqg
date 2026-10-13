#!/usr/bin/env python3

# Quantum Foremost Journey
# Requer durr_hoyer.py (o ordenador Dürr-Høyer em PennyLane) na mesma pasta.

import argparse
import re
import sys
from math import inf

from dg.durr_hoyer import dh_sort

VERTEXRE = r'[a-zA-Z]+'
MOMENTRE = r'[0-9]+'
CONTACTRE = r'({})\s+({})\s+({})'.format(VERTEXRE, VERTEXRE, MOMENTRE)


def read_contacts(infile):
    return [(m.group(1), m.group(2), int(m.group(3)))
            for l in infile
            if (m := re.match(CONTACTRE, l.strip()))]


def quantum_sort_contacts(contacts, seed):
    """
    Ordena os contatos (u, v, momento) pelo momento usando Dürr-Høyer.

    Desempate: cada contato recebe o índice original como critério secundário,
    com chave composta  momento * n + índice.  Assim as chaves ficam todas
    distintas, a ordem é total e determinística, e o resultado coincide com o
    de `list.sort` (que é estável). Isso importa porque, com `m >= a[u]`
    (não estrito), a ordem entre contatos de mesmo momento altera o resultado.
    """
    n = len(contacts)
    if n < 2:
        return list(contacts), 0
    tagged = tuple((u, v, m, i) for i, (u, v, m) in enumerate(contacts))
    ordered, oracle_calls = dh_sort(tagged, rng=seed, key=lambda c: c[2] * n + c[3])
    return [(u, v, m) for u, v, m, _ in ordered], oracle_calls


parser = argparse.ArgumentParser()
parser.add_argument('root',
                    help='Vértice raiz da procura')
parser.add_argument('contacts',
                    help='Lista de triplas dirigidas de_vértice, para_vértice e momento')
parser.add_argument('--seed', type=int, default=12345,
                    help='Semente do RNG da medição quântica (reprodutibilidade)')
parser.add_argument('--verify', action='store_true',
                    help='Compara a ordem obtida com a ordenação clássica')
args = parser.parse_args()

with open(args.contacts) as infile:
    contacts = read_contacts(infile)

# Parte quântica: ordenar a lista de contatos pelo momento (Dürr-Høyer).
contacts_sorted, oracle_calls = quantum_sort_contacts(contacts, args.seed)
print(f'consultas ao oráculo: {oracle_calls}', file=sys.stderr)

if args.verify:
    ok = contacts_sorted == sorted(contacts, key=lambda x: x[2])
    print(f'ordenação idêntica à clássica: {ok}', file=sys.stderr)

contacts = contacts_sorted

a = {args.root: 0}

for u, v, m in contacts:
    if m >= a.get(u, inf):
        if m < a.get(v, inf):
            a[v] = m

print(a)