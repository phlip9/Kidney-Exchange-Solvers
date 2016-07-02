Kidney Exchange Solvers
---

### Problem Description

Currently, there are over 93,000 patients on the kidney transplant waiting list
waiting for deceased donors. Unfortunately, there are not enough deceased donors
to satisfy the needs of every patient. In many cases, patients have a
relative or friend who is willing to donate a kidney. However, the problem is
that the donor’s kidney might not compatible with the patient. All such
incompatible pairs will enter our new kidney exchange system, where the donor’s
kidney may be compatible with the patient in another pair.

We can formulate this problem as a graph `G = (V, E)` where the vertices are each
pair, `P` (patient and donor). Consider two such pairs `P1` and `P2`. A directed
edge exists from `P1` to `P2` if the donor from `P1` has a compatible kidney with
the patient from `P2`. Therefore, in order to carry out kidney transplants for
these patients, we need to find cycles in the system. However, all the
transplants must happen concurrently, so we limit each donation cycle to at most
5 pairs. As an additional constraint, we prioritize children over adults. Every
untreated adult costs us 1 point while every untreated child costs us 2 points.
Our goal is to find a set of donation cycles that minimizes the penaly of our
donation network.


### Algorithms

We present 4 different algorithms, each of which cover different areas of the problem
space. The primary motivation for the ensemble of algorithms is the wide range of
graph densities in our instance set; thus, our objective for each algorithm is to target a
specific subset of the problem space. We also take advantage of the highly optimized
mixed linear integer programming (MILP) library, Gurobi.

The first step in solving an instance is splitting the graph into its strongly connected
components, each of which can be solved independently. For instances with densities
below 25\%, we use a MILP which copies the graph `|V|` times and restricts
the `l^{th}` copy of the graph s.t. it contains only a single cycle beginning and ending at
the `l^{th}` vertex. We then enforce flow and cycle length constraints across every graph
copy. This solves most medium-low density graphs to optimality in tractable time. This
algorithm was inspired by the polynomial-sized Extended Edge model presented in Constantino
et al. (2013).

For graphs of less than 40% density, we find that the optimal (k<=3)-cycle allocation
achieves optimality in much less time than the previously described algorithm. Here, we exhaustively
enumerate every possible (k<=3)-cycle, formulate it as a MILP optimization, and enforce vertex
constraints.

For the highly dense graphs of greater than 40% density, we create two different algorithms.
The first is a (k=2)-cycle MILP which reinterprets the directed graph as an undirected
graph and then optimizes over the set of undirected edges (2-cycles). The second is a randomized,
greedy cycle finder inspired by the description presented in Abbassi et al. (2008)
that achieves better scores than the (k=2)-cycle cover on select instances.

### References

```
Gurobi Optimization, Inc.
    "Gurobi Optimizer",
    http://www.gurobi.com,
    2015.

Constantino, Miguel, et al.
    "New insights on integer-programming models for the kidney exchange problem."
    European Journal of Operational Research
    231.1 (2013): 57-68.

Abbassi, Zeinab, and Laks V. S. Lakshmanan.
    "Offline Matching Approximation Algorithms in Exchange Markets."
    Proceeding of the 17th International Conference on World Wide Web - WWW'08
    (2008): Web.
```
