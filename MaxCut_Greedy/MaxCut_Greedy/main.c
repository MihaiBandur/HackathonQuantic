#include <stdio.h>
#include <stdlib.h>

int n;
int **graph;

// Calculează valoarea tăierii
int cutValue(int *partition) {
    int cut = 0;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++)
            if (graph[i][j] == 1 && partition[i] != partition[j])
                cut++;
    return cut;
}


// Generează fișierul .dot pentru graful cu partiție
void generateDotPartition(int *partition, const char *filename) {
    FILE *fout = fopen(filename, "w");
    if (!fout) {
        perror("Eroare la crearea fișierului .dot");
        return;
    }

    fprintf(fout, "graph MaxCut {\n");
    fprintf(fout, "  node [style=filled, fontname=\"Arial\"];\n");

    for (int i = 0; i < n; i++) {
        const char *color = (partition[i] == 0) ? "lightblue" : "lightcoral";
        fprintf(fout, "  %d [fillcolor=%s];\n", i, color);
    }

    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (graph[i][j] == 1) {
                int cut = (partition[i] != partition[j]);
                const char *color = cut ? "black" : "gray";
                const char *style = cut ? "bold" : "dashed";
                fprintf(fout, "  %d -- %d [color=%s, style=%s];\n", i, j, color, style);
            }
        }
    }

    fprintf(fout, "}\n");
    fclose(fout);
}

// Generează fișierul .dot pentru graful inițial simplu
void generateDotInitial(const char *filename) {
    FILE *fout = fopen(filename, "w");
    if (!fout) {
        perror("Eroare la crearea fișierului .dot");
        return;
    }

    fprintf(fout, "graph InitialGraph {\n");
    fprintf(fout, "  node [style=filled, fillcolor=white, fontname=\"Arial\"];\n");

    for (int i = 0; i < n; i++) {
        fprintf(fout, "  %d;\n", i);
    }

    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (graph[i][j] == 1) {
                fprintf(fout, "  %d -- %d [color=black];\n", i, j);
            }
        }
    }

    fprintf(fout, "}\n");
    fclose(fout);
}

int main() {
    FILE *fin = fopen("input.txt", "r");
    if (!fin) {
        perror("Eroare la deschiderea fișierului input.txt");
        return 1;
    }

    fscanf(fin, "%d", &n);

    graph = malloc(n * sizeof(int*));
    for (int i = 0; i < n; i++) {
        graph[i] = malloc(n * sizeof(int));
        for (int j = 0; j < n; j++) {
            fscanf(fin, "%d", &graph[i][j]);
        }
    }
    fclose(fin);

    int *partition = malloc(n * sizeof(int));
    partition[0] = 0;

    for (int u = 1; u < n; u++) {
        int cut_if_0 = 0, cut_if_1 = 0;
        for (int v = 0; v < u; v++) {
            if (graph[u][v] == 1) {
                if (partition[v] == 1) cut_if_0++;
                if (partition[v] == 0) cut_if_1++;
            }
        }
        partition[u] = (cut_if_0 > cut_if_1) ? 0 : 1;
    }

    int maxCut = cutValue(partition);
    printf("Valoare MaxCut (aproximativă): %d\nPartiția: ", maxCut);
    for (int i = 0; i < n; i++) printf("%d ", partition[i]);
    printf("\n");

    generateDotInitial("graph_initial.dot");
    printf("Fișierul graph_initial.dot a fost generat.\n");

    generateDotPartition(partition, "maxcut_greedy.dot");
    printf("Fișierul maxcut_greedy.dot a fost generat.\n");
    printf("Rulează:\n");
    printf("  dot -Tpng graph_initial.dot -o graph_initial.png\n");
    printf("  dot -Tpng maxcut_greedy.dot -o maxcut_greedy.png\n");

    for (int i = 0; i < n; i++)
        free(graph[i]);
    free(graph);
    free(partition);

    return 0;
}
