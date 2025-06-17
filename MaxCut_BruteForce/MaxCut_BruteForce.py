import random
import time
import os
import csv
import subprocess


def generate_random_graph(n, p=0.3):
    graph = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < p:
                graph[i][j] = graph[j][i] = 1
    return graph


def cut_value(mask, n, graph):
    cut = 0
    for i in range(n):
        for j in range(i + 1, n):
            if graph[i][j] == 1 and ((mask >> i) & 1) != ((mask >> j) & 1):
                cut += 1
    return cut


def brute_force_maxcut(n, graph):
    max_cut = 0
    best_mask = 0
    for mask in range(1 << n):
        cut = cut_value(mask, n, graph)
        if cut > max_cut:
            max_cut = cut
            best_mask = mask
    return best_mask, max_cut


def generate_dot(mask, graph, filename):
    n = len(graph)
    with open(filename, 'w') as f:
        f.write('graph MaxCutBruteForce {\n')
        f.write('  node [style=filled, fontname="Arial"];\n')
        for i in range(n):
            color = "lightblue" if (mask >> i) & 1 else "lightcoral"
            f.write(f'  {i} [fillcolor={color}];\n')
        for i in range(n):
            for j in range(i + 1, n):
                if graph[i][j] == 1:
                    cut = ((mask >> i) & 1) != ((mask >> j) & 1)
                    color = "black" if cut else "gray"
                    style = "bold" if cut else "dashed"
                    f.write(f'  {i} -- {j} [color={color}, style={style}];\n')
        f.write('}\n')


def generate_initial_dot(graph, filename):
    n = len(graph)
    with open(filename, 'w') as f:
        f.write('graph InitialGraph {\n')
        f.write('  node [style=filled, fillcolor=white, fontname="Arial"];\n')
        for i in range(n):
            f.write(f'  {i};\n')
        for i in range(n):
            for j in range(i + 1, n):
                if graph[i][j] == 1:
                    f.write(f'  {i} -- {j};\n')
        f.write('}\n')


def convert_dot_to_png(dot_path):
    png_path = dot_path.replace(".dot", ".png")
    try:
        subprocess.run(['dot', '-Tpng', dot_path, '-o', png_path], check=True)
    except subprocess.CalledProcessError:
        print(f"Eroare la conversia {dot_path} în PNG.")


def save_results(csv_file, graph_id, n, cut_value, duration):
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Graph ID', 'Nodes', 'Cut Value', 'Execution Time (s)'])
        writer.writerow([graph_id, n, cut_value, f"{duration:.6f}"])


def main():
    output_dir = "bruteforce_outputs"
    os.makedirs(output_dir, exist_ok=True)
    results_csv = os.path.join(output_dir, "results_bruteforce.csv")

    existing = len([f for f in os.listdir(output_dir) if f.endswith(".dot")]) // 2
    num_graphs_to_generate = 5

    for idx in range(existing, existing + num_graphs_to_generate):
        n = random.randint(15, 20)  # modifică între 20–25 dacă vrei grafuri mai mari
        graph = generate_random_graph(n, p=0.3)

        start = time.time()
        mask, cut = brute_force_maxcut(n, graph)
        duration = time.time() - start

        id_str = f"graph_{idx:03d}_n{n}"
        dot_initial = os.path.join(output_dir, f"{id_str}_initial.dot")
        dot_maxcut = os.path.join(output_dir, f"{id_str}_maxcut.dot")

        generate_initial_dot(graph, dot_initial)
        generate_dot(mask, graph, dot_maxcut)

        convert_dot_to_png(dot_initial)
        convert_dot_to_png(dot_maxcut)

        save_results(results_csv, id_str, n, cut, duration)

        print(f"[{id_str}] MaxCut = {cut}, Time = {duration:.6f}s")


if __name__ == "__main__":
    main()
