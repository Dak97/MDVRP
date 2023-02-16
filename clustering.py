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
        i = 0
        for centroid in centroid_list:
            x_cen = centroid[0]
            y_cen = centroid[1]
            distances.append((math.sqrt((x_cl - x_cen) ** 2 + (y_cl - y_cen) ** 2), i))
            i += 1
        distances.sort(key=lambda tup: tup[0])
        result.append(distances)
    return result



def find_min_centroid(clients,distances):
    result = {}
    for i in range(len(distances)):
        result[clients[i]] = distances[i][0][1] # restituisce l'indice del centroide più vicino
    return result

def unassigned_clients_closest_to_s(depot_clients,assigned_list,min_centroid,curr_centroid):
    result = []
    for c in depot_clients:
        if min_centroid[c] == curr_centroid and assigned_list[c] is None:
            result.append(c)
    return result



def find_occurences(min_centroid, centroid, offset):
    result = []
    for client in range(offset, len(min_centroid)):
        if min_centroid(client) == centroid:
            result.append(client)
    return result

def isEqual(old_centroids, centroids):
    for i in range(len(centroids)):
        if not(abs(centroids[i][0] - old_centroids[i][0]) <= 0.10 and abs(centroids[i][1] - old_centroids[i][1]) <= 0.10):
            return False
    return True

def capacity_constraint(cliente, domanda, cluster, capacity):
    sum = domanda[cliente]
    for c in cluster:
        sum += domanda[c]
    return sum <= capacity


def update_centroids(clusters, coords, centroids, first):
    result = []
    # print(f"printami cluster:{clusters}")

    for i in range(len(clusters)):
        mean_x, mean_y = 0, 0

        for c in clusters[i]:
            mean_x += coords[c][0]
            mean_y += coords[c][1]

        n = len(clusters[i])

        mean_x = round(mean_x / n, 2)
        mean_y = round(mean_y / n, 2)
        
        # print(f"enne: {n}")

        result.append((mean_x, mean_y))

    return result
def cluster_algorithm(clients, depots, vehicles, capacity, demand, clients_list, demand_list, clients_coord, depots_coord, assigned_list,
                        solution_assignment, n_iter):
    '''
    Fase 2 : Clusteringg
    Per ogni deposito, vengono suddivisi i veicoli tra i clienti assegnati
    a quel deposito nella fase precedente
    '''
    clustering_solution = [[] for _ in range(depots)]
    it = 0
    assigned_list = [None for i in range(clients)]
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
        domanda_sort = [(demand_list[i],i) for i in deposit]
        domanda_sort.sort(key= lambda tup: tup[0], reverse=True)

        for i in range(N):
            centroid_index = domanda_sort[i][1]
            centroids.append(clients_coord[centroid_index])
            selected_centroids.append(centroid_index)

    #  algorithm for clustering
        done = False
        first = True
        i = 0
        distances, min_centroid, priority, clusters, centroid_index = [], {}, [], [], []
        # clusters contiene per ogni deposito una lista contenente il numero di cluster 
        # e per ogni cluster una lista di clienti associati al cluster
        for i in range(N):
            clusters.append([selected_centroids[i]])
            assigned_list[selected_centroids[i]] = i

        
        while not done:
            distances = dist(clients_coord, deposit, centroids) # calcolo le distanze tra cliente e centroide e ordino
            min_centroid = find_min_centroid(deposit, distances)  # per ogni cliente, l'indice del centroide più vicino

            for c in deposit:
                dist_iterator = 0
                
                while assigned_list[c] is None:
                    priority = []

                    curr_centroid = min_centroid[c]  # indice del centroide nella lista dei centroidi
                    G = unassigned_clients_closest_to_s(deposit, assigned_list, min_centroid, curr_centroid)
                    for client in G:
                        priority.append((distances[deposit.index(client)][0][0] / demand[client], client))
                    priority.sort(key=lambda tup: tup[0])

                    for value in priority:
                        unas_client = value[1]
                        if capacity_constraint(unas_client, demand, clusters[curr_centroid], capacity):
                            assigned_list[unas_client] = curr_centroid
                            clusters[curr_centroid].append(unas_client)

                    if assigned_list[c] is None:
                        dist_iterator += 1
                        if dist_iterator >= len(distances[deposit.index(c)]):
                            curr_centroid = distances[deposit.index(c)][0][1]
                            assigned_list[c] = curr_centroid
                            clusters[curr_centroid].append(c)
                        else:
                            min_centroid[c] = distances[deposit.index(c)][dist_iterator][1]
                        
                        

            old_centroids = centroids
            centroids = update_centroids(clusters, clients_coord, centroids, first)
            first = False

            if isEqual(old_centroids,centroids):
                done = True
                print(f"Clusters for deposit {deposit_index} :", clusters)
            
            print("\nOld centroids:\n",old_centroids,"\n New centroids\n",centroids)
                

            it += 1
            if it >= 19:
                done = True # raggiunte numero massimo di iterazioni

            if done:
                clustering_solution[deposit_index] = clusters
                print(clustering_solution)

            
            clusters = []


            for i in range(len(centroids)):
                clusters.append([])

            if not done:
                for i in range(len(assigned_list)):
                    assigned_list[i] = None
    
    return clustering_solution