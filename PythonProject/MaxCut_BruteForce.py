import itertools

def read_graph(filename):
    with open(filename, 'r') as f:
        n = int(f.readline())
        graph = []
        for _ in range(n):
            row = list(map(int, f.readline().split()))
            graph.append(row)
    return n, graph

def cut_value(mask, n, graph):
    cut = 0
    for i in range(n):
        for j in range(i + 1, n):
            if graph[i][j] == 1 and ((mask >> i) & 1) != ((mask >> j) & 1):
                cut += 1
    return cut

def generate_dot(mask, graph, filename):
    n = len(graph)
    with open(filename, 'w') as f:
        f.write('graph MaxCut {\n')
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

def generate_initial_graph_dot(graph, filename):
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

def main():
    n, graph = read_graph("input.txt")

    max_cut = 0
    best_mask = 0

    for mask in range(1 << n):
        val = cut_value(mask, n, graph)
        if val > max_cut:
            max_cut = val
            best_mask = mask

    print("Valoare MaxCut:", max_cut)
    print("Partiția optimă:", ' '.join(str((best_mask >> i) & 1) for i in range(n)))

    generate_dot(best_mask, graph, "maxcut.dot")
    print("Fișierul maxcut.dot a fost generat.")
    print("Rulează: dot -Tpng maxcut.dot -o maxcut.png")

    generate_initial_graph_dot(graph, "graph_initial.dot")
    print("Fișierul graph_initial.dot a fost generat.")
    print("Rulează: dot -Tpng graph_initial.dot -o graph_initial.png")

if __name__ == "__main__":
    main()
