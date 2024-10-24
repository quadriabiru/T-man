# TMAN: Tree-based Multi-Attribute Negotiation Algorithm

## Overview

TMAN (Tree-based Multi-Attribute Negotiation) is a conceptual framework designed for negotiation in multi-agent systems, allowing agents to discuss multiple attributes simultaneously. This implementation explores the algorithm's mechanics through visual representations and neighbor updates in a network of nodes, focusing on color attributes.

## Running Environment

- **OS**: MacOS
- **Language**: Python 3.11.1
- **Interpreter**: Python Interpreter
- **Required Libraries**: 
  - `numpy`
  - `matplotlib`

## Repository Contents

This repository contains a Python implementation of the TMAN algorithm, with two main topologies: **Ring** and **Spectacles**. The code simulates the negotiation process among nodes characterized by different colors (red, green, blue for Ring; black for Spectacles). The nodes exchange information about their neighbors and calculate distances based on color attributes, visualizing the results.

## Instructions

1. **Run `make`** (if applicable).
2. Execute the program using the command:
   ```bash
   python TMAN.py N k T
   ```
   - `N`: Total number of nodes.
   - `k`: Number of nearest neighbors to maintain for each node.
   - `T`: Topology type (`R` for Ring, `S` for Spectacles).

### Example Usage

```bash
python TMAN.py 30 3 R
```
This command initializes a Ring topology with 30 nodes, maintaining 3 nearest neighbors for each node.

## Detailed Functionality

1. **Node Creation**:
   - `createObjectsR(N)` and `createObjectsS(N)` generate nodes with specific color codes.
   
2. **Neighbor Records**:
   - Each node maintains a record of its neighbors, which is updated throughout the simulation. The `create_records` function initializes these records, while `update_records_R` and `update_records_S` manage the neighbor updates during negotiation cycles.

3. **Distance Calculation**:
   - The algorithm calculates the distance between nodes using CIE Lab color space, optimizing the selection of nearest neighbors based on their color attributes. Note that the definition of distance differs between the Spectacles and Ring topologies.

4. **Visualization**:
   - The results are visualized using Matplotlib, showing the nodes' arrangements and their connections through cycles of negotiation.

## Conclusion

This TMAN implementation serves as a conceptual exploration of negotiation among agents based on multi-attribute interactions. It illustrates how nodes can negotiate their relationships while considering their inherent attributes (in this case, color), providing a basis for further experimentation and study in multi-agent systems.

Feel free to explore the code, run simulations, and visualize the outcomes! If you have questions or need clarifications, don't hesitate to reach out.
