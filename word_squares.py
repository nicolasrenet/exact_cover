#!/usr/bin/python3
import exact_cover as dlx

dlx.LOGLEVEL=1

class WordSquare(dlx.ExactCover):
	""" On the last page of his "Dancing Links" article, D. Knuth briefly mentions his using the DLX algorithm to generate 3x3 word squares,
	without giving any details. The following is a solution to the problem."""
	
	
	ALPHABET_SIZE = 26

	def __init__(self, dictionary='dictionary.txt'):

		super().__init__()


		self.dictionary = [ word[:-1] for word in open(dictionary) ]

		self.build_matrix()
		self.build_links()


	def build_matrix(self):
		""" For each position, a letter is selected twice: once for the vertical word, once for the horizontal word. Since
		 the exact cover problem prevents us from selecting a letter-column twice, we use a trick: letters corresponding
		 to positions for vertical words are code _negatively_: 1s everywhere for the position, except for the letter in this position.
		
		 The matrix has the following structure:
		
		 n columns for the words IDs | 3 cols to code the square row | 3 cols to code the square col | 26 x 9 columns that code the letters for each of the 9 positions 
		 """


		size = len(self.dictionary)


		matrix_width = 6 + 9 * self.ALPHABET_SIZE
		print('matrix width = {}'.format( matrix_width ))

		matrix = []
		
		for w in range(len(self.dictionary)):
			
			row = [ 0 ] * matrix_width

			# transform word into list of codes
			letters = [ ord(c) - 97 for c in list( self.dictionary[w] ) ]

			# h positioning: 3 ways
			for h in (0, 1, 2):
				r = row[:]
				r[h]=1
				for l in (0, 1, 2):
					r[ 6 + self.ALPHABET_SIZE * (h*3 + l) + letters[l] ]=1
				matrix.append( r )

			for v in (0,1,2):
				r = row[:]
				r[3+v]=1

				square_positions = [ v + offset for offset in (0,3,6)]

				for l in (0,1,2):
				
					sp = square_positions[l]
					for matrix_col in range( 6 + self.ALPHABET_SIZE * sp, 6 + self.ALPHABET_SIZE * (sp+1)):
						r[matrix_col]=1
					r[ 6 + self.ALPHABET_SIZE * sp + letters[l]] = 0
				matrix.append( r )

		self.matrix=matrix	

					
		#print(self.matrix)			
		
			


	def solution_string(self, solution, solution_count=0):
		"""
		Return a human-readable solution of the problem.
		"""
		count = 0
		if solution_count > 0: count = solution_count
		solution_str_array = ["\n-----  Solution {}  ------".format(count)]
		for i in solution:
			if i is None: break
			j = i.right
			nodes = [ int(i.column.name) ]
			while j is not i:
				nodes.append( int(j.column.name)  )
				j=j.right
			nodes.sort()

			## add only those rows where either col 0, 1, or 2 is in the solution = horizontal words
			#if 0 in nodes or 1 in nodes or 2 in nodes:
			if nodes[0]<3:
				solution_str_array.append( ('R0' if nodes[0]==0 else ('R1' if nodes[0]==1 else 'R2')) + ''.join([ self.matrix_col_to_letter(col) for col in nodes[1:] ]))
				solution_str_array.sort()


		return '\n'.join( ''.join(r[2:]) for r in solution_str_array ) + '\n'


	def matrix_col_to_letter(self, col):
		return chr((col-6)%self.ALPHABET_SIZE+97)
	



ws = WordSquare('dictionary.txt')

ws.solve(6)

	

class Test_WordSquare( unittest.TestCase ):

	def test_word_square_1(self):	
		return True
