import random

ROWS=7
COLS=7
matrix = [ [ 0 for c in range(0, COLS) ] for r in range(0,ROWS) ] 
for r in range(0,ROWS):
	for c in range(0,COLS):
		matrix[r][c] = random.choice( (0,1,0,0,0) )
print(matrix)
