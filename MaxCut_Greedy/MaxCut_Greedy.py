import os
import random
import time
import subprocess
import re

def generate_random_graph(n, density=0.4):
    graph = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            if random.random() < density:
                graph[i][j] = graph[j][i] = 1
    return graph

def write_graph_to_file(graph, filename):
    with open(filename, "w") as f:
        n = len(graph)
        f.write(f"{n}\n")
        for row in graph:
            f.write(" ".join(map(str, row)) + "\n")

def read_graph(filename):
    with open(filename, 'r') as f:
        n = int(f.readline())
        graph = [list(map(int, f.readline().split())) for _ in range(n)]
    return n, graph

def cut_value(mask, n, graph):
    cut = 0
    for i in range(n):
        for j in range(i + 1, n):
            if graph[i][j] == 1 and ((mask >> i) & 1) != ((mask >> j) & 1):
                cut += 1
    return cut

def greedy_maxcut(n, graph):
    part = [0] * n
    changed = True
    while changed:
        changed = False
        for i in range(n):
            current_cut = sum(graph[i][j] for j in range(n) if part[i] != part[j] and graph[i][j])
            new_cut = sum(graph[i][j] for j in range(n) if part[i] == part[j] and graph[i][j])
            if new_cut > current_cut:
                part[i] = 1 - part[i]
                changed = True
    mask = sum((1 << i) for i in range(n) if part[i] == 1)
    return mask, cut_value(mask, n, graph)

def generate_dot(mask, graph, filename):
    n = len(graph)
    with open(filename, 'w') as f:
        f.write('graph MaxCutGreedy {\n  node [style=filled, fontname="Arial"];\n')
        for i in range(n):
            color = "lightblue" if (mask >> i) & 1 else "lightcoral"
            f.write(f'  {i} [fillcolor={color}];\n')
        for i in range(n):
            for j in range(i + 1, n):
                if graph[i][j]:
                    cut = ((mask >> i) & 1) != ((mask >> j) & 1)
                    color = "black" if cut else "gray"
                    style = "bold" if cut else "dashed"
                    f.write(f'  {i} -- {j} [color={color}, style={style}];\n')
        f.write('}\n')

def generate_initial_graph_dot(graph, filename):
    n = len(graph)
    with open(filename, 'w') as f:
        f.write('graph InitialGraph {\n  node [style=filled, fillcolor=white, fontname="Arial"];\n')
        for i in range(n):
            f.write(f'  {i};\n')
        for i in range(n):
            for j in range(i + 1, n):
                if graph[i][j]:
                    f.write(f'  {i} -- {j};\n')
        f.write('}\n')

def convert_dot_to_png(dot_file):
    png_file = dot_file.replace(".dot", ".png")
    try:
        subprocess.run(["dot", "-Tpng", dot_file, "-o", png_file], check=True)
    except FileNotFoundError:
        print("⚠️ Graphviz nu este instalat sau comanda `dot` nu e găsită.")

def get_next_graph_index(output_dir):
    max_index = 0
    pattern = re.compile(r"input_(\d+)\.txt")
    for filename in os.listdir(output_dir):
        match = pattern.match(filename)
        if match:
            idx = int(match.group(1))
            if idx > max_index:
                max_index = idx
    return max_index + 1

def main():
    output_dir = "grafuri_maxcut"
    os.makedirs(output_dir, exist_ok=True)

    next_index = get_next_graph_index(output_dir)
    num_grafuri_noi = 10

    csv_exists = os.path.exists("rezultate.csv")
    with open("rezultate.csv", "a") as results:
        if not csv_exists:
            results.write("Graf,Noduri,Muchii,MaxCut,Durata(ms)\n")

        for i in range(next_index, next_index + num_grafuri_noi):
            n = random.randint(10, 100)
            graph = generate_random_graph(n, density=0.4)
            input_file = os.path.join(output_dir, f"input_{i}.txt")
            write_graph_to_file(graph, input_file)

            start = time.time()
            mask, cut = greedy_maxcut(n, graph)
            duration = (time.time() - start) * 1000

            edge_count = sum(sum(row) for row in graph) // 2

            dot1 = os.path.join(output_dir, f"initial_{i}.dot")
            dot2 = os.path.join(output_dir, f"maxcut_{i}.dot")
            generate_initial_graph_dot(graph, dot1)
            generate_dot(mask, graph, dot2)
            convert_dot_to_png(dot1)
            convert_dot_to_png(dot2)

            results.write(f"Graf_{i},{n},{edge_count},{cut},{duration:.2f}\n")
            print(f"✔️ Graf_{i} | Noduri: {n}, Muchii: {edge_count}, MaxCut: {cut}, Durata: {duration:.2f}ms")

if __name__ == "__main__":
    main()
