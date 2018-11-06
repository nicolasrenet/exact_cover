#!/usr/bin/python3
import exact_cover as dlx
import unittest

dlx.LOGLEVEL=1

class WordSquare(dlx.ExactCover):
	""" On the last page of his "Dancing Links" article, D. Knuth briefly mentions his using the DLX algorithm to generate 3x3 word squares,
	without giving any details. The following is a solution to the problem."""
	
	
	def __init__(self, dictionary='dictionary.txt', square_size=3, alphabet_size=26):

		super().__init__()

		if type(dictionary) is str:
			self.dictionary = [ word[:-1] for word in open(dictionary) ]
		else:
			self.dictionary = dictionary
		self.square_size = square_size
		self.alphabet_size = alphabet_size

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


		
		hor_vert_width = self.square_size * 2
		matrix_width = hor_vert_width  + (self.square_size ** 2) * self.alphabet_size
		
		print('matrix width = {}, square size = {}'.format( matrix_width, self.square_size ))

		vertical_offsets = list( map(lambda x: x*self.square_size, range(self.square_size)) )

		matrix = []
		
		for w in range(len(self.dictionary)):

			#print(self.dictionary[w])
			
			row = [ 0 ] * matrix_width

			# transform word into list of codes
			letters = [ ord(c) - 97 for c in list( self.dictionary[w] ) ]

			# h positioning: 3 ways
			for h in range(self.square_size):
				r = row[:]
				r[h]=1
				for l in range(self.square_size):
					r[ hor_vert_width + self.alphabet_size * (h*self.square_size + l) + letters[l] ]=1
				matrix.append( r )

			for v in range(self.square_size):
				r = row[:]
				r[self.square_size + v]=1

				square_positions = [ v + offset for offset in vertical_offsets ]

				for l in range(self.square_size):
				
					sp = square_positions[l]
					for matrix_col in range( hor_vert_width + self.alphabet_size * sp, hor_vert_width + self.alphabet_size * (sp+1)):
						r[matrix_col]=1
					r[ hor_vert_width + self.alphabet_size * sp + letters[l]] = 0
				matrix.append( r )

		dlx.log(self.condense_matrix(matrix), 3)

		self.matrix=matrix	


	def condense_matrix(self, matrix):
		""" Condense the matrix, for easier console display. 

		:return: the matrix value, in condensed form
		:rtype: str
		"""
		return  str(matrix)[1:-1].translate({ord(c): None for c in ' ,'})
			


	def solution_string(self, solution, solution_count=0):
		"""
		Return a human-readable solution of the problem.
		:rtype: str
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
			if nodes[0]<self.square_size:
				solution_str_array.append( 'R' + str(nodes[0]) + ''.join([ self.matrix_col_to_letter(col) for col in nodes[1:] ]))
				solution_str_array.sort()


		return '\n'.join( ''.join(r[2:]) for r in solution_str_array ) + '\n'


	def matrix_col_to_letter(self, col):
		return chr((col-self.square_size*2)%self.alphabet_size+97)
	



#ws = WordSquare('dictionary_5_letter_words.txt', 5)

#ws.solve(10)

	

class Test_WordSquare( unittest.TestCase ):

	def test_word_square_1(self):	
		""" Testing with tiny dictionary: 3-letter words, on 7-letter alphabet  """
		dictionary = ('abed','aced','aged','babe','bade','bead','beef','cafe','cage','cede',
				'dead','deaf','deed','edge','face','fade','feed','gaff','gage','geed')
		ws = WordSquare( dictionary, 4, 7)  
		self.assertEqual( ws.solve(8), 2 )





	


def main():
        unittest.main()

if __name__ == '__main__':
        main()

