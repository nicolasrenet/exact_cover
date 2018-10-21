#!/usr/bin/python3

import unittest
import time
import random
import exact_cover as dlx

dlx.LOGLEVEL=2


class Pentomino( dlx.ExactCover ):

	def __init__(self, gw=10, gh=6):

		super().__init__()

		self.I = ((1,1,1,1,1),)

		self.N = (	(0, 2, 2),
				(0, 2, 0),
				(2, 2, 0))

		self.L = ( 	(3,0),
				(3,0),
				(3,0),
				(3,3))

		self.U = (	(4, 0, 4),
				(4, 4, 4))

		self.X = ( 	(0,5,0),
				(5,5,5),
				(0,5,0))

		self.W = (	(6, 6, 0),
				(0, 6, 6),
				(0, 0, 6))

		self.P = ( 	(7,7),
				(7,7),
				(7,0))

		self.F = ( 	(0,8,8),
				(8,8,0),
				(0,8,0))

		self.Z = ( 	(9,0),
				(9,9),
				(0,9),
				(0,9))

		self.T = (	(10, 10, 10),
				(0,  10, 0),
				(0,  10, 0))

		self.V = (	(11, 11, 11),
				(11, 0, 0),
				(11, 0, 0))

		self.Y = ( 	(0, 12),
				(12,12),
				(0, 12),
				(0, 12))

		self.grid_width = gw
		self.grid_height = gh

		self.build_matrix()
		self.build_links()
		
	def print_grid(self, gr ):
		string_buffer=''
		symbols = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, '*','%','#' ]
		for i in range(len(gr)):
			for j in range(len(gr[0])):
				string_buffer += "{} ".format( symbols[ gr[i][j] ])
			string_buffer += "\n"
		print(string_buffer)


	# reflect and rotate functions
	@classmethod
	def reflect_horizontal(cls, piece ):
		return piece[::-1] 

	@classmethod
	def reflect_vertical(cls, piece ):
		return [ list(row[::-1]) for row in piece ] 

	@classmethod
	def rotate_90(cls, piece ):
		return [[ row[j] for row in piece[::-1]] for j in range(len(piece[0])) ]

	@classmethod
	def rotate_180(cls, piece ):
		return [ list(row[::-1]) for row in piece[::-1]] 

	@classmethod
	def rotate_270(cls, piece ):
		return [[ row[j] for row in piece ] for j in reversed( range(len(piece[0])))]


	def grid_to_matrix_col(self, row, col ):
		return 12 + row*self.grid_width + col 

	def matrix_col_to_grid(self, c ):
		
		if c < 12:
			return ("Piece", str(c+1))
		
		i = (c-12)//self.grid_width
		j = (c-12)-i*self.grid_width
		return (i,j)


	def populate_matrix(self, m, piece_id, piece ): 
		
		row_length = 12 + self.grid_height*self.grid_width

		# for all possible positions in the grid
		for row in range( self.grid_height-len(piece)+1):
			for col in range( self.grid_width-len(piece[0])+1):
				m.append( [0] * row_length )
				# set the corresponding pentomino column
				m[-1][piece_id-1] = 1
				# for all active positions in the pentomino
				for i in range( len(piece) ):
					for j in range( len(piece[0])):
						if piece[i][j]>0:
							grid_i, grid_j = row + i, col + j
							#print("Column {} =  matrix position ({},{})".format( grid_to_matrix_col(grid_i, grid_j), grid_i, grid_j))
							m[-1][ self.grid_to_matrix_col(grid_i, grid_j)] = 1
	 
		
	def solution_string(self, solution, solution_count=0 ):
		count = 0
		if solution_count > 0: count = solution_count
		solution_str_array = ["\n-----  Solution {}  ------".format(count)]
		for i in solution:
			if i is None: break
			j = i.right
			nodes = [ self.matrix_col_to_grid( int(i.column.name) ) ]
			#print(j.column)
			while j is not i:
				#print(j.column.name)
				nodes.append( self.matrix_col_to_grid( int(j.column.name) ))
				j = j.right
			
			solution_str_array.append(str( sorted([ str(n) for n in nodes ])))
		return '\n'.join( solution_str_array )

		
	def build_matrix(self): 

		# A matrix of all possible ways to insert all 12 pentominos on the grid
		matrix = []

		self.populate_matrix( matrix, 5, self.X )

		for instance in self.I, self.rotate_90( self.I ):
			self.populate_matrix( matrix, 1, instance )

		for instance in self.N, self.rotate_90(self.N), self.rotate_180(self.N), self.rotate_270(self.N):
			self.populate_matrix( matrix, 2, instance)

		for instance in self.L, self.rotate_90(self.L), self.rotate_180(self.L), self.rotate_270(self.L), self.reflect_horizontal(self.L), self.reflect_horizontal(self.rotate_90(self.L)), self.reflect_horizontal(self.rotate_180(self.L)), self.reflect_horizontal(self.rotate_270(self.L)):
			self.populate_matrix( matrix, 3, instance)

		for instance in self.U, self.rotate_90(self.U), self.rotate_180(self.U), self.rotate_270(self.U):
			self.populate_matrix( matrix, 4, instance)

		for instance in self.W, self.rotate_90(self.W), self.rotate_180(self.W), self.rotate_270(self.W):
			self.populate_matrix( matrix, 6, instance)

		for instance in self.P, self.rotate_90(self.P), self.rotate_180(self.P), self.rotate_270(self.P), self.reflect_horizontal(self.P), self.reflect_horizontal(self.rotate_90(self.P)), self.reflect_horizontal(self.rotate_180(self.P)), self.reflect_horizontal(self.rotate_270(self.P)):
			self.populate_matrix( matrix, 7, instance)

		for instance in self.F, self.rotate_90(self.F), self.rotate_180(self.F), self.rotate_270(self.F), self.reflect_horizontal(self.F), self.reflect_horizontal(self.rotate_90(self.F)), self.reflect_horizontal(self.rotate_180(self.F)), self.reflect_horizontal(self.rotate_270(self.F)):
			self.populate_matrix( matrix, 8, instance)

		for instance in self.Z, self.rotate_90(self.Z), self.rotate_180(self.Z), self.rotate_270(self.Z), self.reflect_horizontal(self.Z), self.reflect_horizontal(self.rotate_90(self.Z)), self.reflect_horizontal(self.rotate_180(self.Z)), self.reflect_horizontal(self.rotate_270(self.Z)):
			self.populate_matrix( matrix, 9, instance)

		for instance in self.T, self.rotate_90(self.T), self.rotate_180(self.T), self.rotate_270(self.T):
			self.populate_matrix( matrix, 10, instance)

		for instance in self.V, self.rotate_90(self.V), self.rotate_180(self.V), self.rotate_270(self.V):
			self.populate_matrix( matrix, 11, instance)

		for instance in self.Y, self.rotate_90(self.Y), self.rotate_180(self.Y), self.rotate_270(self.Y), self.reflect_horizontal(self.Y), self.reflect_horizontal(self.rotate_90(self.Y)), self.reflect_horizontal(self.rotate_180(self.Y)), self.reflect_horizontal(self.rotate_270(self.Y)):
			self.populate_matrix( matrix, 12, instance)


		self.matrix = matrix




class Pentomino_TestClass( unittest.TestCase):
	
	piece = ((0,0,1), 
		(1,1,1),
		(0,1,0))

	def test_rotate_90( self ):
		self.assertEqual( Pentomino.rotate_90( self.piece), [[0,1,0],[1,1,0],[0,1,1]])		

	def test_rotate_180( self ):
		self.assertEqual( Pentomino.rotate_180( self.piece), [[0,1,0],[1,1,1],[1,0,0]])		

	def test_rotate_270( self ):
		self.assertEqual( Pentomino.rotate_270( self.piece), [[1,1,0],[0,1,1],[0,1,0]])		


	def test_grid_coordinates_to_matrix_col(self):
		
		pentomino = Pentomino()
		self.assertEqual( pentomino.grid_to_matrix_col( 0,0 ), 12 )
		self.assertEqual( pentomino.grid_to_matrix_col( 0,9 ), 21 )
		self.assertEqual( pentomino.grid_to_matrix_col( 1,0 ), 22 )
		
	def test_matrix_col_to_grid_coordinates(self):
		pentomino = Pentomino()
		self.assertEqual( pentomino.matrix_col_to_grid(12), (0,0))
		self.assertEqual( pentomino.matrix_col_to_grid(21), (0,9))
		self.assertEqual( pentomino.matrix_col_to_grid(22), (1,0))


	def test_solve(self):
		pentomino = Pentomino()
		solutions = pentomino.solve(12, True)
		print("Pentomino has {} solutions.".format(solutions))
		self.assertTrue( solutions > 0 )

def main():
        unittest.main()

if __name__ == '__main__':
        main()

