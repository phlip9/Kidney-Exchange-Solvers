import numpy as np
from scipy.sparse.csgraph import connected_components as connected_components_
from scipy.sparse import rand
import random
from sys import argv

connected_components = lambda A: connected_components_(A, directed=True, connection='strong', return_labels=True)

def serialize(A, children=[]):
    N, _ = A.shape
    res = ''
    res += str(N) + '\n'
    res += ' '.join(map(str, children)) + '\n'
    for i in range(N):
        r = A[i, :]
        res += ' '.join(map(str, r)) + '\n'
    return res

def random_graph(n, rho):
    R = rand(n, n, density=rho, format='dense')
    R_I = np.ceil(R).astype(int)
    A = np.array(R_I)
    for i in range(n):
        A[i, i] = 0
    return A

def random_children(n, P=0.5):
    C = []
    for i in range(n):
        if random.random() < P:
            C.append(i)
    return C

def seed(n):
    random.seed(n)
    np.random.seed(n)

def shuffle(A):
    n = A.shape[0]
    mapping = np.array(range(n))
    np.random.shuffle(mapping)
    return A[mapping, ...][..., mapping]

def density(A):
    n = A.shape[0]
    edges = np.sum(A)
    return edges / (n*n - n)

def join(A1, A2):
    Z1 = np.zeros((A1.shape[0], A2.shape[1]), dtype=int)
    Z2 = np.zeros((A2.shape[0], A1.shape[1]), dtype=int)
    B1 = np.hstack((A1, Z1))
    B2 = np.hstack((Z2, A2))
    B = np.vstack((B1, B2))
    return B

def weak_connect(A1, A2, rho):
    R1 = rand(A1.shape[0], A2.shape[1], density=rho, format='dense')
    R1 = np.ceil(R1).astype(int)
    R1 = np.array(R1)
    Z2 = np.zeros((A2.shape[0], A1.shape[1]), dtype=int)
    B1 = np.hstack((A1, R1))
    B2 = np.hstack((Z2, A2))
    B = np.vstack((B1, B2))
    return B

def anderson_circle(n):
    v_0 = np.zeros((1, n), dtype=int)
    off = 1
    while off < n:
        v_0[0, off] = 1
        off += 6
    A = v_0
    for i in range(1, n):
        v_i = np.roll(v_0, i)
        A = np.vstack((A, v_i))
    return A

def check_anderson(n):
    A = anderson_circle(n)
    I = np.eye(n, n)
    A_i = A

    for k in range(1, 6):
        A_i = A_i.dot(A)
        print('---')
        print('k = %d' % k)
        print(np.diag(A_i))

def check_small():
    A = np.array([
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [1, 1, 0, 0],
    ])
    I = np.eye(4)

    print(A)
    print(A.dot(A))
    print(A.dot(A).dot(A))
    print(A.dot(A).dot(A).dot(A))
    print(A.dot(A).dot(A).dot(A).dot(A))

def prune_noncycle_nodes(A, k):
    N, _ = A.shape
    mask = np.zeros(N, dtype=bool)
    A_i = A
    for i in range(1, k):
        A_i = A_i.dot(A)
        for j in range(N):
            if A_i[j, j] != 0:
                mask[j] = True

    print('sum(mask) =', sum(np.ones(N) - mask.astype(int)))

    if not all(mask):
        A = A[mask, ...]
        A = A[..., mask]
        return A
    else:
        return A

def instance_1():
    seed(0xC5170)
    A1 = random_graph(300, 0.7)
    A2 = anderson_circle(199)
    A = weak_connect(A1, A2, 0.5)
    A = shuffle(A)
    C = random_children(499, 0.5)
    return A, C

def instance_2():
    seed(0xDAE33C5)
    A = random_graph(500, 0.4)
    C = random_children(500, 0.5)
    return A, C

def instance_3():
    seed(0x1337)
    A1 = random_graph(125, 0.8)
    A2 = random_graph(125, 0.8)
    A3 = random_graph(125, 0.8)
    A4 = random_graph(125, 0.8)
    A12 = weak_connect(A1, A2, 0.8)
    A123 = weak_connect(A12, A3, 0.8)
    A1234 = weak_connect(A123, A4, 0.8)
    A = shuffle(A1234)
    C = random_children(500, 0.5)
    return A, C

if __name__ == '__main__':
    if len(argv) > 1 and argv[1] in ['1', '2', '3']:
        if argv[1] == '1':
            A, C = instance_1()
        elif argv[1] == '2':
            A, C = instance_2()
        elif argv[1] == '3':
            A, C = instance_3()
        # print('density of instance', argv[1], '=', density(A))
        print(serialize(A, C), end='')
        # print(connected_components(A))
