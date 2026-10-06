

### Detalhamento da Alocação de Qubits

1. **Qubits de Dados (Estrutura dos Vetores):**
* Cada vetor $(u, v, m)$ utiliza **4 qubits**:
* $1$ qubit para $u$
* $1$ qubit para $v$
* $2$ qubits (`K_BITS = 2`) para a representação do valor $m$ (números inteiros de 0 a 3)


* Como a lista possui $N = 4$ vetores:

$$\text{Qubits de Dados} = 4 \text{ vetores} \times 4 \text{ qubits/vetor} = \mathbf{16 \text{ qubits}}$$




2. **Qubit Auxiliar (Ancilla):**
* É utilizado **1 qubit auxiliar** (`ANCILLA_QUBIT`) para armazenar temporariamente a flag da comparação de $m_1 > m_2$ e controlar a execução da porta de troca $CSWAP$.



$$\text{Total} = 16 \text{ (dados)} + 1 \text{ (ancilla)} = \mathbf{17 \text{ qubits}}$$

---

### Fórmula Geral de Escalonamento

Se alterar os parâmetros de entrada no código, o número total de qubits ($Q_{total}$) necessário será dado por:

$$Q_{total} = N \cdot (2 + K) + 1$$

Onde:

* $N$: Número de vetores/arestas a serem ordenados.
* $K$: Número de bits de precisão utilizados para representar o parâmetro temporal $m$ (`K_BITS`).
* $2$: Qubits fixos para representar os vértices $(u, v)$ de cada aresta.
* $+1$: Qubit ancilla compartilhado pelas operações de comparação e troca.