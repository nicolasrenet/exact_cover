#!/usr/bin/python3

import unittest
import time
import random
import exact_cover as dlx

dlx.LOGLEVEL=1

class WeeklySchedule( dlx.ExactCover ):

	def __init__(self, teachers, load, rooms, sudoku=False):


		super().__init__()

		self.teachers=teachers
		self.load=load
		self.rooms=rooms
		self.sudoku=sudoku

		self.build_matrix()
		self.build_links()

			
	def build_matrix(self): 

		# A matrix of all possible ways for 12 teachers to teach 3 hours in 2 rooms, but this time, _no teacher 
		# can teach twice in the same room
		#
		# Let 
		#	T = # teachers
		#	L = teaching (hours / teacher)
		#	n = # rooms
		#	H = business hours = TL/n 
		#  	
		#-------------------------------------------------------------------------------------------------------------------
		# Solution (1) - not implemented in this version
		#
		#  Default: we rely on the matrix-filling logic to ensure that no teacher is assigned the same hour in 2 different 
		#  rooms (no ubiquity!). 
		#
		#  Columns:
		#
		# | ... T teacher columns ... | TL/n slots for room 1 | TL/n slots for room 2 | ... | TL/n slots for room n
		# 
		# A row represents a schedule assignment for 1 teacher, that choose 3 slots out of the (n x T x L) possible slots
		#
		# For all teachers, only once:
		#  1) generate C(TL/n  L) L-combinations of slots actually worked
		#  2) generate all L-permutations of n rooms (repeats allowed)
		#  3) generate all L-tuples of pairs (hour slot, room)
		#
		#------------------------------------------------------------------------------------------------------------------
		#  Solution (2) It is a cleaner implementation of (1): relax constraint on room/teacher, while ensuring that no teacher
		# teaches in 2 rooms at the same hour, but this time enforced by the matrix
		#
		#  Columns:
		#
		#  | T Teacher cols |  Room-to-hour columns (n x H): rooms for H1, rooms for H2, ..., rooms for HH
		#
		# For each row, we select 
		#      - L of the corresponding R-to-H columns: a choice of 1 room (out of n) for everyone of the L hours (out of H hours) 
		#
		# Steps:
		#  	- generate all permutations of L rooms, repeat allowed (room_lets)  	= n^L elements
		#       - generate all combinations of L hours (hour_lets)			= C(H,L) elements
		#	- form sets of pairs (room, hour)
		#	- populate the matrix accordingly
		#	
		# Total number of rows is R = T * n^L * C(H,L)
		# Total number of candidate solutions is C(R,T)
		#
		#---------------------------------------------------------------------------------------------------------
		#  Solution (3) is a variation of (2), with the extra-constraint that no room can be selected twice for the same teacher. 
		#  There are 2 ways to obtain this:
		#	- either by tweaking the matrix-filling logic to generate room permutations with ** no ** repeats
		#	- or by adding extra-column in the matrix (better)
		#  Pass the 'sudoku' option to obtain this variation at runtime.
		#
		#  Columns:
		#
		#  | T Teacher cols | Room-to-hour cols (n x H): room for hour 1, ..., room for hour H [ | Room-to-teacher columns (n x T): rooms for t. 1, ..., room for t. T | ]
		#
		# For each row, we select 
		#	(1) - 
		#       (2) - 
		#
		# Steps:
		#  	- generate all permutations of L rooms, repeat allowed or not (room_lets)
		#       - generate all combinations of L hours (hour_lets)

		room_lets = self.n_permute_r( range(self.rooms), self.load, True)
		hours_worked = int(self.teachers * self.load / self.rooms)
		hour_lets = self.n_choose_r( range(hours_worked), self.load)


		teacher_schedules=[]
		for hour_let in hour_lets:
			for room_let in room_lets:
				teacher_schedules.append( [ (hour_let[h], room_let[h]) for h in range(self.load)] )


		matrix = []
		matrix_width = self.teachers + self.rooms * hours_worked

		if self.sudoku:
			matrix_width += self.rooms * self.teachers

		for t in range(self.teachers):
			for mts in  [ self.teacher_schedule_to_matrix_columns( ts, t if self.sudoku else -1 ) for ts in teacher_schedules ]:
				row = [ 0 for i in range( matrix_width ) ]
				row[t]=1
				for s in mts:
					row[s]=1
				matrix.append(row)
		#print(matrix)
		print("Exact cover matrix has {} rows".format( len(matrix)))
		self.matrix = matrix
			


	def teacher_schedule_to_matrix_columns(self, schedule, teacher ):
		""" Map a teacher schedule, i.e. a set of L pairs (<hour slot>, room), to the corresponding columns indices in the matrix.
		:param schedule: a list of pairs (<hour slot>, room)
		:type schedule: list
		:return: a list of matrix indices
		:rtype: list
		"""
		offset = self.teachers
		hours_worked = int(self.teachers * self.load / self.rooms)

		indices = []
		for pair in schedule:
			h = pair[0]
			r = pair[1]
			indices.append( offset + h * self.rooms + r )
			if self.sudoku and teacher > -1:
				indices.append( offset + hours_worked*self.rooms + teacher * self.rooms + r )
		return indices
			



	def solution_string(self, solution, solution_count=0):
		"""
		Return a human-readable solution of the problem.
		"""
		count = 0
		if solution_count > 0: count = solution_count
		solution_str_array = ["\n-----  Solution {}  ------".format(count)]
		for i in solution:
			if  i is None: break
			j = i.right
			nodes = [ int(i.column.name) ]
			while j is not i:
				nodes.append( int(j.column.name)  )
				j=j.right
			nodes.sort()
			solution_str_array.append( str([ self.matrix_col_to_grid(col) for col in nodes[:1 + self.load] ]))


		return '\n'.join( solution_str_array )

	def matrix_col_to_grid(self, col):
		""" Interpret the selected row """

		hours_worked=int(self.teachers*self.load/self.rooms)
		if col < self.teachers:
			return "T{}".format(col)
		return "H{}R{}".format( int((col-self.teachers)/self.rooms), (col-self.teachers)%self.rooms )

		
	@classmethod
	def n_choose_r(cls, n_set, r):
		""" Compute all r-subsets of n values

		:param n_set: set of values 
		:param r: number of elements in each combination
		:repeat: if True, repeats allowed (default: False)
		:type n_set: list
		:type r: int
		:type repeat: bool
		"""

		subsets = []

		def n_c_r_rec(i, r_let):
			# base case 1: r-let is complete
			if len(r_let)==r:
				subsets.append(r_let)
				return
			# base case 2: end of the list
			if i>=len(n_set):
				return
			# all branches that do contain the current element i
			n_c_r_rec(i+1, r_let + [ n_set[i] ] )
			# all branches that don't
			n_c_r_rec(i+1, r_let) 
		
		n_c_r_rec(0, [])

		return subsets

	@classmethod
	def n_permute_r(cls, n_set, r, repeat=False):
		""" Compute all r-permutations of n values.
		
		:param n_set: set of values 
		:param r: number of elements in each permutation
		:repeat: if True, repeats allowed (default: False)
		:type n_set: list
		:type r: int
		:type repeat: bool
		"""
		
		permutations = []

		def n_p_r_rec(i, r_let, used):
			if len(r_let)==r:
				permutations.append( r_let )
				return
			if i>len(n_set):
				return
			for j in n_set:
				if repeat or j not in used:
					n_p_r_rec(i+1, r_let + [j], used + [j])
		n_p_r_rec(0,[],[])

		return permutations
		






class WeeklySchedule_TestClass( unittest.TestCase):

		
	def test_n_choose_r_1(self):
		values = range(0, 10)


		self.assertEqual( len( WeeklySchedule.n_choose_r( values, 3 )), 120 )

	def test_n_permute_r(self):
		values = range(0, 10)
		self.assertEqual( len( WeeklySchedule.n_permute_r( values, 3)), 720 )
		self.assertEqual( len( WeeklySchedule.n_permute_r( values, 3, True)), 1000 )

	
	def test_weekly_schedule_normal(self):
		ws = WeeklySchedule(4,2,2)
		solution_count = ws.solve(4, True) 
		print('test_weekly_schedule_normal: WeeklySchedule(4,2,2) has {} solutions.'.format( solution_count))
		self.assertTrue( solution_count > 0)
	

	def test_weekly_schedule_sudoku(self):
		ws = WeeklySchedule(4,2,2, True)
		solution_count = ws.solve(4, True) 
		print('test_weekly_schedule_sudoku: WeeklySchedule(4,2,2) has {} solutions.'.format( solution_count))
		self.assertTrue( solution_count > 0)

	


def main():
        unittest.main()

if __name__ == '__main__':
        main()

