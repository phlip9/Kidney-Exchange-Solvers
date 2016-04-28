# release to students
# get instanceSizes from result of instances_processor.py
# note to future: add validators for READMEs and general submission

import sys

instanceSizes = [499,51,500,500,500,35,18,200,498,500,480,500,200,500,500,500,10,100,500,500,500,10,500,
100,400,50,300,500,500,100,450,350,400,500,100,499,100,428,500,288,500,500,500,3,100,450,3,500,500,100,5,
498,100,500,496,500,500,200,99,5,10,500,30,500,455,10,500,500,100,9,100,499,200,200,500,50,500,308,499,
500,10,500,500,50,500,300,100,217,500,100,9,250,500,100,5,500,500,338,200,300,499,499,500,50,500,416,500,
160,6,181,169,350,30,60,500,500,300,500,100,35,500,450,44,200,500,500,499,500,140,500,500,100,500,400,500,
491,50,500,16,100,500,500,15,21,500,1,500,100,10,500,300,2,30,500,400,482,400,500,500,100,200,500,450,14,
500,261,250,100,100,500,100,300,100,500,500,100,500,58,500,500,499,500,500,58,10,500,50,400,26,365,500,
500,500,14,500,5,500,388,500,50,20,500,7,19,500,120,100,7,9,369,10,200,497,500,100,12,271,450,498,500,500,
120,500,100,30,500,500,50,191,100,10,5,464,500,500,421,500,500,100,6,500,50,10,500,497,500,10,483,500,337,
450,10,500,500,400,450,500,500,100,10,100,500,8,500,500,200,100,500,160,500,400,15,500,250,300,499,1,480,
500,500,500,500,200,500,10,498,50,490,96,100,500,500,421,8,500,150,400,500,500,20,200,500,100,500,12,200,
12,500,15,4,14,500,500,100,500,167,100,500,500,400,500,10,200,500,300,6,500,250,300,200,500,372,300,100,
12,300,9,500,20,88,500,500,500,500,500,473,230,6,100,500,426,496,400,500,207,471,500,150,250,100,100,500,
500,500,5,500,500,50,500,100,14,500,30,394,500,500,100,470,500,100,499,400,2,500,500,200,15,289,10,500,500,
500,500,200,500,296,500,500,400,499,4,381,500,400,75,473,150,500,500,2,300,500,500,500,500,465,11,500,100,
500,184,500,4,500,12,500,6,400,300,500,500,400,500,500,5,35,487,100,7,500,200,500,499,100,100,498,100,480,
500,500,350,500,100,500,500,500,100,500,500,50,500,500,500,100,500,500,182,100,300,500,3,500,500,200,200,
250,100,11,500,350,12,200,102,500,6,1,500,500,500,462,496,100]

def main(argv):
	if len(argv) != 1:
		print "Usage: python solutions_validator.py [path_to_input_file]"
		return
	allPassed = True
	lineIndex = 0
	with open(argv[0], "r") as f:
		for line in f:
			if lineIndex >= len(instanceSizes):
				print "Extra data at end of file"
				return
			result = processTest(line.strip('\n'), instanceSizes[lineIndex])
			if result != "solution ok":
				print "Error with test " + str(lineIndex + 1) + ": " + result
				allPassed = False
			lineIndex += 1
	if lineIndex < len(instanceSizes):
		print "File terminated early; missing lines"
		return
	if allPassed:
                print "all solution lines ok"

# line is a list of strings
def processTest(line, N):
	if line == "None":
		return "solution ok"
	cycles = line.split(';')
	used = [False for i in range(N)]
	for cycle in cycles:
		cycle = cycle.strip(' ').split(' ')
		for v in cycle:
			if not v.isdigit():
				return "Cycles must contain integers."
			vertex = int(v)
			if vertex < 0 or vertex >= N:
				return "Each integer must be between 1 and " + str(N) + ", inclusive."
			if used[vertex]:
				return "Each integer in the range 1 to " + str(N) + " must appear exactly once."
			used[vertex] = True
	return "solution ok"

if __name__ == '__main__':
	main(sys.argv[1:])
