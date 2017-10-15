#!/usr/bin/python3

import unittest
import time
import random
import exact_cover as dlx

dlx.LOGLEVEL=2

class NQueen( dlx.ExactCover ):

	def __init__(self, n=4):
		super().__init__(secondary=n)
		self.n = n
		self.build_matrix()
		self.build_links()


	def solution_string(self, solution, solution_count=0 ):
		count = 0 
		if solution_count > 0: count = solution_count
		solution_str_array = ["\n-----  Solution {} ------\n".format(count) ]

		chessboard = [ ['_' for col in range(self.n) ] for row in range(self.n) ]
		for i in solution:
			if i is None: break
			nodes = [ self.matrix_col_to_grid( int(i.column.name) ), self.matrix_col_to_grid( int(i.right.column.name) ) ]
			
			rank, file = sorted( (int(i.column.name), int(i.right.column.name)))
			file %= self.n

			chessboard[rank][file] = "X"
				
			solution_str_array.append(  str( sorted(nodes, reverse=True) )  )

		#solution_str_array.append( ' '+'_ '*self.n+' ')
		solution_str_array.append('')
		for row in chessboard:
			solution_str_array.append(  ' '.join(row) )
		#solution_str_array.append('-'*(self.n*2+1))

		return '\n'.join( solution_str_array)
	

		
	def build_matrix(self): 

		# A matrix of all possible ways to place N queens on the board:
		# First N columns represent ranks
		# Next N columns represent files
		# Next 2N-1 columns represent up-diags
		# Last 2N-1 columns represent down-diags
		matrix = []

		for rank in range(self.n):
			for file in range(self.n):
				matrix_row = [0] * (6*self.n-2)
				matrix_row[rank]=1
				matrix_row[self.n + file] = 1
				matrix_row[2*self.n + (rank+file) ] = 1
				matrix_row[5*self.n - 2 + (file-rank)]= 1
				matrix.append( matrix_row )
		self.matrix = matrix

	def matrix_col_to_grid( self, c):
		prefix = ''
		if c < self.n:
			prefix = 'R'
		elif c < 2*self.n:	
			prefix = 'F'
			c -= self.n
		return '{}{}'.format(prefix,c)


class NQueenTest( unittest.TestCase):

	def test_four_queen(self):
		p = NQueen(4)
		self.assertEqual( p.solve(4), 2)

	def test_five_queen(self):
		p = NQueen(5)
		self.assertEqual( p.solve(5), 10)


	def test_six_queen(self):
		p = NQueen(6)
		self.assertEqual( p.solve(6), 4 )

	def test_seven_queen(self):
		p = NQueen(7)
		self.assertEqual( p.solve(7), 40)

	def test_eight_queen(self):
		p = NQueen(8)
		self.assertEqual( p.solve(8), 92)

	def test_nine_queen(self):
		p = NQueen(9)
		self.assertEqual( p.solve(9), 352)

if __name__ == '__main__':
	unittest.main()
