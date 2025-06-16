#include <stdio.h>
#include <stdlib.h>

int n;
int** graph;

// Functie care calculeaza valoarea cut-ului pentru o particie data prin mask
int cutValue(int mask) {
    int cut = 0;
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (graph[i][j] == 1) {
                int bit_i = (mask >> i) & 1;
                int bit_j = (mask >> j) & 1;
                if (bit_i != bit_j) {
                    cut++;
                }
            }
        }
    }
    return cut;
}

// Functie care genereaza graful initial fara colorare
void generateInitialGraphDot(const char* filename) {
    FILE* fout = fopen(filename, "w");
    if (!fout) {
        perror("Eroare la deschiderea fisierului .dot");
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
                fprintf(fout, "  %d -- %d;\n", i, j);
            }
        }
    }

    fprintf(fout, "}\n");
    fclose(fout);
}


// Functie care genereaza fisier .dot pentru vizualizare
void generateDot(int mask, const char* filename) {
    FILE* fout = fopen(filename, "w");
    if (!fout) {
        perror("Eroare la deschiderea fisierului .dot");
        return;
    }

    fprintf(fout, "graph MaxCut {\n");
    fprintf(fout, "  node [style=filled, fontname=\"Arial\"];\n");

    for (int i = 0; i < n; i++) {
        const char* color = ((mask >> i) & 1) ? "lightblue" : "lightcoral";
        fprintf(fout, "  %d [fillcolor=%s];\n", i, color);
    }

    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (graph[i][j] == 1) {
                int bit_i = (mask >> i) & 1;
                int bit_j = (mask >> j) & 1;
                int cut = (bit_i != bit_j);
                const char* color = cut ? "black" : "gray";
                const char* style = cut ? "bold" : "dashed";
                fprintf(fout, "  %d -- %d [color=%s, style=%s];\n", i, j, color, style);
            }
        }
    }

    fprintf(fout, "}\n");
    fclose(fout);
}

int main() {
    FILE* fin = fopen("input.txt", "r");
    if (!fin) {
        perror("Eroare la deschiderea fisierului input.txt");
        return 1;
    }

    if (fscanf(fin, "%d", &n) != 1) {
        fprintf(stderr, "Format invalid in input.txt\n");
        fclose(fin);
        return 1;
    }

    // Alocam matricea de adiacenta
    graph = malloc(n * sizeof(int*));
    if (!graph) {
        fprintf(stderr, "Memorie insuficienta\n");
        fclose(fin);
        return 1;
    }
    for (int i = 0; i < n; i++) {
        graph[i] = malloc(n * sizeof(int));
        if (!graph[i]) {
            fprintf(stderr, "Memorie insuficienta\n");
            // eliberam memoria deja alocata
            for (int k = 0; k < i; k++) free(graph[k]);
            free(graph);
            fclose(fin);
            return 1;
        }
    }

    // Citim matricea de adiacenta
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (fscanf(fin, "%d", &graph[i][j]) != 1) {
                fprintf(stderr, "Format invalid in input.txt la matrice\n");
                // eliberam memoria
                for (int k = 0; k < n; k++) free(graph[k]);
                free(graph);
                fclose(fin);
                return 1;
            }
        }
    }
    fclose(fin);

    int maxCut = 0;
    int bestPartition = 0;

    int limit = 1 << n;
    for (int mask = 0; mask < limit; mask++) {
        int val = cutValue(mask);
        if (val > maxCut) {
            maxCut = val;
            bestPartition = mask;
        }
    }

    printf("Valoare MaxCut: %d\nPartitia optima: ", maxCut);
    for (int i = 0; i < n; i++) {
        printf("%d ", (bestPartition >> i) & 1);
    }
    printf("\n");

    generateDot(bestPartition, "maxcut.dot");
    generateInitialGraphDot("graph_initial.dot");
    printf("Fisierul graph_initial.dot a fost generat.\n");
    printf("Ruleaza: dot -Tpng graph_initial.dot -o graph_initial.png\n\n");

    // Eliberam memoria
    for (int i = 0; i < n; i++) free(graph[i]);
    free(graph);

    return 0;
}
