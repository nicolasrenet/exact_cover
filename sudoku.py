#!/usr/bin/python3

import unittest
import exact_cover as dlx

dlx.LOGLEVEL=1

class Sudoku( dlx.ExactCover ):

	
		def __init__(self, game, box_constraint ):
			super().__init__()
			self.game = game
			self.build_matrix( box_constraint )
			self.build_links()

		def build_matrix(self, box_constraint = False):
			dlx.log( "build_matrix(box_constraint={})".format( box_constraint))
			self.matrix = self.game_to_matrix( self.game, box_constraint )


		def solution_string(self, solution, solution_count=0):
			count = 0
			if solution_count > 0: count = solution_count

			solution_str_array = ["\n-----  Solution {} ------\n".format(count) ]

			# the solution rows, in raw form
			solution_entries_array = []
			for i in solution:
				if i is None: break
				nodes = [ int(i.column.name) ]
				j = i.right
				while j is not i:
					nodes.append( int(j.column.name))
					j = j.right
				solution_entries_array.append( sorted( nodes))
			#solution_str_array += [ str( entry ) for entry in  sorted( solution_entries_array, key=lambda x: x[0]) ]

			# the sudoku grid
			#print(solution_entries_array)
			solution_grid = [ row[:] for row in self.game ]		
			for entry in solution_entries_array:
				row = (entry[2]-(9*18))//9	
				col = (entry[2]-(9*18))%9	
				solution_grid[row][col] = entry[0]//18+1
			solution_str_array.append('')
			solution_str_array.append( self.game_string( solution_grid ))

			return '\n'.join( solution_str_array )

		
		def game_string( self, game ):
			game_str_array = []
			for row in game:
				game_str_array.append( str(row) )
			return '\n'.join( game_str_array)
				
					
		def game_to_matrix(self, game, box_constraint = False ):
			""" Construct an exact cover matrix from a partially filled grid
			
			:param game: a numerical matrix of values in the range [0-9], where 0 indicates an empty position
			:param box_constraint: meet the box constraint requirement
			:type box_constraint: bool
			:return: a Boolean matrix, with 243 (box constraint relaxed) or 486 (with box constraint met) columns
			:rtype: list
			"""
			matrix = []
			
			dlx.log( "game_to_matrix(box_constraint={})".format( box_constraint))
			# compute set of values contained in every row and column, in order to narrow down
			# the set of candidate values for empty cells
			row_sets = []
			for row_val in game:
				row_set = set()
				for col_val in row_val:
					if col_val > 0:
						row_set.add( col_val )
				row_sets.append( row_set )
			
			col_sets = []
			for col in range(len(game[0])):
				col_set = set()
				col_val = [ game[row][col] for row in range(len(game)) ]
				for val in col_val:
					if val > 0:
						col_set.add( val )
				col_sets.append( col_set )

			box_sets = []
			for box_row in range(3):
				for box_col in range(3):
					box_set = set()
					for m in range(3):
						for n in range(3):
							val = game[ box_row*3 + m][box_col*3 + n]
							if val > 0:
								box_set.add( val )
					dlx.log(box_set, 2)	
					box_sets.append( box_set )

				
			# go row by row...
			for  row in range(len(game)):
				for col in range(len(game[row])):
					val = game[row][col]
					# if value set, create the corresponding, unique row in the matrix
					
					if val > 0:
						matrix.append( self.set_row( row, col, val, box_constraint ))
					else:
						possible_values = { 1, 2, 3, 4, 5, 6, 7, 8, 9 }
						# compute the complement of the union of the row set and col set
						possible_values -= ( row_sets[row] | col_sets[col] )
						dlx.log(possible_values, 2)
						if box_constraint:
							box_number = ( row - row%3 + col// 3)
							#dlx.log('{} - {}'.format( possible_values, box_sets[box_number]), 2)
							possible_values -= box_sets[box_number]
							dlx.log("-->{}".format(possible_values),2)
						#print("Possible values: {}".format(possible_values)
						for possible in possible_values:
							matrix.append( self.set_row( row, col, possible, box_constraint ))
			print(len(matrix))
			#self.print_matrix(matrix)

			return matrix


		def print_matrix(self, matrix):
			for row in matrix:
				for col in row:
					print('{}'.format(col),end="")
				print('')

		def row_col_flatten(self, row, col):
			return row * 9 + col



		def set_row(self, row, col, val, box):
			""" 
			Create a new row in the matrix, with the following pattern:
			
			Subarrays R1-C1 (ensure that each of the nine 1s is on its own row and column)

			[ row placement of value 1: 9 elements ] [ col placement of value 1: 9 elements ]

			Subarrays R2-C2 (ensure that each of the nine 2s is on its own row and column)

			[ row placement of value 1: 9 elements ] [ col placement of value 1: 9 elements ]
	
			...

			Subarrays R9-C9 (ensure that each of the nine 9s is on its own row and column)

			[ row placement of value 1: 9 elements ] [ col placement of value 1: 9 elements ]

			Subarray P (ensure that no position is set by 2 different numbers)

			[ 0 .. 81 ]

			Total: 18*9  + 81 = 243

			If box constraint is to be met, the matrix has 81 extra columns: one for each box, with 9 positions in each (corresponding to the values set for that box)

			Example:
				if grid contains 7 in (5,8), create a new row of size 180 in the matrix with the following positions set to 1:

				R7[5] 	(7 is assigned row 5)
				C7[8] 	(7 is assigned col 8)
				P[4*9+8](grid position 44 is set)	
				

			Grid cells that have 2 or more candidate values result in as many new rows in the matrix.

			:param row: grid row
			:param col: grid column
			:param val: grid value
			:param box: meet the box constraint requirement
			"""
			#dlx.log( "set_row(box_constraint={})".format( box))
			if (box):
				m_row = [ 0 for i in range( 9*18+ (81*2) ) ]
			else:
				m_row = [ 0 for i in range( 9*18 + 81 ) ]
			# grid position
			m_row[ (9*2)*9  + self.row_col_flatten( row, col) ] = 1

			# set row / col for value
			m_row[ (val-1) * 18 + row ]=1
			m_row[ (val-1) * 18 + 9 + col ]=1

			#print(m_row)

			# box constraint
			if (box):
				# box number, as computed from row/col
				box_row = row//3
				box_col = col//3
				box_number = (box_row * 3) + box_col
				# setting value for this box in the matrix
				m_row[ 243 + box_number * 9 + (val-1) ]=1	

			#print(sum(m_row))
			return m_row
		


class SudokuTest( unittest.TestCase):

	game1 = [
		[5,0,0, 0,1,2, 7,8,0],
		[0,0,7, 0,0,0, 6,4,0],
		[0,0,0, 0,0,7, 0,0,1],
		[0,0,6, 8,0,0, 0,0,0],
		[3,4,0, 0,0,0, 0,7,6],
		[0,0,0, 0,0,6, 9,0,0],
		[1,0,0, 5,0,0, 0,0,0],
		[0,8,2, 0,0,0, 5,0,0],
		[0,5,3, 7,8,0, 0,0,9]
	]

	game2 = [
		[9,0,0, 0,7,0, 0,1,3],
		[0,0,4, 0,0,0, 2,0,0],
		[1,0,0, 9,0,0, 0,0,0],
		[0,8,1, 7,0,0, 0,0,0],
		[0,0,0, 6,2,1, 0,0,0],
		[0,0,0, 0,0,3, 4,7,0],
		[0,0,0, 0,0,8, 0,0,9],
		[0,0,5, 0,0,0, 6,0,0],
		[3,4,0, 0,9,0, 0,0,8]
	]


	def atest_set_row(self):
		
		sudoku = Sudoku( self.game1, False )
		control = [0] * (243 )

		control [ 196 ]=1 	# grid position
		control [ 129 ]=1	# number row
		control [ 142 ]=1	# number col

		print(control)
		print(sudoku.set_row(3,7,8,False))

		self.assertTrue( sudoku.set_row(3,7,8,False) == control )

	def test_1_sudoku_without_box_constraint(self):
		sudoku = Sudoku( self.game1, False )
		self.assertEqual( sudoku.solve(81, count_only=False), 94571)

	
	def atest_2_sudoku(self):
		sudoku = Sudoku( self.game1, True )
		self.assertEqual( sudoku.solve(81, count_only=False), 1)

	
	def atest_3_sudoku_without_box_constraint(self):
		sudoku = Sudoku( self.game2, False )
		self.assertEqual( sudoku.solve(81, count_only=True), 1582533)

	
	def atest_4_sudoku(self):
		sudoku = Sudoku( self.game2, True )
		self.assertEqual( sudoku.solve(81), 1)
		

if __name__=='__main__':
	unittest.main()
