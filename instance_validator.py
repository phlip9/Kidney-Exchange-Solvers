# Released to students

import sys

def main(argv):
    if len(argv) != 1:
        print("Usage: python instance_validator.py [path_to_input_file]")
        return
    print(processInput(argv[0]))

def processInput(s):
    fin = open(s, "r")
    line = fin.readline().split()
    if len(line) != 1 or not line[0].isdigit():
        return "Line 1 must contain a single integer."
    N = int(line[0])
    if N < 1 or N > 500:
        return "N must be an integer between 1 and 500, inclusive."

    line = fin.readline().split()
    if len(line) > N:
        return "There cannot be more than N children vertices."

    children = []
    for child in line:
        if not child.isdigit():
            return "The line of children must contain integers"
        child = int(child)
        if child < 0 or child >= N:
            return "Each child index must be between 0 and N-1"
        children.append(child)

    d = [[0 for j in range(N)] for i in range(N)]
    for i in range(N):
        line = fin.readline().split()
        if len(line) != N:
            return "Line " + str(i+2) + " must contain N integers."
        for j in range(N):
            if not line[j].isdigit():
                return "Line " + str(i+2) + " must contain N integers."
            d[i][j] = int(line[j])
            if d[i][j] < 0 or d[i][j] > 1:
                return "The adjacency matrix must be comprised of 0s and 1s."
    for i in range(N):
        if d[i][i] != 0:
            return "A node cannot have an edge to itself."
    return "instance ok"

if __name__ == '__main__':
    main(sys.argv[1:])
