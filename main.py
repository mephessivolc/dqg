
from quantum_bublesort import quantum_odd_even_sort_circuit, decode_state

# --- CONFIGURAÇÃO DA ESTRUTURA DE DADOS ---
# N = 4 vetores (u, v, m)
# Cada m é representado por K_BITS qubits.
N_VECTORS = 4
K_BITS = 2  # Suporta m em {0, 1, 2, 3}

# Estrutura de endereçamento de qubits:
# Cada registro possui: [u_qubit, v_qubit, m_bit_1, m_bit_0]
QUBITS_PER_VECTOR = 2 + K_BITS  # 2 para (u,v) + K_BITS para m
TOTAL_DATA_QUBITS = N_VECTORS * QUBITS_PER_VECTOR
ANCILLA_QUBIT = TOTAL_DATA_QUBITS  # 1 qubit auxiliar para o resultado do comparador

# --- EXECUÇÃO E TESTE ---

# Entrada de teste não ordenada: [(u, v, m)]
# Valores de m fora de ordem: [3, 1, 2, 0]
dados_entrada = [
    (1, 0, 3),  # Vetor 0: m = 3
    (0, 1, 1),  # Vetor 1: m = 1
    (1, 1, 2),  # Vetor 2: m = 2
    (0, 0, 0)   # Vetor 3: m = 0
]

print("--- ENTRADA (NÃO ORDENADA) ---")
for i, vec in enumerate(dados_entrada):
    print(f"Posição {i}: (u={vec[0]}, v={vec[1]}, m={vec[2]})")

# Executa o circuito quântico
probabilities = quantum_odd_even_sort_circuit(dados_entrada)
most_probable_state = np.argmax(probabilities)

# Formata a medição em string binária
bitstring = format(most_probable_state, f'0{TOTAL_DATA_QUBITS}b')
vetores_ordenados = decode_state(bitstring)

print("\n--- SAÍDA MEDIDA (ORDENADA POR m) ---")
for i, vec in enumerate(vetores_ordenados):
    print(f"Posição {i}: (u={vec[0]}, v={vec[1]}, m={vec[2]})")