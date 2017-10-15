#!/usr/bin/python3

import unittest


""" N-Queen solution, from Dijkstra """

def print_solution( qc, n ):

	for row in range(n):
		row_string_array = [ '' for col in range(n) ]
		for col in range(n):
			if qc[row] == col:
				row_string_array[col]='X'
			else:
				row_string_array[col]='_'
		print( 	' '.join( row_string_array ))


def eight_queen():
	""" As written by Dijkstra in A Short Introduction to the Art of Programming, chapter 9, 1971.
	
	Only modification: N, the current number of queens on the board, is passed as a parameter to the recursive
	function """

	# initialize empty board
	queen_columns = [ 0 ] * 8
	free_columns = [ True ] * 8
	free_up_diag = [ True ] * 15
	free_down_diag = [ True ] * 15
	solution_count = 0

	def generate(n):
		nonlocal solution_count
		# base case: the board is full -> print the configuration
		if n == 8:
			solution_count += 1
			print("\n--- Solution {} ---\n".format( solution_count) )
			print_solution( queen_columns )
			return
		for h in range( 8 ):

			# check that the position (n,h) is free
			if free_columns[h] and free_up_diag[ n+h ] and free_down_diag[ h-n + 7 ]:
				# set queen on square H
				queen_columns[ n ] = h
				free_columns[ h ] = False
				free_up_diag[ n+h ] = False
				free_down_diag[ h-n + 7 ] = False

				# add 1 more queen
				generate(n+1)

				# backtracking: remove queen from square H
				free_columns[ h ] = True
				free_up_diag[ n+h ] = True
				free_down_diag[ h-n + 7 ] = True

	# top recursive call
	generate(0)

	return solution_count

def n_queen(n):
	""" An easy generalization to N queens
	
	:param n: the number of queens, as well as the board size (NxN)
	:type n: int
	:return: the number of (non-fundamental) solutions
	:rtype: int
	"""

	# initialize empty board
	queen_columns = [ 0 ] * n
	free_columns = [ True ] * n
	free_up_diag = [ True ] * (n*2-1)
	free_down_diag = [ True ] * (n*2-1)
	solution_count = 0

	def generate(q):
		nonlocal solution_count
		# base case: the board is full -> print the configuration
		if q == n:
			solution_count += 1
			print("\n--- Solution {} ---\n".format( solution_count) )
			print_solution( queen_columns, n )
			return
		for h in range( n ):

			# check that the position (n,h) is free
			if free_columns[h] and free_up_diag[ q+h ] and free_down_diag[ h-q + n - 1 ]:
				# set queen on square H
				queen_columns[ q ] = h
				free_columns[ h ] = False
				free_up_diag[ q+h ] = False
				free_down_diag[ h-q + n - 1 ] = False

				# add 1 more queen
				generate(q+1)

				# remove queen from square H
				free_columns[ h ] = True
				free_up_diag[ q+h ] = True
				free_down_diag[ h-q + n -1 ] = True

	generate(0)

	return solution_count

class NQueenTest( unittest.TestCase):


	def test_four_queen(self):
		self.assertEqual( n_queen(4), 2)

	def test_five_queen(self):
		self.assertEqual( n_queen(5), 10)

	def test_six_queen(self):
		self.assertEqual( n_queen(6), 4 )

	def test_seven_queen(self):
		self.assertEqual( n_queen(7), 40)

	def test_eight_queen(self):
		self.assertEqual( n_queen(8), 92)

	def test_nine_queen(self):
		self.assertEqual( n_queen(9), 352)

if __name__ == '__main__':
	unittest.main()





