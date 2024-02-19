import random
import numpy as np
import math
import matplotlib.pyplot as plt
import sys

# --- FUNCTIONS USED BY RING AND SPECTACLES ---
def shuffle(combined):
    keys = list(combined.keys())

    for i in range(random.randrange(2,10)):
        random.shuffle(keys)

    return keys

def create_records(nodes_list, N):
    records = {}
    for item in nodes_list:
        possible_choices = [v for v in nodes_list if v != item]
        other_items = random.sample(possible_choices, N)  # Select N random other items from the list
        records[item] = other_items  # Store the selected random other items for the current item
    return records

# --- FUNCTIONS USED ONLY BY RING ---
def createObjectsR(N): 
    combined = {}
    red, rCounter = {}, 0
    green, gCounter = {}, 0
    blue, bCounter = {}, 0

    while(rCounter < (N/3)): 
        id = 'r' + str(rCounter)
        code = [random.randrange(200,255), random.randrange(0,80), random.randrange(0,80)]
        red[id] = code
        rCounter += 1

    while(gCounter < (N/3)):
        id = 'g' + str(gCounter)
        code = [random.randrange(0,80), random.randrange(200,255), random.randrange(0,80)]
        green[id] = code
        gCounter += 1

    while(bCounter < (N/3)):
        id = 'b' + str(bCounter)
        code = [random.randrange(0,80), random.randrange(0,80), random.randrange(200,255)]
        blue[id] = code
        bCounter += 1
        pass

    return red, green, blue

def combine(red,green, blue):
    combined = {}

    combined.update(red)
    combined.update(green)
    combined.update(blue)

    return combined

def gamma_correction(color):
    color /= 255.0
    if color > 0.04045:
        color = ((color + 0.055) / 1.055) ** 2.4
    else:
        color = color / 12.92
    return color

def convert_rgb_to_xyz(sR, sG, sB):
    var_R = gamma_correction(sR)
    var_G = gamma_correction(sG)
    var_B = gamma_correction(sB)

    var_R *= 100
    var_G *= 100
    var_B *= 100

    X = var_R * 0.4124 + var_G * 0.3576 + var_B * 0.1805
    Y = var_R * 0.2126 + var_G * 0.7152 + var_B * 0.0722
    Z = var_R * 0.0193 + var_G * 0.1192 + var_B * 0.9505

    return X, Y, Z

def convert_xyz_to_lab(X, Y, Z):
    Reference_X = 94.811
    Reference_Y = 100.00
    Reference_Z = 107.304

    var_X = X / Reference_X
    var_Y = Y / Reference_Y
    var_Z = Z / Reference_Z

    if var_X > 0.008856:
        var_X = var_X ** (1/3)
    else:
        var_X = (var_X * 903.3) + (16 / 116)

    if var_Y > 0.008856:
        var_Y = var_Y ** (1/3)
    else:
        var_Y = (var_Y * 903.3) + (16 / 116)

    if var_Z > 0.008856:
        var_Z = var_Z ** (1/3)
    else:
        var_Z = (var_Z * 903.3) + (16 / 116)

    CIE_L = (116 * var_Y) - 16
    CIE_a = 500 * (var_X - var_Y)
    CIE_b = 200 * (var_Y - var_Z)

    return CIE_L, CIE_a, CIE_b

def calculate_delta(Ls, As, Bs, Lt, At, Bt):
    delta = math.sqrt((Lt - Ls)**2 + (At - As)**2 + (Bt - Bs)**2)
    return delta

def update_records_R(records, nodes_neighbor_dict,  x, y, shuffled, k):
    total_dist = []
    cycle = []

    total = 0

    for key in nodes_neighbor_dict.keys():
        item_pos = nodes_neighbor_dict[key]  # Position of item
        item_neighbors = list(set(records[key][:]))

        sum_distance_item = sum((nodes_neighbor_dict[x][0] - item_pos[0])**2 + (nodes_neighbor_dict[x][1] - item_pos[1])**2 for x in item_neighbors)
        
        total += sum_distance_item
        # Print for debugging purposes

    print(f"SUM OF DISTANCE => CYCLE 0: {total}")

    cycle.append(0)
    total_dist.append(total)
    
    for i in range(40):
        total = 0
        for item in records.keys():
            neighbor = random.choice(records[item])
            
            # Exchange neighbor lists
            tmp = records[neighbor][:]
            records[neighbor].append(item)
            records[neighbor].extend(records[item])
            records[item].extend(tmp)

            # Calculate nearest neighbors based on Lab color space distances
            item_neighbors = list(set(records[item][:]))
            neighbor_neighbors = list(set(records[neighbor][:]))
            
            item_lab = convert_xyz_to_lab(*convert_rgb_to_xyz(*nodes_neighbor_dict[item]))#[:3]
            neighbor_lab = convert_xyz_to_lab(*convert_rgb_to_xyz(*nodes_neighbor_dict[neighbor]))#[:3]

            # Remove item itself from its neighbor list
            if item in item_neighbors:
                item_neighbors.remove(item)
            if neighbor in neighbor_neighbors:
                neighbor_neighbors.remove(neighbor)

            nearest_neighbors_item = sorted(item_neighbors, key=lambda x: calculate_delta(*item_lab, *convert_xyz_to_lab(*convert_rgb_to_xyz(*nodes_neighbor_dict[x]))))[:k]
            nearest_neighbors_neighbor = sorted(neighbor_neighbors, key=lambda x: calculate_delta(*neighbor_lab, *convert_xyz_to_lab(*convert_rgb_to_xyz(*nodes_neighbor_dict[x]))))[:k]

            # Update records with k nearest neighbors
            records[item] = nearest_neighbors_item
            records[neighbor] = nearest_neighbors_neighbor
        
        # Only receiver updates
        '''for item in records.keys(): 
            neighbor = random.choice(records[item])
            
            # Exchange neighbor lists
            tmp = records[neighbor][:]
            records[neighbor].append(item)
            records[neighbor].extend(records[item])  # Neighbor maintains its own list
            
            # Calculate nearest neighbors based on Lab color space distances for the main node (item)
            item_neighbors = list(set(records[item][:]))
            
            item_lab = convert_xyz_to_lab(*convert_rgb_to_xyz(*nodes_neighbor_dict[item]))[:k]
            
            # Remove item itself from its neighbor list
            if item in item_neighbors:
                item_neighbors.remove(item)

            # Calculate nearest neighbors for the main node (item) based on CIE Lab distance
            nearest_neighbors_item = sorted(item_neighbors, key=lambda x: calculate_delta(*item_lab, *convert_xyz_to_lab(*convert_rgb_to_xyz(*nodes_neighbor_dict[x]))))[:k]

            # Update records with k nearest neighbors for the main node (item) only
            records[item] = nearest_neighbors_item'''

        for key in nodes_neighbor_dict.keys():
            item_pos = nodes_neighbor_dict[key]  # Position of item
            item_neighbors = list(set(records[key][:]))

            sum_distance_item = sum((nodes_neighbor_dict[x][0] - item_pos[0])**2 + (nodes_neighbor_dict[x][1] - item_pos[1])**2 for x in item_neighbors)
            
            total += sum_distance_item
        
        print(f"SUM OF DISTANCE => CYCLE {i+1}: {total}")

        if((i+1) == 1 or (i+1) == 5 or (i+1) == 10 or (i+1) == 15):
            plotNodes_R((i+1), x, y, shuffled, records) # create nodes image

            with open((docName + "_" + str(i+1) + ".txt"), 'w') as f:
                # Iterate over items in the dictionary
                for key, value in records.items():
                    # Write key and value to the file
                    f.write(f"{key}: {', '.join(value)}\n")
                  
        cycle.append(i+1)
        total_dist.append(total)
    
    with open((docName + "_distance_vs_cycles.txt"), 'w') as f:
        # Iterate over the cycles and distances simultaneously
        for c, d in zip(cycle, total_dist):
            # Write cycle and distance values side by side to the file
            f.write(f"SUM OF DISTANCE => CYCLE {c}: {d}\n")

    plt.figure(figsize=(10, 6))
    plt.plot(cycle, total_dist, marker='o', linestyle='-')
    plt.title('Sum of Distances Between Neighboring Nodes')
    plt.xlabel('Number of Cycles')
    plt.ylabel('Sum of Distances')
    plt.grid(True)
    plt.savefig(docName + "_distance_vs_cycles.png")
    plt.show(block=False)
    plt.close('all')
    
    return records

def placeNodes_R(N):
    # Generate angles for placing nodes in a circle
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
    
    # Set the radius of the circle
    radius = 10
    
    # Place nodes in a circle
    x = radius * np.cos(angles)
    y = radius * np.sin(angles)
    
    return x, y

def plotNodes_R(cycle, x, y, lst, records):
    plt.figure(figsize=(10, 10))
    
    c_list = []

    for node in records.keys():
        if(node[0] == 'r'):
            c_list.append('red')
        elif(node[0] == 'g'):
            c_list.append('green')
        else:
            c_list.append('blue')

    for i in range(len(records)):
        plt.scatter(x[i], y[i], color=c_list[i], zorder=10)  # Plot nodes
        plt.text(x[i], y[i], lst[i], ha='center', va='center', fontsize=8)

    # Plot edges between nodes
    for node, neighbors in records.items():
        node_x, node_y = x[lst.index(node)], y[lst.index(node)]

        for neighbor in neighbors:
            neighbor_x, neighbor_y = x[lst.index(neighbor)], y[lst.index(neighbor)]
            plt.plot([node_x, neighbor_x], [node_y, neighbor_y], color='black', alpha=0.5)

    plt.title('Graph of Nodes and Connections Cycle ' + str(cycle))
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig(docName + "_" + str(cycle) + ".png")
    plt.show(block=False)
    plt.close('all')

# --- FUNCTIONS USED ONLY BY SPECTACLES ---
def createObjectsS(N): 
    black = {}
    for i in range(N):
        id = 'k' + str(i)  # Using 'k' to represent black nodes
        code = [0, 0, 0]  # Black color code
        black[id] = code

    return black

def update_records_S(records, nodes_neighbor_dict, k):
    total_dist = []
    cycle = []

    total = 0

    for key in nodes_neighbor_dict.keys():
        item_pos = nodes_neighbor_dict[key]  # Position of item
        item_neighbors = list(set(records[key][:]))

        sum_distance_item = sum((nodes_neighbor_dict[x][0] - item_pos[0])**2 + (nodes_neighbor_dict[x][1] - item_pos[1])**2 for x in item_neighbors)
        
        total += sum_distance_item
    
    print(f"SUM OF DISTANCE => CYCLE 0: {total}")

    cycle.append(0)
    total_dist.append(total)

    for i in range(40):
        total = 0
        #print(f"\n\CYCLE {i+1}")
        for item in records.keys():
            neighbor = random.choice(records[item])
            
            # Exchange neighbor lists
            tmp = records[neighbor][:]
            records[neighbor].append(item)
            records[neighbor].extend(records[item])
            records[item].extend(tmp)

            # Calculate nearest neighbors based on Euclidean distances
            item_neighbors = list(set(records[item][:]))
            neighbor_neighbors = list(set(records[neighbor][:]))
            
            item_pos = nodes_neighbor_dict[item]  # Position of item
            neighbor_pos = nodes_neighbor_dict[neighbor]  # Position of neighbor
            
            # Calculate squared Euclidean distance between item and its neighbors
            nearest_neighbors_item = sorted(item_neighbors, key=lambda x: (nodes_neighbor_dict[x][0] - item_pos[0])**2 + (nodes_neighbor_dict[x][1] - item_pos[1])**2)[:k]
            
            # Calculate squared Euclidean distance between neighbor and its neighbors
            nearest_neighbors_neighbor = sorted(neighbor_neighbors, key=lambda x: (nodes_neighbor_dict[x][0] - neighbor_pos[0])**2 + (nodes_neighbor_dict[x][1] - neighbor_pos[1])**2)[:k]
                                                     
            # Update records with k nearest neighbors
            records[item] = nearest_neighbors_item
            records[neighbor] = nearest_neighbors_neighbor

        for key in nodes_neighbor_dict.keys():
            item_pos = nodes_neighbor_dict[key]  # Position of item
            item_neighbors = list(set(records[key][:]))

            sum_distance_item = sum((nodes_neighbor_dict[x][0] - item_pos[0])**2 + (nodes_neighbor_dict[x][1] - item_pos[1])**2 for x in item_neighbors)
            
            total += sum_distance_item
            # Print for debugging purposes
        
        print(f"SUM OF DISTANCE => CYCLE {i+1}: {total}")

        cycle.append(i+1)
        total_dist.append(total)

        if((i+1) == 1 or (i+1) == 5 or (i+1) == 10 or (i+1) == 15):
            plotNodes_S((i+1), nodes, records) # create nodes image

            with open((docName + "_" + str(i+1) + ".txt"), 'w') as f:
                # Iterate over items in the dictionary
                for key, value in records.items():
                    # Write key and value to the file
                    f.write(f"{key}: {', '.join(value)}\n")

    with open((docName + "_distance_vs_cycles.txt"), 'w') as f:
        # Iterate over the cycles and distances simultaneously
        for c, d in zip(cycle, total_dist):
            # Write cycle and distance values side by side to the file
            f.write(f"SUM OF DISTANCE => CYCLE {c}: {d}\n")

    plt.figure(figsize=(10, 6))
    plt.plot(cycle, total_dist, marker='o', linestyle='-')
    plt.title('Sum of Distances Between Neighboring Nodes')
    plt.xlabel('Number of Cycles')
    plt.ylabel('Sum of Distances')
    plt.grid(True)
    plt.savefig(docName + "_distance_vs_cycles.png")
    plt.show(block=False)
    plt.close('all')

    return records

def placeNodes_S(N):
    # Number of nodes on each circle
    N_circle = N // 3  # Assuming N is even
    
    # Radius of the circles
    radius_circle = 1
    
    # X and Y coordinates for nodes on the first circle
    angle_circle1 = np.linspace(0, 2 * np.pi, N_circle, endpoint=False)
    x_circle1 = radius_circle * np.cos(angle_circle1) - 2
    y_circle1 = radius_circle * np.sin(angle_circle1)
    
    # X and Y coordinates for nodes on the second circle
    angle_circle2 = np.linspace(0, 2 * np.pi, N_circle, endpoint=False)
    x_circle2 = radius_circle * np.cos(angle_circle2) + 2
    y_circle2 = radius_circle * np.sin(angle_circle2)
    
    # X and Y coordinates for nodes on the semicircle
    angle_semicircle = np.linspace(0, np.pi, N - 2 * N_circle, endpoint=False)
    x_semicircle = np.cos(angle_semicircle)
    y_semicircle = np.sin(angle_semicircle)
    
    # Concatenate the coordinates
    x = np.concatenate((x_circle1, x_semicircle, x_circle2))
    y = np.concatenate((y_circle1, y_semicircle, y_circle2))
    
    # Combine with black nodes
    black = createObjectsS(N)
    combined = {**black, **{f"k{i}": [x[i], y[i]] for i in range(N)}}
    
    return x, y, combined

def plotNodes_S(cycle, lst, records):
    plt.figure(figsize=(10, 10))
    
    for nodes in lst.keys():
        plt.scatter(lst[nodes][0], lst[nodes][1], color='black', zorder=10)  # Plot nodes
        #plt.text(x[i], y[i], lst[i], ha='center', va='center', fontsize=8)

    # Plot edges between nodes
    for node, neighbors in records.items():
        node_x, node_y = lst[node][0], lst[node][1]

        for neighbor in neighbors[0:3]: # Ask about this
            neighbor_x, neighbor_y = lst[neighbor][0], lst[neighbor][1]
            plt.plot([node_x, neighbor_x], [node_y, neighbor_y], color='black', alpha=0.5)

    plt.title('Graph of Nodes and Connections Cycle ' + str(cycle))
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig(docName + "_" + str(cycle) + ".png")
    plt.show(block=False)
    plt.close('all')

# --- START MAIN ---
if __name__ == "__main__":
    if (len(sys.argv) != 4): 
        print(f"Invalid number of arguments ({len(sys.argv)-1}) provided\nUSEAGE: python/python3 TMAN.py N k T where T = S or R\n")
        sys.exit(1)

    else: 
        N = int(sys.argv[1])
        k = int(sys.argv[2])
        topology = sys.argv[3]

        if topology == "R":
            docName = topology + "_N" + str(N) + "_k" + str(k)

            redNodes, greenNodes, blueNodes = createObjectsR(N)

            combined = combine(redNodes,greenNodes,blueNodes)

            shuffled = shuffle(combined)

            records = create_records(shuffled, k) # first round, node and neighbors list instantiated

            x, y = placeNodes_R(len(records)) # xy co-ordinates for shapes

            records = update_records_R(records, combined, x, y, shuffled, k) # records dict with nodes and neighbors => need to save this to csv => do they both reshuffle

        elif topology == "S":
            docName = topology + "_N" + str(N) + "_k" + str(k)

            x, y, nodes = placeNodes_S(N) # xy co-ordinates for shapes

            shuffled = shuffle(nodes)

            records = create_records(shuffled, k) # first round, node and neighbors list instantiated

            records = update_records_S(records, nodes, k) # records dict with nodes and neighbors => need to save this to csv => do they both reshuffle

        else: 
            print(f"Invalid toplogy option{sys.argv[3]}\nT must be S or R\n")
            sys.exit(1)