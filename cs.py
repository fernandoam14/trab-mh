# Author: Fernando Amaral Musso

from random import uniform, shuffle, sample, randint
from math import exp, inf

def simulated_annealing_clustering_search(sa_to, sa_tf, sa_alpha, sa_max_iter, sa_max_bad_iter, cs_n_clusters, cs_lambda, depot, customers, distances, demands, k_vehicles, capacity):
    # Initial solution to Simulated Annealing
    s = generate_random_solution(depot, customers, distances, demands, k_vehicles, capacity)
    best_s = s

    # Clusters initialization
    clusters = []

    for _ in range(cs_n_clusters):
        random_solution = generate_random_solution(depot, customers, distances, demands, k_vehicles, capacity)
        clusters.append([random_solution, 1])

    # Variables initialization
    best_s = s
    current_t = sa_to
    current_iter = 0
    current_bad_iter = 0
    improved = False

    while current_t > sa_tf and current_bad_iter <= sa_max_bad_iter:
        # Simulated Annealing module
        while current_iter <= sa_max_iter:
            current_iter += 1
            neighbor_s = find_any_neighbor(s, depot, distances, demands, capacity)
            delta = solution_total_cost(neighbor_s, depot, distances) - solution_total_cost(s, depot, distances)

            if delta < 0:
                s = neighbor_s

                if solution_total_cost(s, depot, distances) < solution_total_cost(best_s, depot, distances):
                    best_s = s
                    improved = True
            else:
                if uniform(0, 1) < exp(- delta / current_t):
                    s = neighbor_s

        # Clustering process
        closest_cluster = None
        closest_dist = inf

        for c in clusters:
            dist = solution_distance(c[0], s)

            if dist < closest_dist:
                closest_cluster = c
                closest_dist = dist

        closest_cluster[1] += 1

        # Assimilation process
        closest_cluster[0] = assimilation(closest_cluster[0], s, depot, customers, distances, demands, capacity)

        # Local Search phase
        if closest_cluster[1] >= cs_lambda:
            closest_cluster[1] = 1
            local_search_s = local_search(closest_cluster[0], depot, customers, distances, demands, capacity)

            if solution_total_cost(local_search_s, depot, distances) < solution_total_cost(closest_cluster[0], depot, distances):
                closest_cluster[0] = local_search_s

            if solution_total_cost(closest_cluster[0], depot, distances) < solution_total_cost(best_s, depot, distances):
                best_s = closest_cluster[0]
                improved = True

        # Prepare next iteration
        current_t *= sa_alpha
        current_iter = 0

        if improved:
            current_bad_iter = 0
            improved = False
        else:
            current_bad_iter += 1

    return best_s, solution_total_cost(best_s, depot, distances)

def generate_random_solution(depot, customers, distances, demands, k_vehicles, capacity):
    remaining_customers = [c for _,c in sorted(zip(demands[2:], customers))]
    s = []
    count = 0

    for _ in range(k_vehicles):
        s.append([])

    while remaining_customers:
        count += 1

        if count <= len(customers):
            shuffle(s)
        else:
            s = find_any_neighbor(s, depot, distances, demands, capacity)

        c = remaining_customers[0]

        for index in range(k_vehicles):
            (can_attend, new_r) = randomly_attend_customer(s[index], c, demands, capacity)

            if can_attend:
                s[index] = new_r
                remaining_customers.remove(c)
                break

    return s

def find_any_neighbor(s, depot, distances, demands, capacity):
    neighbor_s = []

    for r in s:
        neighbor_s.append(list(r))

    move = randint(0, 3)

    if move == 0:
        move_operator(neighbor_s)
    elif move == 1:
        swap_operator(neighbor_s)
    elif move == 2:
        inversion_operator(neighbor_s)
    else:
        exchange_operator(neighbor_s, depot, distances, demands, capacity)

    return neighbor_s

def assimilation(s1, s2, depot, customers, distances, demands, capacity):
    dist = solution_distance(s1, s2)
    new_dist = 0
    best_neighbor = s1
    next_neighbor = s1

    while new_dist < dist:
        new_neighbor = []

        for r in next_neighbor:
            new_neighbor.append(list(r))

        move = randint(0, 3)

        if move == 0:
            move_operator(new_neighbor)
        elif move == 1:
            swap_operator(new_neighbor)
        elif move == 2:
            inversion_operator(new_neighbor)
        else:
            exchange_operator(new_neighbor, depot, distances, demands, capacity)

        new_dist = solution_distance(new_neighbor, s2)

        if new_dist < dist:
            next_neighbor = new_neighbor

            if solution_total_cost(new_neighbor, depot, distances) < solution_total_cost(best_neighbor, depot, distances):
                best_neighbor = new_neighbor

    return best_neighbor

def local_search(s, depot, customers, distances, demands, capacity):
    improved = True

    while improved:
        improved = False
        best_neighbor = s
        best_total_cost = solution_total_cost(best_neighbor, depot, distances)

        for _ in range(len(customers)):
            new_neighbor = []

            for r in best_neighbor:
                new_neighbor.append(list(r))

            move = randint(0, 3)

            if move == 0:
                move_operator(new_neighbor)
            elif move == 1:
                swap_operator(new_neighbor)
            elif move == 2:
                inversion_operator(new_neighbor)
            else:
                exchange_operator(new_neighbor, depot, distances, demands, capacity)

            total_cost = solution_total_cost(new_neighbor, depot, distances)

            if total_cost < best_total_cost:
                improved = True
                best_neighbor = new_neighbor
                best_total_cost = total_cost

        s = best_neighbor

    return s

def solution_total_cost(s, depot, distances):
    total_cost = 0

    for r in s:
        total_cost += route_total_cost(r, depot, distances)

    return int(total_cost)

def route_total_cost(r, depot, distances):
    if len(r) == 0:
        return 0
    else:
        total_cost = distances[depot][r[0]] + distances[r[-1]][depot]

        index1 = 0
        index2 = 1

        while index2 < len(r):
            total_cost += distances[r[index1]][r[index2]]
            index1 += 1
            index2 += 1

        return total_cost

def route_total_demand(r, demands):
    total_demand = 0

    for c in r:
        total_demand += demands[c]

    return total_demand

def randomly_attend_customer(r, c, demands, capacity):
    new_r = list(r)

    index = randint(0,len(new_r))
    new_r.insert(index, c)

    if route_total_demand(new_r, demands) <= capacity:
        return True, new_r
    else:
        return False, r

def bestly_attend_customer(r, c, depot, distances, demands, capacity):
    if route_total_demand((r + [c]), demands) <= capacity:
        best_r = r
        best_total_cost = inf
        index = 0

        while index <= len(r):
            new_r = list(r)
            new_r.insert(index, c)

            total_cost = route_total_cost(new_r, depot, distances)

            if total_cost < best_total_cost:
                best_r = new_r
                best_total_cost = total_cost

            index += 1

        return True, best_r
    else:
        return False, r

def move_operator(s):
    [r] = sample(s, 1)

    if len(r) >= 1:
        [c] = sample(r, 1)
        r.remove(c)

        index = randint(0,len(r))
        r.insert(index, c)

def swap_operator(s):
    [r] = sample(s, 1)

    if len(r) >= 2:
        [c1, c2] = sample(r, 2)

        aux = r.index(c1)
        r[r.index(c2)] = c1
        r[aux] = c2

def inversion_operator(s):
    [r] = sample(s, 1)

    if len(r) >= 2:
        [c1, c2] = sample(r, 2)
        aux = s.index(r)

        if r.index(c1) < r.index(c2):
            r = r[:(r.index(c1) + 1)] + [c for c in reversed(r[(r.index(c1) + 1):r.index(c2)])] + r[r.index(c2):]
        else:
            r = r[:(r.index(c2) + 1)] + [c for c in reversed(r[(r.index(c2) + 1):r.index(c1)])] + r[r.index(c1):]

        s[aux] = r

def exchange_operator(s, depot, distances, demands, capacity):
    [r1, r2] = sample(s, 2)

    if len(r1) >= 1:
        [c] = sample(r1, 1)
        aux1 = r1.index(c)
        r1.remove(c)

        aux2 = s.index(r2)
        (can_attend, best_r) = bestly_attend_customer(r2, c, depot, distances, demands, capacity)

        if can_attend:
            s[aux2] = best_r
        else:
            r1.insert(aux1, c)

    elif len(r2) >= 1:
        [c] = sample(r2, 1)
        aux2 = r2.index(c)
        r2.remove(c)

        aux1 = s.index(r1)
        (can_attend, best_r) = bestly_attend_customer(r1, c, depot, distances, demands, capacity)

        if can_attend:
            s[aux1] = best_r
        else:
            r2.insert(aux2, c)

def solution_distance(s1, s2):
    total_dist = 0

    for r1 in s1:
        closest_dist = inf

        for r2 in s2:
            dist = len([i for i, j in zip(r1, r2) if i != j])

            if dist < closest_dist:
                closest_dist = dist

        total_dist += closest_dist

    return total_dist
