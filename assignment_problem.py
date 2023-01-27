import imp
import math
from docplex.mp.model import Model
from variables import load_varible_from_file, IMPORT_FROM_FILE
if IMPORT_FROM_FILE:
    load_varible_from_file()
from variables import clients, depots, clients_coord, depots_coord, vehicles, capacity, demand

'''
Fase 1 : Assignment Problem
Clients are assigned to a depot
'''
def solve_assignment_problem(log_output_solution=True, print_solution=True):
    pairs = [(i, j) for i in range(0, clients) for j in range(0, depots)]  # coppie customer-depots
    costs = {(i, j): math.sqrt((clients_coord[i][0] - depots_coord[j][0]) ** 2 + (clients_coord[i][1] - depots_coord[j][1]) ** 2) for i, j in pairs}
    solution_assignment = [[] for _ in range(depots)]
   
    mdl = Model('Assigment Problem')
    x = mdl.binary_var_dict(pairs, name='x')
    mdl.minimize(mdl.sum(costs[i, j]*x[i, j] for i in range(0, clients) for j in range(0, depots)))

    mdl.add_constraints(mdl.sum(x[i, j] for j in range(0, depots)) == 1 for i in range(0, clients))
    mdl.add_constraints(mdl.sum(demand[i]*x[i, j] for i in range(0, clients)) <= vehicles*capacity for j in range(0, depots))
    
    # TU NON VAI QUI!!!
    mdl.add_constraint(x[12,0] == 0)
    mdl.add_constraint(x[7,0] == 0)
    mdl.add_constraint(x[5,0] == 0)
    mdl.add_constraint(x[10,2] == 0)
    mdl.add_constraint(x[7,2] == 0)
    mdl.add_constraint(x[8,0] == 0)
    mdl.add_constraint(x[13,0] == 0)
    mdl.add_constraint(x[1,0] == 0)
    mdl.add_constraint(x[12,2] == 0)
    mdl.add_constraint(x[6,2] == 0)

    mdl.parameters.timelimit = (60*60)
    s = mdl.solve(log_output=log_output_solution)

    for pair in pairs:
        if x[pair].solution_value == 1.0:
            solution_assignment[pair[1]].append(pair[0])
    if print_solution:
        for cluster, i in zip(solution_assignment, range(depots)):
            print(f'Cluster {i} -> {cluster}')

    return solution_assignment
if __name__ == '__main__':
    solve_assignment_problem()