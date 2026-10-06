import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=TOTAL_DATA_QUBITS + 1)


def get_vector_wires(vector_idx):
    """Retorna os índices dos qubits associados a um determinado vetor E_i."""
    start = vector_idx * QUBITS_PER_VECTOR
    return list(range(start, start + QUBITS_PER_VECTOR))


def compare_and_swap(vec1_idx, vec2_idx, ancilla):
    """
    Circuito Reversível de Compare-and-Swap.
    Compara o valor de m entre o Vetor 1 e o Vetor 2.
    Se m1 > m2, troca todos os qubits dos dois vetores (u, v, m).
    """
    w1 = get_vector_wires(vec1_idx)
    w2 = get_vector_wires(vec2_idx)
    
    # Qubits que contêm o valor de m
    m1_wires = w1[2:]
    m2_wires = w2[2:]

    # --- 1. ETAPA DE COMPARAÇÃO (m1 > m2) ---
    # Comparador simples para K_BITS = 2:
    # Se (m1[1] > m2[1]) OU (m1[1] == m2[1] E m1[0] > m2[0]) -> ancilla = 1
    
    # Caso Bit Mais Significativo (MSB): m1[1] = 1 e m2[1] = 0
    qml.PauliX(m2_wires[1])
    qml.Toffoli(wires=[m1_wires[1], m2_wires[1], ancilla])
    qml.PauliX(m2_wires[1])

    # Caso LSB quando MSB é igual: m1[1] == m2[1] e (m1[0] = 1, m2[0] = 0)
    # Ativa ancilla se m1[0] > m2[0] e MSBs forem iguais
    qml.CNOT(wires=[m1_wires[1], m2_wires[1]])
    qml.PauliX(m2_wires[1])  # Ativo se m1[1] == m2[1]
    
    qml.PauliX(m2_wires[0])
    qml.MultiControlledX(
        control_wires=[m2_wires[1], m1_wires[0], m2_wires[0]], 
        wires=ancilla
    )
    qml.PauliX(m2_wires[0])
    qml.PauliX(m2_wires[1])
    qml.CNOT(wires=[m1_wires[1], m2_wires[1]])  # Desfaz alteração no MSB de m2

    # --- 2. ETAPA DE TROCA CONTROLADA (CSWAP / Porta Fredkin) ---
    # Se ancilla == 1, realiza SWAP entre todos os qubits dos vetores (u, v, m)
    for q1, q2 in zip(w1, w2):
        qml.CSWAP(wires=[ancilla, q1, q2])

    # --- 3. ETAPA DE DESCOMPUTAÇÃO (Uncomputation) ---
    # Limpa o qubit ancilla revertendo as portas de comparação
    qml.CNOT(wires=[m1_wires[1], m2_wires[1]])
    qml.PauliX(m2_wires[1])
    qml.PauliX(m2_wires[0])
    qml.MultiControlledX(
        control_wires=[m2_wires[1], m1_wires[0], m2_wires[0]], 
        wires=ancilla
    )
    qml.PauliX(m2_wires[0])
    qml.PauliX(m2_wires[1])
    qml.CNOT(wires=[m1_wires[1], m2_wires[1]])

    qml.PauliX(m2_wires[1])
    qml.Toffoli(wires=[m1_wires[1], m2_wires[1], ancilla])
    qml.PauliX(m2_wires[1])


@qml.qnode(dev)
def quantum_odd_even_sort_circuit(vectors_data):
    """
    Circuito Principal do Quantum Odd-Even Transposition Sort.
    """
    # 1. Estado Inicial: Codifica a entrada não ordenada nos registradores
    for vec_idx, (u, v, m) in enumerate(vectors_data):
        wires = get_vector_wires(vec_idx)
        if u == 1: qml.PauliX(wires[0])
        if v == 1: qml.PauliX(wires[1])
        
        # Converter m para binário (2 bits)
        m_bin = format(int(m), '02b')
        if m_bin[0] == '1': qml.PauliX(wires[2])  # MSB
        if m_bin[1] == '1': qml.PauliX(wires[3])  # LSB

    # 2. Loop Paralelo de N Etapas (Alternando Ímpar e Par)
    for step in range(N_VECTORS):
        if step % 2 == 0:
            # Fase Ímpar: compara pares (0,1) e (2,3)
            compare_and_swap(0, 1, ANCILLA_QUBIT)
            compare_and_swap(2, 3, ANCILLA_QUBIT)
        else:
            # Fase Par: compara par (1,2)
            compare_and_swap(1, 2, ANCILLA_QUBIT)

    # 3. Medição de todos os qubits de dados
    return qml.probs(wires=list(range(TOTAL_DATA_QUBITS)))


def decode_state(bitstring):
    """Decodifica a string de bits nos vetores (u, v, m) correspondentes."""
    result = []
    for i in range(N_VECTORS):
        sub = bitstring[i * QUBITS_PER_VECTOR : (i + 1) * QUBITS_PER_VECTOR]
        u = int(sub[0])
        v = int(sub[1])
        m = int(sub[2:], 2)  # Converte os bits de m para inteiro
        result.append((u, v, m))
    return result