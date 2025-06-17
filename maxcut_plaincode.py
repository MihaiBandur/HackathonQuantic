import os
import random
import time
import csv

import rustworkx as rx
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from qiskit.quantum_info import SparsePauliOp
from qiskit.circuit.library import QAOAAnsatz
from qiskit_ibm_runtime import QiskitRuntimeService, Session, EstimatorV2 as Estimator, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from dotenv import load_dotenv

# Load IBM Quantum API key
load_dotenv()
IBM_KEY = os.getenv("IBM_KEY")
QiskitRuntimeService.save_account(channel="ibm_quantum", token=IBM_KEY,
                                  overwrite=True, set_as_default=True)
service = QiskitRuntimeService(channel='ibm_quantum')
backend = service.least_busy(min_num_qubits=127)
print(f"Using backend: {backend}")


def gen_rx_graph(n: int, p: float = 0.4) -> rx.PyGraph:
    """Generate an Erdős–Rényi random graph as a rustworkx PyGraph."""
    G = rx.PyGraph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i+1, n):
            if random.random() < p:
                G.add_edge(i, j, 1.0)
    return G


def to_bitstring(state_int: int, num_bits: int) -> list[int]:
    return [int(b) for b in format(state_int, f'0{num_bits}b')]


def calculate_cost(state: int, observable: SparsePauliOp) -> float:
    """Evaluate expectation of a Pauli-Z-cost Hamiltonian on a computational basis state."""
    bits = to_bitstring(state, observable.num_qubits)
    total = 0.0
    # Each term is a string of I/Z
    for label, coeff in zip(observable.paulis.to_labels(), observable.coeffs):
        eigen = 1
        # Qiskit label is big-endian: leftmost is qubit N-1
        for qubit_index, op in enumerate(label[::-1]):
            if op == 'Z':
                eigen *= -1 if bits[qubit_index] == 1 else 1
        total += coeff.real * eigen
    return total


def best_solution(samples: dict[int, float], hamiltonian: SparsePauliOp) -> int:
    """Return state with minimum cost from a distribution."""
    min_cost = float('inf')
    best_state = 0
    for state, prob in samples.items():
        cost = calculate_cost(state, hamiltonian)
        if cost < min_cost:
            min_cost = cost
            best_state = state
    return best_state


def cost_function(params, circuit, hamiltonian, estimator) -> float:
    """Objective for the classical optimizer: estimate expectation value."""
    isa_hamiltonian = hamiltonian.apply_layout(circuit.layout)
    job = estimator.run([(circuit, isa_hamiltonian, params)])
    result = job.result()[0]
    cost = result.data.evs
    # track costs for plotting
    cost_function.history.append(cost)
    return cost

def qaoa(n: int, graph: rx.PyGraph) -> tuple[int, float]:
    """Run one-layer QAOA on the given graph, return best state and cost."""
    # Build cost Hamiltonian
    paulis = []
    for u, v, w in graph.edge_list(), graph.weighted_edge_list():  # edges + weights
        pass  # we'll use build below
    pauli_list = []
    for u, v, w in graph.weighted_edge_list():
        ops = ['I'] * n
        ops[u] = ops[v] = 'Z'
        pauli_list.append(("".join(ops)[::-1], w))
    cost_hamiltonian = SparsePauliOp.from_list(pauli_list)

    # Build and transpile QAOA circuit
    ansatz = QAOAAnsatz(cost_operator=cost_hamiltonian, reps=1)
    ansatz.measure_all()
    layout = list(range(ansatz.num_qubits))
    pm = generate_preset_pass_manager(initial_layout=layout, backend=backend)
    transpiled = pm.run(ansatz)

    # Classical optimization
    cost_function.history = []
    with Session(backend=backend) as session:
        estimator = Estimator(mode=session)
        estimator.options.default_shots = 1000
        estimator.options.dynamical_decoupling.enable = True
        estimator.options.dynamical_decoupling.sequence_type = "XY4"
        estimator.options.twirling.enable_gates = True
        estimator.options.twirling.num_randomizations = 'auto'

        res = minimize(
            cost_function,
            x0=[0.6, 0.5],
            args=(transpiled, cost_hamiltonian, estimator),
            method='COBYLA'
        )

    # Sample from optimized circuit
    optimized = transpiled.assign_parameters(res.x)
    sampler = Sampler(mode=backend)
    sampler.options.default_shots = 10000
    sampler.options.dynamical_decoupling.enable = True
    sampler.options.dynamical_decoupling.sequence_type = "XY4"
    sampler.options.twirling.enable_gates = True
    sampler.options.twirling.num_randomizations = 'auto'

    job = sampler.run([(optimized,)])
    counts = job.result()[0].data.meas.get_int_counts()
    shots = sum(counts.values())
    dist = {state: count/shots for state, count in counts.items()}

    best = best_solution(dist, cost_hamiltonian)
    best_cost = calculate_cost(best, cost_hamiltonian)
    return best, best_cost


def brute(n: int, graph: list[list[int]]) -> tuple[int, int]:
    best_mask = 0
    best_cut = 0
    for m in range(1 << n):
        cut = sum(
            1 for i in range(n) for j in range(i+1, n)
            if graph[i][j] and (((m >> i) & 1) != ((m >> j) & 1))
        )
        if cut > best_cut:
            best_cut, best_mask = cut, m
    return best_mask, best_cut


def greedy(n: int, graph: list[list[int]]) -> tuple[int, int]:
    part = [0]*n
    changed = True
    while changed:
        changed = False
        for i in range(n):
            cur = sum(graph[i][j] for j in range(n) if part[i] != part[j])
            new = sum(graph[i][j] for j in range(n) if part[i] == part[j])
            if new > cur:
                part[i] = 1 - part[i]
                changed = True
    mask = sum((1 << i) for i, p in enumerate(part) if p)
    cut = sum(
        1 for i in range(n) for j in range(i+1, n)
        if graph[i][j] and (((mask >> i) & 1) != ((mask >> j) & 1))
    )
    return mask, cut


if __name__ == '__main__':
    # Prepare output
    os.makedirs('plots', exist_ok=True)
    with open('compare_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'n', 'exact', 'greedy', 'qaoa', 't_brute', 't_greedy', 't_qaoa'])

        for i in range(5):
            n = random.randint(6, 8)
            rx_graph = gen_rx_graph(n)
            # Convert to adjacency matrix
            mat = [[0]*n for _ in range(n)]
            for u, v, w in rx_graph.weighted_edge_list():
                mat[u][v] = mat[v][u] = int(w)

            t0 = time.time()
            _, exact_cut = brute(n, mat)
            t_br = time.time() - t0

            t0 = time.time()
            _, greedy_cut = greedy(n, mat)
            t_gr = time.time() - t0

            t0 = time.time()
            _, qaoa_cut = qaoa(n, rx_graph)
            t_qa = time.time() - t0

            writer.writerow([i, n, exact_cut, greedy_cut, qaoa_cut, t_br, t_gr, t_qa])

    # Plot comparison
    df = pd.read_csv('compare_results.csv')
    df.plot(x='n', y=['exact', 'greedy', 'qaoa'], marker='o')
    plt.title('Max-Cut Value Comparison')
    plt.xlabel('Number of Nodes')
    plt.ylabel('Cut Value')
    plt.grid(True)
    plt.savefig('plots/cut_compare.png')
    plt.show()
