# Author: Fernando Amaral Musso

from reader import read_instance
from cs import simulated_annealing_clustering_search
from statistics import mean, stdev
from timeit import default_timer
from math import sqrt
from os import walk

################################################################################

def euclidean_distance(v1, v2):
    (x1, y1) = v1
    (x2, y2) = v2

    return sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))

def calculate_distances(coordinates):
    distances = []
    distances.append([0] * len(coordinates))

    for i in range(1, len(coordinates)):
        line = [0] * len(coordinates)

        for j in range(1, len(coordinates)):
            if i != j:
                line[j] = euclidean_distance(coordinates[i], coordinates[j])

        distances.append(line)

    return distances

################################################################################

sa_to = 100
sa_tf = 0.001
sa_alpha = 0.995
sa_max_iter = 1000
sa_max_bad_iter = 500
cs_n_clusters = 10
cs_lambda = 7

dirs = ['Instances/A', 'Instances/B', 'Instances/F']

for d in dirs:
    csv = open('Results/' + d.split('/')[1] + '_results.csv', 'w+')
    csv.write('instance,average_s,best_s,worst_s,deviation_s,average_time\n')

    f = []
    for (_, _, filenames) in walk(d):
        f = f + filenames

    for name in f:
        times = []
        solutions = []

        for _ in range(5):
            depot, customers, coordinates, demands, k_vehicles, capacity = read_instance(d, name)
            distances = calculate_distances(coordinates)

            start_time = default_timer()
            _, s = simulated_annealing_clustering_search(sa_to, sa_tf, sa_alpha, sa_max_iter, sa_max_bad_iter, cs_n_clusters, cs_lambda, depot, customers, distances, demands, k_vehicles, capacity)
            end_time = default_timer()
            execution_time = end_time - start_time

            print(name + ' finished')

            times.append(execution_time)
            solutions.append(s)

        average_s = mean(solutions)
        best_s = min(solutions)
        worst_s = max(solutions)
        deviation_s = stdev(solutions)
        average_time = mean(times)

        print(name, average_s, best_s, worst_s, deviation_s, average_time, sep=',', file=csv)

    csv.close()
