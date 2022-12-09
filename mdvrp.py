import cplex
from docplex.mp.model import Model
import matplotlib.pyplot as plot
import math
import random

depositi = 2
clienti = 5
capacity = 80
veicoli = 2

set_clienti = range(clienti)
set_depositi = range(clienti, clienti+depositi)
domanda =  [7,30,16,9,21,15,29,23,11,5,19,29,23,21,10,15,3,41,9,28,8,8,16,10,28,7,15,14,6,19,11,12,23,26,17,6,9,15,14,7,27,13,11,16,10,5,25,17,18,10] #[random.randint(5,10) for _ in set_clienti]
coord_nodi = [(37,52),(49,49),(52,64),(20,26),(40,30),(21,47),(17,63),(31,62),(52,33),(51,21),(42,41),(31,32),(5,25),(12,42),(36,16),(52,41),(27,23),(17,33),(13,13),(57,58),(62,42),(42,57),(16,57),(8,52),(7,38),(27,68),(30,48),(43,67),(58,48),(58,27),(37,69),(38,46),(46,10),(61,33),(62,63),(63,69),(32,22),(45,35),(59,15),(5,6),(10,17),(21,10),(5,64),(30,15),(39,10),(32,39),(25,32),(25,55),(48,28),(56,37),(20,20),(30,40),(50,30),(60,50)]
set_vertici = list(set_clienti) + list(set_depositi)
arcs = [(i, j, k) for i in set_clienti for j in set_clienti if i != j for k in range(veicoli*depositi)]
deposit_arcs = []
for d in set_depositi:
    for k in range(veicoli):
        k = k + veicoli * set_depositi.index(d)
        for j in set_clienti:
            deposit_arcs.append((d,j,k))
            deposit_arcs.append((j,d,k))
arcs += deposit_arcs
costo = {(i, j): math.sqrt((coord_nodi[j][0] - coord_nodi[i][0])**2
                           + (coord_nodi[j][1] - coord_nodi[i][1])**2) for i, j,k in arcs}
y = [(i,k) for i in set_vertici for k in range(veicoli*depositi)]
up = [(i,k) for i in set_clienti for k in range(veicoli*depositi)]
# print(set_clienti)
# print(set_depositi)
# print(domanda)
# print(coord_nodi)
# print(set_vertici)
print(len(arcs))
# print(y)
# print(costo)
#print(u)

mdl = Model('MDVRP')
x = mdl.binary_var_dict(arcs, name='x')  # variabili decisionali
u = mdl.continuous_var_dict(up, ub=capacity, name='u')  # upper bound
y = mdl.binary_var_dict(y, name='y')
mdl.minimize(mdl.sum(costo[i, j]*x[i, j, k] for i in set_vertici for j in set_vertici if i != j for k in range(veicoli*depositi) if (i,j,k) in x))

 # per ogni cliente puo passare solo un veicolo
mdl.add_constraints(mdl.sum(y[i, k] for k in range(veicoli*depositi)) == 1 for i in set_clienti if i < clienti)

for d in set_depositi:
    mdl.add_constraint(mdl.sum(y[d, k] for k in range(veicoli*depositi)) == veicoli )

# constraint 1.31 pag 15
mdl.add_constraints(mdl.sum(x[i,j,k] for j in set_vertici if i != j and (i,j,k) in x) == y[i,k] for i in set_vertici for k in range(veicoli*depositi) )
mdl.add_constraints(mdl.sum(x[j,i,k] for j in set_vertici if i != j and (j,i,k) in x) == y[i,k] for i in set_vertici for k in range(veicoli*depositi) )

# 1.32
#print(mdl.add_constraints(mdl.sum(domanda[i]*y[i, k] for i in set_clienti) <= capacity for k in range(depositi*veicoli)))

# mdl.add_constraints(mdl.sum(x[i, j] for j in set_vertici if j != i) == 1 for i in set_clienti)
# mdl.add_constraints(mdl.sum(x[i, j] for i in set_vertici if i != j) == 1 for j in set_clienti)

mdl.add_constraints((u[i,k] - u[j,k] + (capacity*x[i,j,k]) <= capacity - domanda[j]) for i in set_clienti for j in set_clienti for k in range(veicoli*depositi) if i!=j and i < clienti )
mdl.add_constraints((domanda[i] <= u[i,k]) for i in set_clienti for k in range(veicoli*depositi) if i < clienti)
mdl.add_constraints((u[i,k] <= capacity) for i in set_clienti for k in range(veicoli*depositi) if i < clienti)

for d in range(clienti,depositi):
    for k in range(veicoli):
        mdl.add_constraints(mdl.sum(x[d,j,k] for j in set_clienti) == 1)
        mdl.add_constraints(mdl.sum(x[j,d,k] for j in set_clienti) == 1)

mdl.parameters.timelimit = (60*60)

s = mdl.solve(log_output=True)
print(s)
if s is not None:
    print(s.solve_status)

    for veicolo in range(veicoli*depositi):
        routes = [arc for arc in arcs if arc[2] == veicolo and x[arc].solution_value == 1.0]
        
        for c in routes:
            c1 = c[0]
            c2 = c[1]
            plot.plot([coord_nodi[c1][0],coord_nodi[c2][0]],[coord_nodi[c1][1],coord_nodi[c2][1]], c="#000000", marker='.', markersize=10)

    plot.axis('equal')
    plot.show()