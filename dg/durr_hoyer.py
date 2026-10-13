"""
Ordenação de vetores (u, v, t) pela 3ª entrada via Dürr-Høyer, com PennyLane.
Estilo funcional: tuplas imutáveis, funções puras, recursão, RNG explícito.

O circuito é executado em `default.qubit` (statevector exato, shots=None).
Retornamos as probabilidades da medição e amostramos com um RNG puro próprio,
o que mantém a execução reprodutível e sem efeito colateral.
"""
from __future__ import annotations

from math import ceil, log2, sqrt
from typing import Callable, Sequence, Tuple

import numpy as np
import pennylane as qml

Vec = Tuple[int, int, int]   # (u, v, t)
Rng = int

# ---------------------------------------------------------------- RNG puro
def next_float(rng: Rng) -> Tuple[float, Rng]:
    mask = (1 << 64) - 1
    s = (rng + 0x9E3779B97F4A7C15) & mask
    z = ((s ^ (s >> 30)) * 0xBF58476D1CE4E5B9) & mask
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & mask
    z ^= z >> 31
    return (z >> 11) / float(1 << 53), s


def next_int(rng: Rng, n: int) -> Tuple[int, Rng]:
    x, r = next_float(rng)
    return int(x * n), r


# ---------------------------------------------------- circuito de Grover
def n_qubits(n_items: int) -> int:
    return max(2, ceil(log2(n_items)))  # GroverOperator exige >= 2 qubits


def grover_probs(marked_idx: Tuple[int, ...], n_wires: int, j: int) -> np.ndarray:
    """
    Probabilidades de medição após j iterações de Grover.
      H^{⊗k}  ->  [ Oráculo (FlipSign por estado marcado) -> Difusão ]^j
    O oráculo é uma tabela de consulta (lookup): um FlipSign por índice marcado.
    Em hardware, seria substituído por um comparador de inteiros reversível.
    """
    wires = list(range(n_wires))
    dev = qml.device("default.qubit", wires=n_wires)

    @qml.qnode(dev)
    def circuit():
        for w in wires:
            qml.Hadamard(wires=w)
        for _ in range(j):
            for i in marked_idx:
                qml.FlipSign(i, wires=wires)       # U_f: |i> -> -|i>
            qml.GroverOperator(wires=wires)        # 2|s><s| - I
        return qml.probs(wires=wires)

    return circuit()


def measure(probs: np.ndarray, rng: Rng) -> Tuple[int, Rng]:
    x, rng2 = next_float(rng)
    return int(np.searchsorted(np.cumsum(probs), x * probs.sum())), rng2


# ------------------------------------------- busca de elemento marcado (BBHT)
def bbht_search(
    keys: Tuple[int, ...], threshold: int, n_wires: int,
    rng: Rng, budget: int, lam: float = 6 / 5,
) -> Tuple[int | None, Rng, int]:
    """Procura i com keys[i] < threshold. Devolve (índice|None, rng, consultas)."""
    n = len(keys)
    marked_idx = tuple(i for i, k in enumerate(keys) if k < threshold)
    if not marked_idx:              # checagem clássica: evita laço infinito
        return None, rng, 0
    cap = sqrt(2 ** n_wires)

    def loop(m: float, rng: Rng, used: int):
        if used >= budget:
            return None, rng, used
        j, rng1 = next_int(rng, max(1, ceil(m)))
        idx, rng2 = measure(grover_probs(marked_idx, n_wires, j), rng1)
        used2 = used + j + 1
        if idx < n and keys[idx] < threshold:      # verificação clássica
            return idx, rng2, used2
        return loop(min(lam * m, cap), rng2, used2)

    return loop(1.0, rng, 0)


# ------------------------------------------------------ Dürr-Høyer (mínimo)
def durr_hoyer_min(keys: Sequence[int], rng: Rng) -> Tuple[int, Rng, int]:
    n = len(keys)
    if n == 1:
        return 0, rng, 0
    keys_t = tuple(keys)
    n_wires = n_qubits(n)
    budget = ceil(22.5 * sqrt(n) + 1.4 * log2(n) ** 2)
    y0, rng0 = next_int(rng, n)

    def loop(y: int, rng: Rng, used: int):
        if budget - used <= 0:
            return y, rng, used
        idx, rng1, spent = bbht_search(keys_t, keys_t[y], n_wires, rng, budget - used)
        if idx is None:
            return y, rng1, used + spent
        return loop(idx, rng1, used + spent)

    return loop(y0, rng0, 0)


# ------------------------------------------------------------- ordenação
def dh_sort(
    vectors: Sequence[Vec], rng: Rng = 12345,
    key: Callable[[Vec], int] = lambda v: v[2],
) -> Tuple[Tuple[Vec, ...], int]:
    def go(rest: Tuple[Vec, ...], rng: Rng, acc: Tuple[Vec, ...], calls: int):
        if not rest:
            return acc, calls
        i, rng1, used = durr_hoyer_min([key(v) for v in rest], rng)
        return go(rest[:i] + rest[i + 1:], rng1, acc + (rest[i],), calls + used)

    return go(tuple(vectors), rng, (), 0)


# ------------------------------------------------------------------- teste
if __name__ == "__main__":
    edges = [(0, 1, 7), (1, 2, 3), (2, 3, 9), (0, 3, 1), (3, 1, 5), (2, 0, 3)]
    ordered, calls = dh_sort(edges)
    print("entrada :", edges)
    print("ordenado:", list(ordered))
    print("consultas ao oráculo:", calls)
    expected = sorted(e[2] for e in edges)
    assert [e[2] for e in ordered] == expected

    ok = sum([e[2] for e in dh_sort(edges, rng=s)[0]] == expected for s in range(30))
    print(f"corretude em 30 execuções: {ok}/30")

    print("\nCircuito de Grover (k=3 qubits, marcado={2}, j=1):")
    dev = qml.device("default.qubit", wires=3)

    @qml.qnode(dev)
    def demo():
        for w in range(3):
            qml.Hadamard(wires=w)
        qml.FlipSign(2, wires=[0, 1, 2])
        qml.GroverOperator(wires=[0, 1, 2])
        return qml.probs(wires=[0, 1, 2])

    print(qml.draw(demo)())