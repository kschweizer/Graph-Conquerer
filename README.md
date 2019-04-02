# Graph-Conquerer

Input graph-matrix examples in the `/inputs` directory

example input: 

    3 
    Kanto Johto Hoenn
    Johto
    1 6 x
    6 2 0.5
    x 0.5 3
    
In this instance, the first line passed in is the number of nodes:3, the second line is the list of node names, and the third line is the starting node: Johto. The lines afterward represent the graph matrix, where an "x" marks no edge between nodes A and B (represented as (A,B) or (B,A)). So, Johto has an edge between itself and Kanto of length 6 (value at x=2,y=1 and x=1,y=2 NOTE: always symmetrical). For the diagonal of the matrix, when x axis = y axis, the value in place is the cost of "conquering" that node, which will also add all the nodes with connections to the node to the list of nodes in our dominating set, BUT NOT CONQUER THEM!.


### Running the solver

Pass in input file and output directory to the function `solve_from_file` in `solver_template.py` or pass in an input directory and output directory to `solve_all` in `solver_template.py`. Use with Python3 recommended.
