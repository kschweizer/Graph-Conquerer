# Graph-Conquerer

### The problem:

Given a graph of nodes and undirected edges, as well as a starting node, we would like to "rule" over every node in the graph by deciding which nodes to "conquer". Conquering a node adds the node to our list of nodes that we rule, as well as all its adjacent nodes connected by an edge. Every node has an associated cost to conquer it, and any movement between nodes has an associated traveling cost. Our goal is thus to find the cheapest way to traverse the graph and conquer nodes such that every node is under our rule. 

IMPORTANT NOTE: Our traversal of the graph must always start and end at the starting node, à la Traveling Salesman Problem.

### Inputs 

Input graph-matrix examples in the `/inputs` directory

Inputs must have the file extension `.in` and be passed with the convention described below.

example input: 

    3 
    Kanto Johto Hoenn
    Johto
    1 6 x
    6 2 0.5
    x 0.5 3
    
In this instance, the first line passed in is the number of nodes:3, the second line is the list of node names, and the third line is the starting node: Johto. The lines afterward represent the graph matrix, where an "x" marks no edge between nodes A and B (represented as (A,B) or (B,A)). So, Johto has an edge between itself and Kanto of length 6 (value at x=2,y=1 and x=1,y=2 NOTE: always symmetrical). For the diagonal of the matrix, when x axis = y axis, the value in place is the cost of "conquering" that node, which will also add all the nodes with connections to the node to the list of nodes in our dominating set, BUT NOT CONQUER THEM!.


### Running the solver

To run on a single file:

`python solver.py <input_file_name> <output_directory>`

To run on all input files:

`python solver.py --all <input_directory> <output_directory>`

### Reading outputs

Outputs are structed in 2 lines:

- Line 1 is the walk constructed by the solver, starting from the start node and ending at the start node

- Line 2 is the list of nodes we decide to conquer
