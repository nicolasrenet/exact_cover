#!/usr/bin/python3

import sys

matrix = eval( sys.argv[1] )

count = 6

rows = len(matrix)
cols = len(matrix[0])

if len(sys.argv)>2: 
	count = int( sys.argv[2] )

for mtx in range(0,count):

	print('\\begin{minipage}{.5\\linewidth}')
	print('$\\kbordermatrix{')
	print('    ',end='')
	for c in range(0,cols):
		print('& c_{} '.format(c+1),end='')
	print('\\\\')
	for r in range(0,rows):
		print('r_{} '.format(r+1), end='')
		print('& \\tikzmark{{m{}{}1}} {} '.format(mtx+1, r+1, matrix[r][0]), end='')
		for col in range(1, cols-1):
			if r==0 or r==rows-1:
				print('& \\tikzmark{{m{}{}{}}} {} '.format(mtx+1,r+1, col+1, matrix[r][col]), end='')
			else:
				print('& {} '.format(matrix[r][col]), end='')
		print('& \\tikzmark{{m{}{}{}}} {} '.format(mtx+1, r+1, cols, matrix[r][cols-1]), end='')
		if r<rows-1:
			print('\\\\')
		else:
			print('')
				
	print('}$')
	print('\\end{minipage}')
	print('\\begin{minipage}{.4\\linewidth}')
	print('\\end{minipage}')
	print('\n\\vspace{1em}\n')
