import math
from docplex.mp.model import Model
from old_clustering import old_cluster_algorithm
from clustering import cluster_algorithm


'''
Fase 1 : Assignment Problem
Clients are assigned to a depot
'''
def assignment_clustering(clients, depots, vehicles, capacity, demand, clients_list, demand_list, clients_coord, depots_coord, assigned_list,
                            log_output_solution=True, print_solution=True):
    done = False
    pairs = [(i, j) for i in range(0, clients) for j in range(0, depots)]  # coppie customer-depots
    costs = {(i, j): math.sqrt((clients_coord[i][0] - depots_coord[j][0]) ** 2 + (clients_coord[i][1] - depots_coord[j][1]) ** 2) for i, j in pairs}
   
    mdl = Model('Assigment Problem')
    x = mdl.binary_var_dict(pairs, name='x')
    mdl.minimize(mdl.sum(costs[i, j]*x[i, j] for i in range(0, clients) for j in range(0, depots)))

    mdl.add_constraints(mdl.sum(x[i, j] for j in range(0, depots)) == 1 for i in range(0, clients))
    mdl.add_constraints(mdl.sum(demand[i]*x[i, j] for i in range(0, clients)) <= vehicles*capacity for j in range(0, depots))

    mdl.parameters.timelimit = (60*60)

    while not done:
        solution_assignment = [[] for _ in range(depots)]
        s = mdl.solve(log_output=log_output_solution)
        for pair in pairs:
            if x[pair].solution_value > 0.1:
                solution_assignment[pair[1]].append(pair[0])

        clusters = cluster_algorithm(clients, depots, vehicles, capacity, demand, clients_list, demand_list, clients_coord, depots_coord, assigned_list,
                                        solution_assignment, 20)

        # clusters = old_cluster_algorithm(clients, depots, vehicles, capacity, demand, clients_list, demand_list, clients_coord, depots_coord, assigned_list,
        #                                 solution_assignment, 20)  

        # clusters = [item for sublist in clusters for item in sublist]
        no_problems = True
        for deposit in clusters:
            for cluster in deposit:
                temp = [demand[c] for c in cluster]
                sum_demands = sum(temp)
                if sum_demands > capacity:
                    mdl.add_constraints(mdl.sum(x[i, j] for i in cluster) != len(cluster) for j in range(0, depots))
                    no_problems = False

        if no_problems:
            done = True

    if print_solution:
        for cluster, i in zip(solution_assignment, range(depots)):
            print(f'Cluster {i} -> {cluster}')

    

    return clusters
if __name__ == '__main__':
    assignment_clustering()