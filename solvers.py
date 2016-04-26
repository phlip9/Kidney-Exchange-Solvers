import numpy as np
from instance_gen import serialize

from gurobipy import Model, GRB, tuplelist, LinExpr

def read(filename):
    with open(filename, 'r') as f:
        lines = [[int(x) for x in line.split()] for line in f]
        C = set(lines[1])
        A = np.array(lines[2:])
        return A, C

def constantino(A, C, k):
    """
    Polynomial-sized CCMcP Edge-Extended Model
    See Constantino et al. (2013)
    """
    _ = '*'
    m = Model()
    m.modelsense = GRB.MAXIMIZE

    n = A.shape[0]
    vars = {}
    edges = tuplelist()

    # Variables
    for l in range(n):
        for i in range(n):
            for j in range(n):
                if A[i, j] == 1:
                    e = (l, i, j)
                    edges.append(e)
                    w = 2 if j in C else 1
                    var = m.addVar(vtype=GRB.BINARY, obj=w, name='x^%d_{%d,%d}' % e)
                    vars[e] = var

    m.update()

    # Constraint (2), (5), (6): Flow in = Flow out and symmetry reducers
    for l in range(n):
        for i in range(n):
            lhs_vars = [vars[e] for e in edges.select(l, _, i)]
            ones = [1.0]*len(lhs_vars)
            lhs = LinExpr()
            lhs.addTerms(ones, lhs_vars)

            rhs_vars = [vars[e] for e in edges.select(l, i, _)]
            ones = [1.0]*len(rhs_vars)
            rhs = LinExpr()
            rhs.addTerms(ones, rhs_vars)

            m.addConstr(lhs == rhs)

            if i < l:
                m.addConstr(lhs == 0)
            elif i > l:
                rhs2_vars = [vars[e] for e in edges.select(l, l, _)]
                ones = [1.0]*len(rhs2_vars)
                rhs2 = LinExpr()
                rhs2.addTerms(ones, rhs2_vars)

                m.addConstr(lhs <= rhs2)

    # Constraint (3): Use a vertex only once
    for i in range(n):
        c_vars = [vars[e] for e in edges.select(_, i, _)]
        ones = [1.0]*len(c_vars)
        expr = LinExpr()
        expr.addTerms(ones, c_vars)
        m.addConstr(expr <= 1)

    # Constraint (4): Limit cardinality of cycles to k
    for l in range(n):
        c_vars = [vars[e] for e in edges.select(l, _, _)]
        ones = [1.0]*len(c_vars)
        expr = LinExpr()
        expr.addTerms(ones, c_vars)
        m.addConstr(expr <= k)

    m.optimize()
    m.update()

    cycles = []
    for l in range(n):
        cycle = []
        c_edges = [e for e in edges.select(l, _, _)]
        c_vars = [vars[e] for e in c_edges]
        c_edges = [e for e in edges.select(l, _, _) if vars[e].x == 1.0]
        n_edges = len(c_edges)
        if n_edges != 0:
            e = c_edges[0]
            cycle.append(e[1])
            for i in range(1, n_edges):
                j = e[2]
                for p in range(n_edges):
                    e = c_edges[p]
                    if e[1] == j:
                        cycle.append(e[1])
                        break
            cycles.append(cycle)

    return cycles, m.objval

def test():
    m = Model("mip1")

    x = m.addVar(vtype=GRB.BINARY, name='x')
    y = m.addVar(vtype=GRB.BINARY, name='y')
    z = m.addVar(vtype=GRB.BINARY, name='z')

    m.update()

    m.setObjective(x + y + 2 * z, GRB.MAXIMIZE)

    m.addConstr(x + 2 * y + 3 * z <= 4, 'c0')
    m.addConstr(x + y >= 1, 'c1')

    m.optimize()

    print('x =', x.x)
    print('y =', y.x)
    print('z =', z.x)
    print('objective =', m.objval)

# test()
# print(serialize(*read('MILP_LOVERS2.in')), end='')

A, C = read('MILP_LOVERS3.in')
cycles, objval = constantino(A, C, 5)
print('cycles =', cycles)
print('objval =', objval)
