#!/usr/bin/python3

import unittest


""" 
	Classic, recursive implementation of N-Queen solution, from `E. W. Dijkstra <file://../E.W.Dijkstra Archive_ A Short Introduction to the Art of Programming (EWD 316), Chapter 9.html>`_.
"""

def print_solution( qc ):
	""" 
	Print a solution chessboard on the console.
	For example, given the first solution for the 4-Queen problem :math:`[1,3,0,2]`, the function prints the chessboard configuration that follows::

		X _ _ _
		_ _ _ X
		X _ _ _
		_ _ X _


	:param qc: a vector of column indices, whose first element is the queen position  in the first row, the second element is the queen position in the second row, and so on.
	:type qc: list
	"""
	n = len(qc)
	for row in range(n):
		row_string_array = [ '' for col in range(n) ]
		for col in range(n):
			if qc[row] == col:
				row_string_array[col]='X'
			else:
				row_string_array[col]='_'
		print( 	' '.join( row_string_array ))
 
def encode_solution(qc):
	""" 
	.. _encode_solution:

	Encode a solution as a radix-10 integer. For example, the solution :math:`[0,4,7,5,2,6,1,3]` in which rows 0 through 7 have queens in columns 0, 4, 7, 5, 2, 6, 1, and 3 respectively, is encoded  as integer :math:`4,752,613`.

	:param qc: a vector a column indices, where each each index is the position of the queen for the corresponding row.
	:type qc: list
	:return: a radix-10 representation of the vector of indices.
	:rtype: int
	"""
	solution_code = 0
	for col in qc:
		solution_code = solution_code * 10 + col
	return solution_code

def eight_queen():
	""" As written by Dijkstra in *A Short Introduction to the Art of Programming*, chapter 9, 1971.
	
	Only modification: N, the current number of queens on the board, is passed as a parameter to the recursive
	function.
	
	:return: a list of solution codes, where each vector of column numbers is encoded as an integer (call the encode_solution_ procedure).
	:rtype: int
	"""

	# initialize empty board
	queen_columns = [ 0 ] * 8
	free_columns = [ True ] * 8
	free_up_diag = [ True ] * 15
	free_down_diag = [ True ] * 15

	solutions = []

	def generate(n):
		# base case: the board is full -> print the configuration
		if n == 8:
			solutions.append( encode_solution( queen_columns ))
			#print("\n--- Solution {} ---\n".format( len(solutions)) )
			#print_solution( queen_columns )
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

	return solutions

def n_queen(n):
	""" An easy generalization to N queens.
	
	:param n: the number of queens, as well as the board size (:math:`n\\times n`)
	:type n: int
	:return: a list of solution codes, where each vector of column numbers is encoded as an integer (call the encode_solution_ procedure).
	
	:rtype: int
	"""

	# initialize empty board
	queen_columns = [ 0 ] * n
	free_columns = [ True ] * n
	free_up_diag = [ True ] * (n*2-1)
	free_down_diag = [ True ] * (n*2-1)
	solutions = []

	def generate(q):
		# base case: the board is full -> print the configuration
		if q == n:
			solutions.append( encode_solution( queen_columns ))
			#print("\n--- Solution {} ---\n".format( len(solutions)) )
			#print_solution( queen_columns )
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

	return solutions

class NQueenTest( unittest.TestCase):

	seven_queen_solutions = [	246135, 362514, 415263, 531642, 1306425, 1350246, 1403625, 1420635, 1463025, 1526304, 
					1642053, 2051463, 2053164, 2461350, 2514036, 2613504, 2630415, 3025164, 3041526, 3164205,
					3502461, 3625140, 3641502, 4036251, 4053162, 4152630, 4205316, 4613502, 4615203, 5024613,
					5140362, 5203641, 5246031, 5263041, 5316420, 5360241, 6135024, 6251403, 6304152, 6420531]

	eight_queen_solutions = [	4752613, 5726314, 6357142, 6471352, 13572064, 14602753, 14630752, 15063724, 15720364, 
					16257403, 16470352, 17502463, 20647135, 24170635, 24175360, 24603175, 24730615, 25147063,
					25160374, 25164073, 25307461, 25317460, 25703641, 25704613, 25713064, 26174035, 26175304,
					27360514, 30471625, 30475261, 31475026, 31625704, 31625740, 31640752, 31746025, 31750246,
					35041726, 35716024, 35720641, 36074152, 36271405, 36415027, 36420571, 37025164, 37046152,
					37420615, 40357162, 40731625, 40752613, 41357206, 41362750, 41506372, 41703625, 42057136,
					42061753, 42736051, 46027531, 46031752, 46137025, 46152037, 46152073, 46302751, 47302516,
					47306152, 50417263, 51602473, 51603742, 52064713, 52073164, 52074136, 52460317, 52470316,
					52613704, 52617403, 52630714, 53047162, 53174602, 53602417, 53607142, 57130642, 60275314,
					61307425, 61520374, 62057413, 62714053, 63147025, 63175024, 64205713, 71306425, 71420635,
					72051463, 73025164]


	def test_eight_queen_1(self):
		self.assertEqual( len(eight_queen()), 92)

	def test_eight_queen_2(self):
		self.assertEqual( eight_queen(), self.eight_queen_solutions)


	def test_four_queen_1(self):
		self.assertEqual( len(n_queen(4)), 2)

	def test_four_queen_2(self):
		self.assertEqual( n_queen(4), [1302, 2031])

	def test_five_queen_1(self):
		self.assertEqual( len(n_queen(5)), 10)

	def test_five_queen_2(self):
		self.assertEqual( n_queen(5), [2413, 3142, 13024, 14203, 20314, 24130, 30241, 31420, 41302, 42031])

	def test_six_queen_2(self):
		self.assertEqual( len(n_queen(6)), 4 )

	def test_six_queen_2(self):
		self.assertEqual( n_queen(6), [135024, 251403, 304152, 420531] )

	def test_seven_queen_1(self):
		self.assertEqual( len(n_queen(7)), 40)

	def test_seven_queen_2(self):
		self.assertEqual( n_queen(7), self.seven_queen_solutions )

	def test_eight_queen_3(self):
		self.assertEqual( len(n_queen(8)), 92)

	def test_eight_queen_4(self):
		self.assertEqual( n_queen(8), self.eight_queen_solutions)

	def test_nine_queen(self):
		self.assertEqual( len(n_queen(9)), 352)

if __name__ == '__main__':
	unittest.main()





