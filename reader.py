# Author: Fernando Amaral Musso

def read_instance(path, filename):
    instance = filename.split('.')[0].split('-')

    n_nodes = int(instance[1][1:])
    k_vehicles = int(instance[2][1:])

    depot = 1
    customers = []
    coordinates = [0] * (n_nodes + 1)
    demands = [0] * (n_nodes + 1)
    capacity = 0

    f = open(path + '/' + filename, 'r')

    # Skips file header
    line = f.readline().strip()

    while line != 'NODE_COORD_SECTION':
        line = line.split(':')

        # Reads vehicles capacity
        if line[0].strip() == 'CAPACITY':
            capacity = int(line[1].strip())

        line = f.readline().strip()

    # Reads depot coordinates
    line = f.readline().strip()

    line = line.split();
    depot = int(line[0])
    coordinates[depot] = (float(line[1]), float(line[2]))

    # Reads customers coordinates
    line = f.readline().strip()

    while line != 'DEMAND_SECTION':
        line = line.split();
        customers.append(int(line[0]))
        coordinates[int(line[0])] = (float(line[1]), float(line[2]))
        line = f.readline().strip()

    # Skips depot demand
    line = f.readline()

    # Reads customers demands
    line = f.readline()

    while line != 'DEPOT_SECTION':
        line = line.split();
        demands[int(line[0])] = int(line[1])
        line = f.readline().strip()

    f.close()

    return depot, customers, coordinates, demands, k_vehicles, capacity
