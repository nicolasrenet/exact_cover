#!/usr/bin/python3

import unittest
import time
import random
import exact_cover as dlx

dlx.LOGLEVEL=1

class WeeklySchedule( dlx.ExactCover ):

	def __init__(self, teachers=12, load=3, rooms=3):

		super().__init__()



		self.teachers=teachers
		self.load=load
		self.rooms=rooms

		self.build_matrix()
		self.build_links()
		
	 
		
	def build_matrix(self): 

		# A matrix of all possible ways for 12 teachers to teach 3 hours in 2 rooms
		#
		# Let 
		#	T = # teachers
		#	L = teaching (hours / teacher)
		#	n = # rooms
		#
		# Solution (1)
		#
		#  Idea: the matrix filling logic ensures that no teacher is assigned the same hour in 2 different room (no ubiquity!)
		#
		#  Columns:
		#
		# | ... T teacher columns ... | TL/n slots for room 1 | TL/n slots for room 2 | ... | TL/n slots for room n
		# 
		# A row represents a schedule assignment for 1 teacher, that choose 3 slots out of the (n x T x L) possible slots

		# For all teachers, only once:
		# 1) generate C(TL/n  L) L-combinations of slots actually worked
		# 2) generate all L-permutations of n rooms (repeats allowed)
		# 3) generate all L-tuples of pairs (hour slot, room)
		# For each teacher: 
		#  For each n-tuple:
		#    Create a row in the matrix

		#  Solution (2)
		#
		#  Idea: the matrix filling logic, but the matrix is larger; much of the work is shifted to the DLX algorithm.
		#
		#  Columns:
		#
		# | ... T Teacher columns ... | Room-to-teacher columns (n x T) | Hour-to-teacher columns (TL/n x T ) |
		#
		# For each row, we select 
		#	- L of the corresponding R-to-T columns (a choice of L room assignments, out of C(nT, L) possibilities
		#       - L of the corresponding H-to-T columns (a choice of L hour assignments, out of C(TL/n, L) possibilities
		#
		# Total: 12 + (3x12) + (12^2 * 3) / n 
		#
		# Difficulty: we must be able to select a room more than once for every teacher. The solution above would fit a narrower,
		# Sudoku-like definition of the problem, where no teacher must teach twice in the same classroom (that keeps them on the
		# edge, which should please the administrators).
		#
		# That could be solved with an even larger set of room-to-teacher columns: we would have T subsets of 
		# n^L columns. Each column in a subset would represent one way to assign L rooms (possibly the same) to a teacher
		#

		# solution (1)

		# hours open for business
		slots = int(self.teachers * self.load / self.rooms)
		slot_lets = self.n_choose_r( range(slots), self.load)
		room_lets = self.n_permute_r( range(self.rooms), self.load, True)

		teacher_schedules = []
		for slot_let in slot_lets:
			for room_let in room_lets:
				teacher_schedules.append( [ (slot_let[h],room_let[h]) for h in range(self.load) ] ) 

		
		matrix = []
		matrix_width= self.teachers + self.teachers * self.load 
		for mts in [ self.teacher_schedule_to_matrix_columns( ts ) for ts in teacher_schedules ]:
			for t in range(self.teachers):
				row = [ 0 for i in range( matrix_width ) ]
				row[t]=1
				for s in mts:
					row[s]=1
				matrix.append(row)
		#print(matrix)						
		self.matrix = matrix

	def teacher_schedule_to_matrix_columns(self, schedule ):
		""" Map a teacher schedule, i.e. a set of L pairs (<hour slot>, room), to the corresponding columns indices in the matrix.
		:param schedule: a list of pairs (<hour slot>, room)
		:type schedule: list
		:return: a list of matrix indices
		:rtype: list
		"""
		offset = self.teachers
		worked = int(self.teachers * self.load / self.rooms)
  
		indices = []
		for pair in schedule:
			indices.append( offset + pair[1]*worked + pair[0])
		#print(indices)
		return indices


	def n_choose_r(self, n_set, r):
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

	def n_permute_r(self, n_set, r, repeat=False):
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
			solution_str_array.append( str([ self.matrix_col_to_grid(col) for col in nodes ]))


		return '\n'.join( solution_str_array )

	def matrix_col_to_grid(self, col):
		""" Interpret the selected row """

		hours_worked=int(self.teachers*self.load/self.rooms)
		if col < self.teachers:
			return "T{}".format(col)
		room = int( (col-self.teachers)/hours_worked )
		hour = (col-self.teachers)%hours_worked
		return "H{}R{}".format(hour, room)


class WeeklyScheduleSudoku( WeeklySchedule ):

	def __init__(self, teachers=12, load=3, rooms=3, sudoku=False):

		self.sudoku = sudoku
		
		super().__init__(teachers, load, rooms)
		

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
		#
		#  Solution (2) It is a cleaner implementation of solution (1): relax constraint on room/teacher, while ensuring that no teacher teaches in 2 rooms at the same hour, but this time enforced by the matrix
		#
		#  Columns:
		#
		#  | T Teacher cols |  Room-to-hour columns (n x H): rooms for H1, rooms for H2, ..., rooms for HH
		#
		# For each row, we select 
		#       (1) - L of the corresponding R-to-H columns: a choice of 1 room (out of n) for everyone of the L hours (out of H hours) -> this ensures that hours are assigned to teachers, as well as rooms, and no
		#
		# Steps:
		#  	- generate all permutations of L rooms, repeat allowed (room_lets)
		#       - generate all combinations of L hours (hour_lets)
		#	- form sets of pairs (room, hour)
		#	- populate the matrix accordingly


		room_lets = self.n_permute_r( range(self.rooms), self.load, not self.sudoku )
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
			for mts in  [ self.teacher_schedule_to_matrix_columns( ts, -1 ) for ts in teacher_schedules ]:
				row = [ 0 for i in range( matrix_width ) ]
				row[t]=1
				for s in mts:
					row[s]=1
				matrix.append(row)
		#print(matrix)
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
				indices.append( offset + hours_worked + teacher * self.rooms + r )
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
			solution_str_array.append( str([ self.matrix_col_to_grid(col) for col in nodes ]))


		return '\n'.join( solution_str_array )

	def matrix_col_to_grid(self, col):
		""" Interpret the selected row """

		hours_worked=int(self.teachers*self.load/self.rooms)
		if col < self.teachers:
			return "T{}".format(col)
		return "H{}R{}".format( int((col-self.teachers)/self.rooms), (col-self.teachers)%self.rooms )


		#---------------------------------------------------------------------------------------------------------
		#  Solution (3) It is a sudoku-like problem, where we cannot select an hour-col twice for the same teacher, 
		#  but cannot select a room-col twice for the same teacher either
		#
		#  Columns:
		#
		#  | T Teacher cols | Room-to-teacher cols (n x T) | Room-to-hour columns (n x H) 
		#
		# For each row, we select 
		#	(1) - L of the corresponding R-to-T columns: a choice of L room assignments = C(n, L) possibilities
		#       (2) - L of the corresponding R-to-H columns: a choice of 1 room (out of n) for everyone of the L hours (out of H hours) -> this ensures that hours are assigned to teachers, as well as rooms, and no
		#
		# Steps:
		#  	- generate all permutations of L rooms, no repeat allowed (room_lets)
		#       - generate all combinations of L hours (hour_lets)
		#       - 

#ws = WeeklyScheduleSudoku(4,2,2)
ws = WeeklyScheduleSudoku(12,3,3,False)


start = time.time()
ws.solve(12)
#print("Time elapsed: {}mn".format( (time.time() - start)//60))






class WeeklySchedule_TestClass( unittest.TestCase):

		
	def test_n_choose_r_1(self):
		values = range(0, 10)


		ws = WeeklySchedule()
		self.assertEqual( len( ws.n_choose_r( values, 3 )), 120 )

	def test_n_permute_r(self):
		values = range(0, 10)
		ws=WeeklySchedule()
		self.assertEqual( len( ws.n_permute_r( values, 3)), 720 )
		self.assertEqual( len( ws.n_permute_r( values, 3, True)), 1000 )

	
	def atest_known_solution(self):
		# construct the matrix of a know solution
		summary = (
			(15,16,17,18,19),
			(26,36,37,38,48),
			(61,68,69,70,71),
			(12,13,22,32,33),
			(14,23,24,25,34),
			(41,50,51,59,60),
			(20,21,30,31,40),
			(47,57,58,66,67),
			(55,56,63,64,65),
			(42,52,53,54,62),
			(27,28,29,39,49),
			(35,43,44,45,56))

		matrix = [ [ 0 for j in range(72) ] for i in range(12) ]

		
		row=0
		for idx in range(len(summary)):
			matrix[row][idx]=1
			for pos in summary[idx]:
				matrix[row][pos]=1
			row += 1
		
		def junk_row():
			new_row = [0] * 72
			index_pool = list( range(0,72) )
			for  i in range(5):
				idx = random.randint(0,len(index_pool)-1)
				new_row[idx]=1
				index_pool.pop(idx)
			return new_row
				
		for junk in range(0):
			new_pos = random.randint(0,len(matrix)-1)
			matrix.insert( new_pos, junk_row())

		
		print_matrix(matrix,12,72)

		lists = build_links( matrix )	

		solution = [None for i in range(12) ]
		search(0, lists, solution)
		print(solution)
		print_solution(solution)

	


def main():
        unittest.main()

if __name__ == '__main__':
        main()

