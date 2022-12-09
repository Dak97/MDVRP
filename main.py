import math
import cplex
from docplex.mp.model import Model
from numpy import random
import matplotlib.pyplot as plot
from clustering import cluster_algorithm, dist, find_min_centroid, find_occurences, capacity_constraint, update_centroids
from variables import load_varible_from_file, IMPORT_FROM_FILE
from assignment_problem import solve_assignment_problem
if IMPORT_FROM_FILE:
    load_varible_from_file()
from variables import clients, depots, vehicles, capacity, clients_list, assigned_list, demand, demand_list, clients_coord, depots_coord


solution_assignment = solve_assignment_problem(log_output_solution=False)

clustering_solution = cluster_algorithm(solution_assignment)

print(clustering_solution)


'''
Fase 3: Ottimizzazione binaria.
Per ogni deposito, per ogni cluster ottenuto nel passo precedente viene
determinato tramite un problema di ottimizzazione binaria il percorso che
il veicolo deve effettuare per visitare tutti i clienti assegnatagli 
minimizzando il costo
'''
print("FASE DI OTTIMIZAZIONE BINARIA")
indice_deposito = -1
optimization_solutions = [[] for deposit in range(depots)]
for deposit in range(depots):
    for cluster in [item for sublist in clustering_solution[deposit] for item in sublist]:
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
        print(mdl.add_constraints(mdl.sum(x[i, j] for j in set_vertici if j != i) == 1 for i in cluster))
        print(mdl.add_constraints(mdl.sum(x[i, j] for i in set_vertici if i != j) == 1 for j in cluster))

        #print(mdl.add_constraint(mdl.sum(x[-1, j] for j in cluster) == vehicles))
        #mdl.add_constraint(mdl.sum(x[i, -1] for i in cluster) == vehicles)
        mdl.add_constraints(
            (u[i] - u[j] + (capacity * x[i, j]) <= capacity - demand[j]) for i in cluster for j in cluster if
            i != j)
        mdl.add_constraints(u[i] >= demand[i] for i in cluster)
        mdl.parameters.timelimit = (60 * 60)
        s = mdl.solve(log_output=True)
        print(s, s.solve_status)

        local_solution = []
        for arc in arcs:
            if x[arc].solution_value == 1.0:
                local_solution.append(arc)
        
        optimization_solutions[deposit].append(local_solution)

# for s in optimization_solutions:
#     print(s)
for deposit in optimization_solutions:
    print("deposit :", deposit)
    deposit_index = optimization_solutions.index(deposit)
    for cluster in deposit:
        print("cluster :", cluster)
        for pair in cluster:
            print("pair :", pair)
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

marker_list = ['*', 'd', '+', 'P']
for deposit in clustering_solution:
    deposit_index = clustering_solution.index(deposit)
    plot.plot(depots_coord[deposit_index][0], depots_coord[deposit_index][1], c="#000000", marker='v', markersize=10)
    plot.annotate('$D_%d$' % deposit_index, (depots_coord[deposit_index][0] + 1, depots_coord[deposit_index][1]))
    marker = marker_list[deposit_index]
    for cluster in deposit[0]:
        print(cluster)
        color = random.rand(3,)
        for c in cluster:
            plot.plot(clients_coord[c][0], clients_coord[c][1], c=color, marker=marker, markersize=5)
            plot.annotate('$c_{%d}$' % c, (clients_coord[c][0] + 1, clients_coord[c][1]))
plot.axis('equal')
# plot.show()
print(optimization_solutions)

plot.axis('equal')
plot.show()

