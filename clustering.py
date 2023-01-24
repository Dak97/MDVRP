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
            distances.append(
                math.sqrt((x_cl - x_cen) ** 2 + (y_cl - y_cen) ** 2))
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

        if len(clusters[i]) > 0:
            n = len(clusters[i])
        else:
            n = len(clusters[i]) + 1

        mean_x = round(mean_x / n, 2)
        mean_y = round(mean_y / n, 2)
        result.append((mean_x, mean_y))

    return result


def reorganize_clusters(clusters, priority, wrong, demands, capacity, assigned):
    i = 0
    sorted_demand_clusters = []
    for cluster in clusters:
        current_list = [(demands[c], c) for c in cluster]
        current_list.sort(key=lambda tup: tup[0])
        sorted_demand_clusters.append(current_list)

        # rappresento ciascun cluster come coppia (domanda cliente, cliente) ordinando in modo crescente in base alla domanda
    for client in clusters[wrong]:  # per ogni cliente del cluster da sistemare
        # ottengo la priorità di quel cliente
        client_priority = priority[client]
        for other_priority in client_priority:  # per ogni valore nella priorità e quindi per ogni cluster
            # se si tratta di un cluster diverso da quello da sistemare
            if other_priority[1] != wrong:
                # ricava la rappresentazione della domanda di quel cluster
                sort_other = sorted_demand_clusters[other_priority[1]]
                print(demands)
                while i < len(sort_other) and sort_other[i][0] < demands[client]:
                    # finché la domanda del cliente nel'altro cluster è minore di quello che dobbiamo spostare
                    capacity_wrong = sum(
                        i for i, j in sorted_demand_clusters[wrong])
                    capacity_other = sum(i for i, j in sort_other)
                    # ottieni le capacità totali dei 2 cluster
                    if capacity_wrong - demands[client] + sort_other[i][0] <= capacity and capacity_other + demands[client] - sort_other[i][0] <= capacity:
                        # controlla se effettuando uno scambio entrambi i cluster soddisfano il capacity constraint
                        assigned[client] = other_priority[1]
                        assigned[sort_other[i][1]] = wrong
                        print(sort_other[i][1])
                        print(clusters[wrong], clusters[other_priority[1]])
                        clusters[wrong].remove(client)
                        clusters[wrong].append(sort_other[i][1])

                        clusters[other_priority[1]].remove(sort_other[i][1])
                        clusters[other_priority[1]].append(client)
                        # se sì, effettua lo scambio e termina l'esecuzione della funzione
                        return
                    else:
                        # altrimenti passa al cliente successivo di quel cluster
                        i += 1


def cluster_algorithm(solution_assignment):
    '''
    Fase 2 : Clusteringg
    Per ogni deposito, vengono suddivisi i veicoli tra i clienti assegnati
    a quel deposito nella fase precedente
    '''
    clustering_solution = [[] for _ in range(depots)]

    for deposit in solution_assignment:
        print(deposit)
        deposit_index = solution_assignment.index(
            deposit)  # estraggo l'indice del deposito

        # calculate number of centroids
        sum = 0
        for c in deposit:
            sum += demand[c]
        N = math.ceil(sum/capacity)  # number of clusters

        #  select centroids
        centroids = []  # contiene le coordinate dei centroidi come pair
        old_centroids = []  # centroidi dell'iterazione precedente
        selected_centroids = []  # indici dei clienti centroidi nel primo step
        domanda_sort = [(demand_list[i],i) for i in deposit]
        domanda_sort.sort(reverse=True, key= lambda tup: tup[0])

        for i in range(N):
            centroid_index = domanda_sort[i][1]
            centroids.append(clients_coord[centroid_index])
            selected_centroids.append(centroid_index)

    #  algorithm for clustering
        done = False
        first = True
        i = 0
        iterations = 1
        distances, min_centroid, clusters, centroid_index = [], [], [], []
        priority = {}
        # clusters contiene per ogni deposito una lista contenente il numero di cluster
        # e per ogni cluster una lista di clienti associati al cluster
        for i in range(N):
            clusters.append([selected_centroids[i]])
            assigned_list[selected_centroids[i]] = i

        if len(deposit) == 1:
            done = True

        # if N == 1:
        #     clustering_solution.append([deposit]) 
        #     done = True

        while not done and iterations < 20:
            distances = dist(clients_coord, deposit, centroids)
            # clienti più vicini al centroide
            min_centroid = find_min_centroid(distances)
            for c in deposit:
                priority[c] = []
                # indice del centroide nella lista dei centroidi
                s = min_centroid[deposit.index(c)]
                curr_centroid = s
                for centroid, i in zip(centroids, range(len(centroids))):
                    priority[c].append(
                        (distances[deposit.index(c)][i]/demand[c], i))

                priority[c].sort(key=lambda tup: tup[0])

                i = 0
                print(clusters)
                while assigned_list[c] is None and i < len(clusters):
                    # G = find_occurences(min_centroid,s,c[0] + 1)
                    if capacity_constraint(c, demand, clusters[curr_centroid], capacity):
                        # print('soddisfo')
                        assigned_list[c] = curr_centroid
                        clusters[priority[c][i][1]].append(c)
                    else:
                        i += 1
                        if i < len(priority[c]):
                            # print('ciao')
                            curr_centroid = priority[c][i][1]

                if assigned_list[c] is None:
                    print(c)
                    assigned_list[c] = priority[c][0][1]
                    clusters[priority[c][0][1]].append(c)
                    reorganize_clusters(
                        clusters, priority, priority[c][0][1], demand_list, capacity, assigned_list)

            old_centroids = centroids
            centroids = update_centroids(
                clusters, clients_coord, centroids, first)

            first = False
            if old_centroids == centroids:
                done = True
                print(f"Clusters for deposit {deposit_index} :", clusters)

            iterations += 1
        
            if not done and iterations < 20:
                clusters = []
                for i in range(len(centroids)):
                    clusters.append([])
                for i in range(len(assigned_list)):
                    assigned_list[i] = None

        clustering_solution[deposit_index].append(clusters)
        print(clustering_solution)

    return clustering_solution
