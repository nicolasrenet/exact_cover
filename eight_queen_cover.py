#!/usr/bin/python3

import unittest
import time
import random
from exact_cover import *


class EightQueen( ExactCover ):

	def __init__(self, gw=10, gh=6):


		self.queens = [ 0 ] * 8
		self.up_diag = [ True ] * 8
		self.down_diag = [ True ] * 8
		

	def print_solution(self, solution ):
		print("\n-----Solution------")
		for i in solution:
			if i is None: break
			j = i.right
			nodes = [ self.matrix_col_to_grid( int(i.column.name) ) ]
			#print(j.column)
			while j is not i:
				#print(j.column.name)
				nodes.append( self.matrix_col_to_grid( int(j.column.name) ))
				j = j.right
			
			print(sorted([ str(n) for n in nodes ]))
	

		
	def build_matrix(self): 

		# A matrix of all possible ways to place 8 queens on the board:
		# First 8 columns represent ranks
		# Next 8 columns represent files
		# Next 15 columns represent up-diags
		# Last 15 columns represent down-diags
		matrix = []

		for rank in range(8):
			for file in range(8):
				matrix_row = [0] * (8*2 + 15*2)
				matrix_row[rank]=1
				matrix_row[8 + file] = 1
				matrix_row[16 + (rank+file) ] = 1
				matrix_row[16 + 15 + (file-rank + 8 - 1) ] = 1
				print(matrix_row)
				matrix.append( matrix_row )
		return matrix


p = EightQueen()

matrix = p.build_matrix()
print(matrix)

p.build_links( matrix )

solution =  [ None for i in range(8) ] 

#start = time.time()
p.search(0, solution)
#print("Time elapsed: {}mn".format( (time.time() - start)//60))

p.print_solution( solution )





#class Pentomino_TestClass( unittest.TestCase):
#	
#	piece = ((0,0,1), 
#		(1,1,1),
#		(0,1,0))
#
#	def test_rotate_90( self ):
#		self.assertEqual( rotate_90( self.piece), [[0,1,0],[1,1,0],[0,1,1]])		
#
#	def test_rotate_180( self ):
#		self.assertEqual( rotate_180( self.piece), [[0,1,0],[1,1,1],[1,0,0]])		
#
#	def test_rotate_270( self ):
#		self.assertEqual( rotate_270( self.piece), [[1,1,0],[0,1,1],[0,1,0]])		
#
#
#	def test_grid_coordinates_to_matrix_col(self):
#		
#		self.assertEqual( grid_to_matrix_col( 0,0 ), 12 )
#		self.assertEqual( grid_to_matrix_col( 0,9 ), 21 )
#		self.assertEqual( grid_to_matrix_col( 1,0 ), 22 )
#		
#	def test_matrix_col_to_grid_coordinates(self):
#		self.assertEqual( matrix_col_to_grid(12), (0,0))
#		self.assertEqual( matrix_col_to_grid(21), (0,9))
#		self.assertEqual( matrix_col_to_grid(22), (1,0))
#
#
#	def atest_known_solution(self):
#		# construct the matrix of a know solution
#		summary = (
#			(15,16,17,18,19),
#			(26,36,37,38,48),
#			(61,68,69,70,71),
#			(12,13,22,32,33),
#			(14,23,24,25,34),
#			(41,50,51,59,60),
#			(20,21,30,31,40),
#			(47,57,58,66,67),
#			(55,56,63,64,65),
#			(42,52,53,54,62),
#			(27,28,29,39,49),
#			(35,43,44,45,56))
#
#		matrix = [ [ 0 for j in range(72) ] for i in range(12) ]
#
#		
#		row=0
#		for idx in range(len(summary)):
#			matrix[row][idx]=1
#			for pos in summary[idx]:
#				matrix[row][pos]=1
#			row += 1
#		
#		def junk_row():
#			new_row = [0] * 72
#			index_pool = list( range(0,72) )
#			for  i in range(5):
#				idx = random.randint(0,len(index_pool)-1)
#				new_row[idx]=1
#				index_pool.pop(idx)
#			return new_row
#				
#		for junk in range(0):
#			new_pos = random.randint(0,len(matrix)-1)
#			matrix.insert( new_pos, junk_row())
#
#		
#		print_matrix(matrix,12,72)
#
#		lists = build_links( matrix )	
#
#		solution = [None for i in range(12) ]
#		search(0, lists, solution)
#		print(solution)
#		print_solution(solution)
#
#
#def main():
#        unittest.main()

#if __name__ == '__main__':
#        main()

