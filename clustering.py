import math
from variables import load_varible_from_file, IMPORT_FROM_FILE
if IMPORT_FROM_FILE:
    load_varible_from_file()
from variables import clients, depots, clients_coord, depots_coord, vehicles, capacity, demand, demand_list, assigned_list

def dist(coords, clients, centroid_list):
    result = []
    for client in clients:
        x_cl = coords[client][0]
        y_cl = coords[client][1]
        distances = []
        for centroid in centroid_list:
            x_cen = centroid[0]
            y_cen = centroid[1]
            distances.append(math.sqrt((x_cl - x_cen) ** 2 + (y_cl - y_cen) ** 2))
        result.append(distances)
    return result


def find_min_centroid(distances):
    result = []
    for i in range(len(distances)):
        result.append(distances[i].index(min(distances[i])))
    return result


def find_occurences(min_centroid, centroid, offset):
    result = []
    for client in range(offset, len(min_centroid)):
        if min_centroid(client) == centroid:
            result.append(client)
    return result


def capacity_constraint(cliente, domanda, cluster, capacity):
    sum = domanda[cliente]
    for c in cluster:
        sum += domanda[c]
    return sum <= capacity


def update_centroids(clusters, coords, centroids, first):
    result = []

    for i in range(len(clusters)):
        if first:
            mean_x, mean_y = 0, 0
        else:
            mean_x = centroids[i][0]
            mean_y = centroids[i][1]

        for c in clusters[i]:
            mean_x += coords[c][0]
            mean_y += coords[c][1]

        if first:
            n = len(clusters[i])
        else:
            n = len(clusters[i]) + 1

        mean_x = round(mean_x / n, 2)
        mean_y = round(mean_y / n, 2)
        result.append((mean_x, mean_y))

    return result
def cluster_algorithm(solution_assignment):
    '''
    Fase 2 : Clusteringg
    Per ogni deposito, vengono suddivisi i veicoli tra i clienti assegnati
    a quel deposito nella fase precedente
    '''
    clustering_solution = [[] for _ in range(depots)]

    for deposit in solution_assignment:
        deposit_index = solution_assignment.index(deposit) # estraggo l'indice del deposito

        # calculate number of centroids
        sum = 0
        for c in deposit:
            sum += demand[c]
        N = math.ceil(sum/capacity)  # number of clusters

        #  select centroids
        centroids = [] # contiene le coordinate dei centroidi come pair
        old_centroids = [] # centroidi dell'iterazione precedente
        selected_centroids = [] # indici dei clienti centroidi nel primo step
        domanda_sort = demand_list.copy()
        domanda_sort.sort(reverse=True)

        for i in range(N):
            centroid_index = demand_list.index(domanda_sort[i])
            centroids.append(clients_coord[centroid_index])
            selected_centroids.append(centroid_index)

    #  algorithm for clustering
        done = False
        first = True
        i = 0
        iterations = 1
        distances, min_centroid, priority, clusters, centroid_index = [], [], [], [], []
        # clusters contiene per ogni deposito una lista contenente il numero di cluster 
        # e per ogni cluster una lista di clienti associati al cluster
        for i in range(N):
            clusters.append([selected_centroids[i]])
            assigned_list[selected_centroids[i]] = i

        while not done and iterations < 20:
            distances = dist(clients_coord, deposit, centroids)
            min_centroid = find_min_centroid(distances) # clienti più vicini al centroide
            for c in deposit:
                priority = []
                s = min_centroid[deposit.index(c)] # indice del centroide nella lista dei centroidi
                curr_centroid = s
                for centroid, i in zip(centroids,range(len(centroids))):
                    priority.append((distances[deposit.index(c)][i]/demand[c],i))

                priority.sort(key=lambda tup: tup[0])

                i = 0
                while assigned_list[c] is None and i < len(clusters):
                    # G = find_occurences(min_centroid,s,c[0] + 1)
                    if capacity_constraint(c, demand, clusters[curr_centroid], capacity):
                        print('soddisfo')
                        assigned_list[c] = curr_centroid
                        clusters[priority[i][1]].append(c)
                    else:
                        i += 1
                        if i < len(priority):
                            print('ciao')
                            curr_centroid = priority[i][1]

                if assigned_list[c] is None:
                    assigned_list[c] = priority[0][1]
                    clusters[priority[0][1]].append(c)

            old_centroids = centroids
            centroids = update_centroids(clusters, clients_coord, centroids, first)

            first = False
            if old_centroids == centroids:
                done = True
                print(f"Clusters for deposit {deposit_index} :", clusters)

            if done:
                clustering_solution[deposit_index].append(clusters)
                print(clustering_solution)
                
            clusters = []
            iterations += 1 
            for i in range(len(centroids)):
                clusters.append([])

            if not done:
                for i in range(len(assigned_list)):
                    assigned_list[i] = None
    
    return clustering_solution