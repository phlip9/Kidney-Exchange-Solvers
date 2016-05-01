from statistics import *
from solvers import solve_file

fileName = "/Users/Anthony/Downloads/phase1-processed/%d.in"  # TODO CHANGE THIS

def stats():
    vertices = []
    for i in range(1, 493):
        fileH = open(fileName % i)
        count = fileH.readline()
        count.replace("\n", "")
        num = int(count)
        vertices.append(num)

    print("Mean: %d" % mean(vertices))
    print("median: %d" % median(vertices))
    print("stdev: %d" % pstdev(vertices))
    print("max: %d" % max(vertices))
    print("num under 200: %d" % len([x for x in vertices if x <= 250]))


def easy_run():
    for i in range(1, 493):
        this = fileName % i
        shouldRun = False
        with open(this) as fileH:
            fileH = open(fileName % i)
            count = fileH.readline()
            count.replace("\n", "")
            num = int(count)
            if num <= 100:
                shouldRun = True
        if shouldRun:
            print(i)
            print(solve_file(this, 5))

easy_run()
