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

def greedy_maxcut(n, graph):
    part = [0] * n  # Inițial toți în partea 0

    changed = True
    while changed:
        changed = False
        for i in range(n):
            current_cut = 0
            new_cut = 0
            for j in range(n):
                if graph[i][j] == 1:
                    if part[i] != part[j]:
                        current_cut += 1
                    else:
                        new_cut += 1
            if new_cut > current_cut:
                part[i] = 1 - part[i]
                changed = True

    # Convertim part[] în bitmask
    mask = 0
    for i in range(n):
        if part[i] == 1:
            mask |= (1 << i)
    return mask, cut_value(mask, n, graph)

def generate_dot(mask, graph, filename):
    n = len(graph)
    with open(filename, 'w') as f:
        f.write('graph MaxCutGreedy {\n')
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

    mask, cut = greedy_maxcut(n, graph)

    print("Valoare MaxCut (greedy):", cut)
    print("Partiția aleasă:", ' '.join(str((mask >> i) & 1) for i in range(n)))

    generate_dot(mask, graph, "maxcut_greedy.dot")
    print("Fișierul maxcut_greedy.dot a fost generat.")
    print("Rulează: dot -Tpng maxcut_greedy.dot -o maxcut_greedy.png")

    generate_initial_graph_dot(graph, "graph_initial.dot")
    print("Fișierul graph_initial.dot a fost generat.")
    print("Rulează: dot -Tpng graph_initial.dot -o graph_initial.png")

if __name__ == "__main__":
    main()
