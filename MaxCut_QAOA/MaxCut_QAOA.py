import random, time, os, csv
import matplotlib.pyplot as plt
from qiskit_algorithms import QAOA
from qiskit_optimization.applications import Maxcut
from qiskit_optimization.algorithms import MinimumEigenOptimizer
#from qiskit.algorithms import QAOA
from qiskit_aer.primitives import Estimator as AerEstimator

def gen_graph(n,p=0.4):
    graph=[[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            if random.random()<p: graph[i][j]=graph[j][i]=1
    return graph

def cut_value(mask,n,graph):
    return sum(1 for i in range(n) for j in range(i+1,n)
               if graph[i][j]==1 and ((mask>>i)&1)!=((mask>>j)&1))

def brute(n,graph):
    best,cut=0,0
    for m in range(1<<n):
        c=cut_value(m,n,graph)
        if c>cut: best,cut=m,c
    return best,cut

def greedy(n,graph):
    part=[0]*n
    changed=True
    while changed:
        changed=False
        for i in range(n):
            cur=sum(graph[i][j] for j in range(n) if part[i]!=part[j])
            new=sum(graph[i][j] for j in range(n) if part[i]==part[j])
            if new>cur:
                part[i]=1-part[i]; changed=True
    m=sum((1<<i) for i in range(n) if part[i]); return m, cut_value(m,n,graph)

def qaoa(n,graph):
    edge_list=[(i,j) for i in range(n) for j in range(i+1,n) if graph[i][j]]
    maxcut = Maxcut(edge_list)
    qp = maxcut.to_quadratic_program()
    qaoa = QAOA(estimator=AerEstimator(), reps=1)
    algo = MinimumEigenOptimizer(qaoa)
    res=algo.solve(qp)
    mask=int("".join(str(int(x)) for x in res.x[::-1]),2)
    return mask, int(res.fval)

# rulare test
os.makedirs("plots",exist_ok=True)
with open("compare_results.csv","w",newline='') as f:
    w=csv.writer(f); w.writerow(["id","n","exact","greedy","qaoa","t_brute","t_greedy","t_qaoa"])
    for i in range(5):
        n=random.randint(10,15); g=gen_graph(n)
        t0=time.time(); mb,cb=brute(n,g); t_br=time.time()-t0
        t0=time.time(); mg,cg=greedy(n,g); t_gr=time.time()-t0
        t0=time.time(); mq,cq=qaoa(n,g); t_qa=time.time()-t0
        w.writerow([i,n,cb,cg,cq,t_br,t_gr,t_qa])
# grafic
import pandas as pd
df=pd.read_csv("compare_results.csv")
df.plot(x="n", y=["exact","greedy","qaoa"], marker='o')
plt.savefig("plots/cut_compare.png")
