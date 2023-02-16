import cplex
from docplex.mp.model import Model
import matplotlib.pyplot as plot
import math
from variables import generate_file_variables, load_benchmark
from numpy import random

LOAD_FROM_FILE = True

def load_from_file(n_prob):
    f = open(f"problems/problem_{n_prob}.txt", 'r')
    lines = f.readlines()
    lines = [line.replace('\n', '').replace(' ', '') for line in lines]
    lines = [tuple(line.split('-')) for line in lines]

    return int(lines[0][1]), int(lines[1][1]), int(lines[2][1]), int(lines[3][1]), eval(lines[5][1]), eval(lines[6][1])+eval(lines[7][1])
    
if LOAD_FROM_FILE:
    # clienti, depositi, veicoli, capacity, domanda, coord_nodi = load_from_file(5)
    clienti, depositi, veicoli, capacity, domanda, set_clienti, demand_list, \
    clients_coord, depots_coord, assigned_list = load_benchmark(23)
    coord_nodi = clients_coord + depots_coord
    set_depositi = range(clienti, clienti+depositi)
else:
    depositi = 2
    clienti = 13
    capacity = 10
    veicoli = 2

    set_clienti = range(clienti)
    set_depositi = range(clienti, clienti+depositi)

    flag = False
    while(not flag):
        domanda = [random.randint(1, capacity) for i in set_clienti] # demand for each clients
        print("sum(domanda): ",sum(domanda))
        if depositi*capacity*veicoli >= sum(domanda):
            flag = True

    coord_nodi = [(int(random.rand() * 200),int(random.rand() * 100)) for _ in range(clienti)] + [(int(random.rand() * 200),
                        int(random.rand() * 100)) for _ in range(depositi)]

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
# print(len(arcs))
# print(y)
# print(costo)
# print(u)
#print(load_from_file(1))

# generate_file_variables(clienti,depositi,veicoli,capacity,list(set_clienti),domanda,
#                         coord_nodi[0:clienti],coord_nodi[clienti:clienti+depositi])

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

mdl.parameters.timelimit = (60*120)

s = mdl.solve(log_output=True)
print(s._objective)
if s is not None:
    #print(s.solve_status)

    for veicolo in range(veicoli*depositi):
        routes = [arc for arc in arcs if arc[2] == veicolo and x[arc].solution_value > 0.1]

        for c in routes:
            c1 = c[0]
            c2 = c[1]
            plot.plot([coord_nodi[c1][0],coord_nodi[c2][0]],[coord_nodi[c1][1],coord_nodi[c2][1]], c="#000000", markersize=10)

    for coord in coord_nodi:
        if coord_nodi.index(coord) >= clienti:
            color = '#FF0000'
        else:
            color = '#000000'
        plot.plot(coord[0], coord[1], c=color,marker='.',markersize=10)

    plot.axis('equal')
    plot.show()