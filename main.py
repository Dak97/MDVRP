import math
import cplex
from docplex.mp.model import Model
from numpy import random
import matplotlib.pyplot as plot
import time

from variables import load_varible_from_file, load_benchmark, IMPORT_FROM_FILE, BENCH_MARK
from assignment_problem import assignment_clustering

if BENCH_MARK:
    clients, depots, vehicles, capacity, demand, clients_list, demand_list, \
    clients_coord, depots_coord, assigned_list = load_benchmark(2)

if IMPORT_FROM_FILE:
   clients, depots, vehicles, capacity, demand, clients_list, demand_list,\
    clients_coord, depots_coord, assigned_list = load_varible_from_file(1)

start_time = time.time()


clustering_solution = assignment_clustering(clients, depots, vehicles, capacity, demand, clients_list, demand_list,
                                            clients_coord, depots_coord, assigned_list, log_output_solution=False, print_solution=False)

print("----------------------------------------------")
print("PROBLEMA DI ASSEGMANETO E CLUSTERING TERMINATO")
print("----------------------------------------------")


print(f"Soluzione del clustering:\n{clustering_solution}\n\n")

'''
Fase 3: Ottimizzazione binaria
Per ogni deposito, per ogni cluster ottenuto nel passo precedente viene
determinato tramite un problema di ottimizzazione binaria il percorso che
il veicolo deve effettuare per visitare tutti i clienti assegnatagli 
minimizzando il costo
'''
indice_deposito = -1
sum_objective = 0
optimization_solutions = [[] for deposit in range(depots)]
for deposit in range(depots):
    for cluster in clustering_solution[deposit]:
        set_vertici = cluster + [indice_deposito]
        arcs = [(i, j) for i in set_vertici for j in set_vertici if i != j]
        costo = {}
        for i, j in arcs:
            if i == -1:
                costo[(i, j)] = math.sqrt((clients_coord[j][0] - depots_coord[deposit][0]) ** 2 + (clients_coord[j][1] - depots_coord[deposit][1]) ** 2)
            elif j == -1:
                costo[(i, j)] = math.sqrt((depots_coord[deposit][0] - clients_coord[i][0]) ** 2 + (
                            depots_coord[deposit][1] - clients_coord[i][1]) ** 2)
            else:
                costo[(i,j)] = math.sqrt((clients_coord[j][0] - clients_coord[i][0]) ** 2 + (
                            clients_coord[j][1] - clients_coord[i][1]) ** 2)

        mdl = Model('MDVRP')
        x = mdl.binary_var_dict(arcs, name='x')  # variabili decisionali
        u = mdl.continuous_var_dict(cluster, ub=capacity, name='u')  # upper bound
        mdl.minimize(mdl.sum(costo[i, j] * x[i, j] for i in set_vertici for j in set_vertici if i != j))
        mdl.add_constraints(mdl.sum(x[i, j] for j in set_vertici if j != i) == 1 for i in cluster)
        mdl.add_constraints(mdl.sum(x[i, j] for i in set_vertici if i != j) == 1 for j in cluster)

        mdl.add_constraint(mdl.sum(x[-1, j] for j in cluster) == 1)
        mdl.add_constraint(mdl.sum(x[i, -1] for i in cluster) == 1)

        mdl.add_constraints(
            (u[i] - u[j] + (capacity * x[i, j]) <= capacity - demand[j]) for i in cluster for j in cluster if
            i != j)

        mdl.add_constraints(u[i] >= demand[i] for i in cluster)
        mdl.parameters.timelimit = (60 * 60)
        s = mdl.solve(log_output=False)
        # print(s, s.solve_status)
        sum_objective += s._objective
        local_solution = []
        for arc in arcs:
            if x[arc].solution_value > 0.1:
                local_solution.append(arc)
        
        optimization_solutions[deposit].append(local_solution)

end_time = time.time()

print("FASE DI OTTIMIZAZIONE BINARIA TERMINATO")

print(f"\n\nIl tempo totale dell'algoritmo è: {end_time-start_time}")
print(f"\nLa somma delle funzioni obiettivo è: {sum_objective}\n")

# for s in optimization_solutions:
#     print(s)
for deposit in optimization_solutions:
    # print("deposit :", deposit)
    deposit_index = optimization_solutions.index(deposit)
    for cluster in deposit:
        # print("cluster :", cluster)
        for pair in cluster:
            # print("pair :", pair)
            if pair[0] == -1:
                v1 = depots_coord[deposit_index]
                v2 = clients_coord[pair[1]]

            elif pair[1] == -1:
                v1 = clients_coord[pair[0]]
                v2 = depots_coord[deposit_index]

            else:
                v1 = clients_coord[pair[0]]
                v2 = clients_coord[pair[1]]

            plot.plot([v1[0], v2[0]], [v1[1], v2[1]], color='#000000')

marker_list = ['*', 'd', '+', 'P', 's', 'h', 'x','^','v','>','<']
for deposit in clustering_solution:
    deposit_index = clustering_solution.index(deposit)
    plot.plot(depots_coord[deposit_index][0], depots_coord[deposit_index][1], c="#000000", marker='v', markersize=10)
    plot.annotate('$D_%d$' % deposit_index, (depots_coord[deposit_index][0] + 1, depots_coord[deposit_index][1]))
    marker = marker_list[deposit_index]
    for cluster in deposit:
        # print(cluster)
        color = random.rand(3,)
        for c in cluster:
            plot.plot(clients_coord[c][0], clients_coord[c][1], c=color, marker=marker, markersize=5)
            plot.annotate('$c_{%d}$' % c, (clients_coord[c][0] + 1, clients_coord[c][1]))
plot.axis('equal')
# plot.show()
# print(optimization_solutions)

plot.axis('equal')
plot.show()

