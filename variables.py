from numpy import random
from json import loads
import os
'''
Variables declaration
'''
IMPORT_FROM_FILE = False
BENCH_MARK = True
clients = 10 # number of clients 
depots = 2 # number of depots
vehicles = 4 # number of vehicles
capacity = 60 # capacity

clients_list = [i for i in range(clients)] # list of clients
assigned_list = [None for i in range(clients)] # list of assigned clients to cluster
demand = {i: random.randint(1, 30) for i in clients_list} # demand for each clients
demand_list = list(demand.values()) # list of clients' demand

clients_coord = [(round(random.rand() * 200, 2),
                    round(random.rand() * 100, 2)) for _ in range(clients)] # clients' coordinates

depots_coord = [(round(random.rand() * 200, 2),
                    round(random.rand() * 100, 2)) for _ in range(depots)] # depots' coordinates

def generate_file_variables(clients,depots,vehicles,capacity,clients_list,demand_list,clients_coord,depots_coord):
    i = 1
    while os.path.isfile(f"problems/problem_{i}.txt"):
        i += 1
    f = open(f"problems/problem_{i}.txt", "w")
    f.write(f'Clienti - {clients}\nDepositi - {depots}\n')
    f.write(f'Veicoli - {vehicles}\nCapacita - {capacity}\n')
    f.write(f'Lista Clienti - {clients_list}\n')
    f.write(f'Lista di Domanda - {demand_list}\n')
    f.write(f'Coordinate Clienti - {clients_coord}\n')
    f.write(f'Coordinate Depositi - {depots_coord}\n')
    f.close()
def load_varible_from_file():
    # f = open("p01.txt", 'r')
    f = open("problems/problem_14.txt", 'r')

    lines = f.readlines()
    lines = [line.replace('\n', '').replace(' ', '') for line in lines]
    lines = [tuple(line.split('-')) for line in lines]

    clients = int(lines[0][1]) 
    depots = int(lines[1][1])
    vehicles = int(lines[2][1])
    capacity = int(lines[3][1])
    
    clients_list = eval(lines[4][1])
    demand_list = eval(lines[5][1])
    clients_coord = eval(lines[6][1])
    depots_coord = eval(lines[7][1])

    f.close()
    
    demand = {i: demand_list[i] for i in clients_list}
    assigned_list = [None for i in range(clients)]

    return clients, depots, vehicles, capacity, demand, clients_list, demand_list, clients_coord, depots_coord, assigned_list

def load_benchmark(n):
    demand = {}
    clients_coord = []
    depots_coord = []

    if n < 10:
        n = f'0{n}'
    else:
        n = str(n)

    f = open(f"benchmark/p{n}.txt", 'r')
    lines = f.readlines()
    lines = [tuple(line.split()) for line in lines]

    vehicles = int(lines[0][1])
    clients = int(lines[0][2])
    clients_list = list(range(clients))
    depots = int(lines[0][3])
    capacity = int(lines[1][1])
    for i in range(depots + 1, depots + clients + 1):
        clients_coord.append((int(lines[i][1]), int(lines[i][2])))
        demand[i - depots - 1] = int(lines[i][4])

    for i in range(depots + clients + 1, len(lines)):
        depots_coord.append((int(lines[i][1]), int(lines[i][2])))

    demand_list = list(demand.values())
    assigned_list = [None for _ in range(clients)]
    return clients, depots, vehicles, capacity, demand, clients_list, demand_list, clients_coord, depots_coord, assigned_list

def print_variables():
    print(f'Clienti - {clients}\nDepositi - {depots}')
    print(f'Veicoli - {vehicles}\nCapacità - {capacity}')
    print(f'Lista Clienti - {clients_list}')
    print(f'Lista Clienti Assegnati - {assigned_list}')
    print(f'Domanda per Cliente - {demand}')
    print(f'Lista di Domanda - {demand_list}')
    print(f'Coordinate Clienti - {clients_coord}')
    print(f'Coordinate Depositi - {depots_coord}')

if __name__ == '__main__':
    load_benchmark(1)
    #generate_file_variables(clients,depots,vehicles,capacity,clients_list,demand_list,clients_coord,depots_coord)
    #load_varible_from_file()
    #print_variables()