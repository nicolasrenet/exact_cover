#!/usr/bin/python3

import unittest
import random

"""
A Python library for solving Exact Cover problems, with the DLX "Dancing Links" implementation.

Reference: Donald KNUTH, **Dancing Links**, 2002.

Both standard (Pentomino, sudokus) and generalized (N-Queen) exact cover problems can be solved.

"""

LOGLEVEL=3

def log( content, level=3):
	if level <= LOGLEVEL:
		print(content)

class Color:
	MAGENTA = '\033[91m'
	OKGREEN = '\033[92m'
	ENDC = '\033[0m'


class Node():
	""" 
	A data node: the elementary unit of the net of linked lists that represent the exact cover matrix
	in the DLX algorithm.
	"""
	
	def __init__(self, l=None, r=None, u=None, d=None,row=0):
		self.left = l
		self.right = r
		self.up = u
		self.down = d
		# pointer to the column header
		self.column = None
		
		# Useful only for logging the list
		self.row = row
		

class ColumnHeader():
	""" Head of a column list """
	def __init__(self, name, size=0, l=None, r=None, u=None, d=None):
		self.name=str(name)
		self.size=size
		self.left=l
		self.right=r
		self.up=u
		self.down=d
		

class ExactCover():
	""" Exact Cover problem."""

	def __init__(self, secondary=0):
		""" 
		Initialization procedure.

		:param secondary: the first index of a secondary column or, alternatively, the number of primary columns. Provide non-zero value to instantiate a generalized exact cover problem, such as the N-queen problem.
		:type secondary: int
		"""
		# Linked list
		self.h = None
		self.node_matrix = None
		self.secondary = secondary
		self.matrix = []


	def build_links(self):
		"""
		Build the net of linked-lists, from the Boolean matrix set for the problem.
		
		:return: the root node, i.e. a dummy header, the first node in the list of headers.
		:rtype: exact_cover.ColumnHeader
		"""
		self.node_matrix = [ [ None for j in range(len(self.matrix[0])) ] for i in range(len(self.matrix)) ]
		# going row by row, constructing horizontal linked lists
		for row in range(len(self.matrix)):
			left = None
			first = None
			for col in range(len(self.matrix[0])):
				if self.matrix[row][col]==1:
					if left is None:
						first = Node(row=row)
						left = first
					else:
						left.right=Node(left,row=row)
						left = left.right
					self.node_matrix[row][col]=left
			left.right = first
			first.left = left

		# going column by column, constructing the vertical linked lists, with their headers
		h = ColumnHeader("H")
		left = h
		for col in range( len(self.matrix[0])) :
			colname=col
			head = ColumnHeader(name=colname,l=left)

			# regular exact cover problem: all headers linked together
			if self.secondary == 0 or (self.secondary > 0 and col < self.secondary):
				left.right = head
				head.left = left
			# generalized problem: only primary columns linked together
			else:
				# link last primary column to root
				if col == self.secondary:
					left.right = h
				# circular pointer on remaining nodes
				head.left = head
				head.right = head
				
			up = head
			size = 0
			for row in range( len(self.matrix)):
				if self.matrix[row][col] == 1:
					node = self.node_matrix[row][col]
					up.down = node
					node.up = up
					node.column = head
					up = node
					size += 1
			up.down = head
			head.up = up	
			head.size = size
			left = head
		if (self.secondary == 0):
			head.right=h
			h.left = head
		self.h = h

	def cover_column(self, c):
		""" Cover a column. This happens in 2 cases:
			* a row in this column is currently selected in the solution
			* the column conflicts with the current selection of rows

		:param c: a column header
		:type c: exact_cover.ColumnHeader
		"""
		# remove c from the horizontal linked list
		log("cover_column({})".format(int(c.name)+1))
		c.right.left = c.left
		c.left.right = c.right
		
		# for each conflicting row...
		i = c.down

		# ... suppress nodes in that row
		while i is not c:
			log("Cover row {}".format(i.row+1))
			j  = i.right
			# fixing vertical links
			while j is not i:
				j.down.up = j.up
				j.up.down = j.down
				j.column.size -= 1
				j = j.right
			i = i.down

	def uncover_column(self, c):
		""" Uncover a column, when backtracking.

		:param c: a column header
		:type c: exact_cover.ColumnHeader
		"""
		log("uncover_column({})".format(int(c.name)+1))
		i = c.up
		while i is not c:
			j = i.left
			while j is not i:
				j.column.size += 1
				j.down.up = j
				j.up.down = j
				j = j.left
			i = i.up
		c.right.left = c
		c.left.right = c


	def solve( self, solution_length, count_only=False ):
		""" Solve a problem, by a recursive filtering of the matrix, in its linked-list implementation.
		
		:param solution_length: the number of rows to be selected in the matrix. Ex. 12 for the 12 pieces 
		of a Pentomino problem, 81 for the 81 positions of a 9x9 sudoku, 8 for an 8-Queen problem...
		:param count_only: just return the number of solutions; do not print them.
		:type solution_length: int
		:type count_only: boolean
		:return: the number of solutions
		:rtype: int
		"""
		solution = [ None for s in range(solution_length) ]
		
		solution_count = 0

		def search( k, solution ):
			""" The recursive procedure of the DLX algorithm:
				* by trial-and-error, select rows in the matrix
				* delete conflicting rows and columns
				* recursively search the matrix so reduced
			The procedure returns in 2 cases:
				* deadend: the branch explored does not lead to a solution
				* success: the matrix is empty, i.e. an assignment has been found
			:param k: the level of recursion
			:solution: the vector of solution rows; each element is a data node in the corresponding row of the
			linked-list matrix; it is not guaranteed the node points to the first element of the row:  proper
			iteration over the row list in order to produce a readable solution is left to the solution_string()
			procedure, which is to be overriden by the subclasses.
			:type k: int
			:type solution: exact_cover.Node
			"""
			
			nonlocal solution_count

			log("search({})".format(k))
			#log(self.links_string( headers_only=False))
			#log( self.solution_string( solution) )

			if self.h.right is self.h:
				solution_count += 1
				if not count_only:
					print("SUCCESS")
					print(self.solution_string( solution, solution_count ))
				return

			c = self.h.right
			min_c = self.h.right
			min_size = self.h.right.size
			while c is not self.h:
				if c.size < min_size:
					min_c = c
					min_size = c.size 
				c = c.right
			c = min_c
			
			if (c.size == 0):
				log("DEAD END! Column {} has not been selected, but all rows in it have been removed. Backtracking...".format(int(c.name)+1))
				return

			log("Examining rows in column {} (as part of the solution)".format( int(c.name)+1))
			self.cover_column( c )
			r = c.down
			while r is not c:
				log("Select row {}".format(r.row+1 ))
				solution[k] = r 
				log( self.solution_string( solution ))
				j = r.right
				while j is not r:
					log("Covering column {} (conflict with row {})".format( int(c.name)+1, r.row+1))
					self.cover_column( j.column )
					j = j.right

				search(k+1, solution)

				log("Back to level {}".format(k))
				r = solution[k]
				log("Deselect row {}".format(r.row+1 ))
				solution[k] = None
				c = r.column
				j = r.left
				while j is not r:
					self.uncover_column( j.column)
					j = j.left

				r = r.down
			log("Removing column {} from the solution)".format( int(c.name)+1))
			self.uncover_column( c )

		search(0, solution)

		return solution_count

	def matrix_string(self, l=0,r=36 ):
		matrix_str = ''
		for i in self.matrix:
			matrix_str += str(i[l:(r+1)]) + '\n'
		return matrix_str

	def columns_string(self):
		node = self.h.right
		headers_string = "-> " + self.h.name + " --> "
		count = 0
		while node is not self.h:
			if node.right is self.h:
				headers_string += "{} -".format(node.name)
			else:
				headers_string += "{} --> ".format(node.name)
			count += 1
			node = node.right
		return headers_string


	def links_string(self, right=36, headers_only=True,color=False):

		links_str_array = ['\n']

		strings_matrix = [ [ '+' for j in range(len(self.node_matrix[0][:right]))] for i in range(len( self.node_matrix )) ]	
		strings_matrix.insert(0, [ '+' for j in range(len(self.node_matrix[0][:right])) ] )

		# By default, all data nodes in red
		for i in range(len(self.node_matrix)):
			for j in range(len(self.node_matrix[i][:right])):
				if self.node_matrix[i][j] is not None:
					if color:
						strings_matrix[ i+1 ][j] = Color.MAGENTA + 'o' + Color.ENDC
					else:
						strings_matrix[ i+1 ][j] =  'X' 

		# Active nodes (i.e. in the list) are in green
		col = self.h.right
		while col is not self.h and int(col.name)<right:
			node=col.down
			strings_matrix[0][ int(col.name) ] = col.name
			while node is not col:
				if color:
					strings_matrix[ node.row+1 ][ int(col.name) ] = Color.OKGREEN + 'O' + Color.ENDC
				else:
					strings_matrix[ node.row+1 ][ int(col.name) ] = 'O'
				node = node.down
			
			col = col.right
		
		links_str_array.append(' '+'  '.join([ '|' for el in strings_matrix[0] ]))

		colheaders_string = '-'
		for colnumber in  strings_matrix[0]:
			if len(colnumber) == 1:
				colheaders_string += colnumber + '--'
			else:
				colheaders_string += colnumber + '-'

		links_str_array.append(colheaders_string)

		if not headers_only:
			for line in strings_matrix[1:]:
				links_str_array.append(' '+'  '.join([ '|' for el in line ]))
				links_str_array.append('-'+'--'.join( line) + '-')
			links_str_array.append(' '+ '  '.join([ '|' for el in line ]) + '\n')

		return '\n'.join( links_str_array )
		

		
	def solution_string(self, solution, solution_count=0 ):
		solution_str=("\n-----Solution------\n")
		for i in solution:
			if i is None: break
			j = i.right
			nodes = [ i.column.name ]
			while j is not i:
				nodes.append( j.column.name) 
				j = j.right
			
			solution_str += str(sorted([ str(n) for n in nodes ])) + '\n'
		return solution_str





class ExactCover_UnitTest( unittest.TestCase ):



#	def test_build_links(self):
#
#		ec = ExactCover()
#		
#		ec.build_links( self.matrix )			
#
#		self.assertEqual( ec.h.name, "H" )
#		self.assertEqual( ec.h.right.size, 2 )
#		self.assertEqual( ec.h.right.right.size, 2 )
#		self.assertEqual( ec.h.right.right.right.size, 2 )
#		self.assertEqual( ec.h.right.right.right.right.size, 3 )
#		self.assertEqual( ec.h.left.size, 3 )
#		self.assertEqual( ec.h.left.left.size, 2 )
#		self.assertEqual( ec.h.left.left.left.size, 2 )
#
#	def test_print_columns(self):
#		
#		ec = ExactCover()
#		ec.build_links( self.matrix )
#		
#		ec.print_columns() 
#
#	def test_print_links(self):
#		ec = ExactCover()
#		ec.build_links( self.matrix)
#		ec.print_links()
#
#		ec.print_matrix( self.matrix )
#
#
#	def test_cover_column(self):
#
#		ec = ExactCover()
#		ec.build_links( self.matrix )			
#
#		# uncovering column "0"
#		ec.cover_column( ec.h.right )
#
#		self.assertEqual( ec.h.right.size, 2)
#		self.assertEqual( ec.h.right.name, "1")
#		self.assertEqual( ec.h.right.right.size, 2)
#		self.assertEqual( ec.h.right.right.name, "2")
#		self.assertEqual( ec.h.right.right.right.size, 1)
#		self.assertEqual( ec.h.right.right.right.name, "3")
#		self.assertEqual( ec.h.left.size, 2)
#		self.assertEqual( ec.h.left.name, "6")
#		self.assertEqual( ec.h.left.left.size, 2)
#		self.assertEqual( ec.h.left.left.name, "5")
#		self.assertEqual( ec.h.left.left.left.size, 2)
#		self.assertEqual( ec.h.left.left.left.name, "4")
#
#		ec.print_columns()
#		# uncovering column "3"
#		ec.cover_column( ec.h.right.right.right )
#		ec.print_columns()
#		# uncovering column "6"
#		ec.cover_column( ec.h.left )
#		ec.print_columns()
#		self.assertEqual( ec.h.right.name, "1")
#		self.assertEqual( ec.h.right.right.name, "2")
#		self.assertEqual( ec.h.right.right.right.name, "4")
#		self.assertEqual( ec.h.left.name, "5")
#		self.assertEqual( ec.h.name, "H")
#
#	def test_uncover_column(self):
#		ec = ExactCover()
#		ec.build_links( self.matrix )			
#
#		# covering all columns except one
#		for i in range(6):
#			ec.cover_column( ec.h.right )
#
#		ec.print_columns()
#		c = ec.h.right
#
#		ec.cover_column( c )
#
#		ec.print_columns()
#
#
#		ec.uncover_column( c )
#
#		ec.print_columns()
#
#		self.assertEqual( ec.h.right.name, "6")
#
#		
		
	def print_matrix( self, matrix ):
		print("\n\n[", end='')
		for r in matrix[:-1]:
			print('{},'.format(r))
		print('{}]'.format(matrix[-1]))

	def has_null_column( self, matrix, primary_count=-1):
		colcount = len(matrix)
		nullcol = [ 0 for i in matrix ]
		for col in range(0, colcount ):
			if (primary_count >0 and col < primary_count) and [ rw[col] for rw in matrix ] == nullcol:
				return True
		return False


	def random_matrix(self, rows=6, cols=6, primary_count=-1):
	
		ROWS=rows
		COLS=cols
		matrix = [ [ 0 for c in range(0, COLS) ] for r in range(0,ROWS) ] 

		while( self.has_null_column( matrix, primary_count )):	
			self.print_matrix( matrix )
			for r in range(0,ROWS):
				while matrix[r] == [0]*COLS:
					matrix[r]  = [ random.choice( (0,1) ) for el in range(0, COLS ) ]

		return(matrix)

	matrix1 = (	
			(1,0,0,1,0,0,1),
			(1,0,0,1,0,0,0),
			(0,0,0,1,1,0,1),
			(0,0,1,0,1,1,0),
			(0,1,1,0,0,1,1),
			(0,1,0,0,0,0,1))

	
	matrix2 = [	[0, 1, 1, 0, 1, 0, 0],
			[0, 0, 0, 1, 1, 0, 1],
			[0, 0, 0, 0, 0, 1, 0],
			[1, 0, 1, 0, 0, 0, 0],
			[1, 1, 1, 0, 0, 1, 0],
			[0, 0, 0, 1, 1, 0, 1],
			[0, 1, 1, 0, 0, 1, 1]]

	matrix3 = [	[0, 1, 1, 1, 0, 0, 1],
			[0, 1, 0, 1, 1, 1, 0],
			[0, 0, 1, 0, 0, 1, 1],
			[1, 1, 0, 1, 1, 0, 1],
			[0, 0, 0, 0, 1, 0, 0],
			[1, 0, 0, 0, 0, 0, 0],
			[1, 1, 0, 1, 0, 0, 0]]

	matrix4 = [	[0, 1, 1, 1, 0, 1, 1],
			[0, 0, 0, 1, 1, 1, 1],
			[0, 1, 0, 1, 1, 1, 0],
			[1, 0, 1, 0, 1, 1, 1],
			[0, 0, 0, 0, 1, 1, 0],
			[0, 1, 0, 0, 1, 1, 1],
			[1, 1, 1, 1, 1, 1, 1]]


	## Generalized matrices
	matrix5 = [	[0, 1, 0, 1, 0, 1, 1],
			[0, 1, 1, 1, 1, 0, 0],
			[1, 0, 1, 0, 0, 1, 0],
			[1, 1, 1, 1, 1, 0, 0],
			[1, 1, 0, 0, 1, 1, 1],
			[0, 0, 0, 0, 0, 1, 0],
			[0, 1, 1, 1, 0, 1, 0]]


	matrix6 = [	[0, 0, 1, 0, 0, 1, 0],
			[0, 0, 0, 1, 1, 0, 0],
			[0, 1, 0, 1, 0, 0, 0],
			[1, 0, 1, 0, 0, 0, 1],
			[0, 1, 0, 0, 1, 1, 0],
			[0, 0, 0, 1, 1, 0, 1],
			[1, 0, 1, 1, 0, 0, 1]]

	def atest_search_1(self):
			
		ec = ExactCover()
		ec.matrix = self.matrix1
		self.print_matrix( ec.matrix)
		ec.build_links()
	
		self.assertTrue( ec.solve(6) == 1)

	def atest_search_2(self):
			
		ec = ExactCover()
		ec.matrix = self.matrix2
		self.print_matrix( ec.matrix)
		ec.build_links()
	
		self.assertTrue( ec.solve(7) == 2)

	def test_search_3(self):
			
		ec = ExactCover()
		ec.matrix = self.matrix3
		self.print_matrix( ec.matrix)
		ec.build_links()
	
		self.assertTrue( ec.solve(7) == 1)

	def atest_search_4(self):
			
		ec = ExactCover()
		ec.matrix = self.matrix4
		self.print_matrix( ec.matrix)
		ec.build_links()
	
		self.assertTrue( ec.solve(7) == 1)

	def test_search_5(self):
			
		ec = ExactCover(5)
		ec.matrix = self.matrix5
		self.print_matrix( ec.matrix)
		ec.build_links()
	
		self.assertTrue( ec.solve(7) == 1)

	def test_search_6(self):
			
		ec = ExactCover(5)
		ec.matrix = self.matrix6
		self.print_matrix( ec.matrix)
		ec.build_links()
	
		self.assertTrue( ec.solve(7) == 1)

	def atest_search_2(self):

		for trial in range(1,10):
			
			matrix = self.random_matrix(7,7,5)
			print("\n\n====== Starting test {}:".format( trial))		
			self.print_matrix( matrix)
			ec = ExactCover(5)
			ec.matrix = matrix
			ec.build_links()
	
			ec.solve(7, False)

def main():
        unittest.main()

if __name__ == '__main__':
        main()

