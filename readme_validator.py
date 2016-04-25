# Released to students: validator for README

import sys

def main(argv):
    if len(argv) == 1:
        print(processReadMe(argv[0]))
    elif len(argv) == 0:
        print(processReadMe())
    else:
        print("Usage Error: python readme_validator.py [*optional* path_to_readme]")

def processReadMe(path="README"):    
    try:
        fin = open("README", "r")
    except FileNotFoundError:
        return "README not found."

    line = fin.readline().strip()
    if len(line) <= 1:
        return "You must have a team name."

    i = 0
    while True:
        line = fin.readline().split()
        if len(line) == 0 or len(line[0]) == 0:
            break;

        sid = line[0]
        if i >= 4:
            return "You have too many students on your team."
        if len(sid) > 8 or len(sid) <= 0 or not sid.isdigit():
            return "The {0}-th ID is invalid".format(i)
        i += 1;

    return "instance ok"

if __name__ == '__main__':
    main(sys.argv[1:])
