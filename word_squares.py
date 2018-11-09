#!/usr/bin/python3
import exact_cover as dlx
import unittest

dlx.LOGLEVEL=1

class WordSquare(dlx.ExactCover):
	""" On the last page of his "Dancing Links" article, D. Knuth briefly mentions his using the DLX algorithm to generate 3x3 word squares,
	without giving any details. The following is a solution to the problem.
	
	This version satisfies the diagonal constraint.
	"""
	
	
	def __init__(self, dictionary='dictionary.txt', square_size=3, alphabet_size=26):

		super().__init__()

		if type(dictionary) is str:
			with open(dictionary) as d:
				self.dictionary = [ word[:-1] for word in d ]
		else:
			self.dictionary = dictionary
		self.square_size = square_size
		self.alphabet_size = alphabet_size
		self.diagonal_width = 2*self.square_size*self.alphabet_size

		self.build_matrix()
		self.build_links()


	def build_matrix(self):
		""" For each position, a letter is selected twice: once for the vertical word, once for the horizontal word. Since
		 the exact cover problem prevents us from selecting a letter-column twice, we use a trick: letters corresponding
		 to positions for vertical words are code _negatively_: 1s everywhere for the position, except for the letter in this position.
		
		 The matrix has the following structure:
		
		 		| N cols to code the square row 
				| N cols to code the square col 
				| 2 cols to code the square diagonal
				| 26 x N^2 columns that code the letters for each of the 9 positions 
				| 26 x  2N [ 2N-1 if n odd ] columns that code the letters for each of the 5 diagonal positions: each horizontal word sets them with 1s,
					each diagonal word set them with 0s
						
		 """



		size = len(self.dictionary)
		
		row = 0
		matrix2word=[]

		
		hor_vert_diag_width = self.square_size * 2 + 2
		positions_col_width =  (self.square_size ** 2) * self.alphabet_size
		matrix_width = hor_vert_diag_width  + positions_col_width + self.diagonal_width
		

		
		print('matrix width = {}, square size = {}'.format( matrix_width, self.square_size ))

		vertical_offsets = list( map(lambda x: x*self.square_size, range(self.square_size)) )

		matrix = []
		
		for w in range(len(self.dictionary)):

			#print(self.dictionary[w])
			
			row = [ 0 ] * matrix_width

			# transform word into list of codes
			letters = [ ord(c) - 97 for c in list( self.dictionary[w] ) ]

			# horizontal positioning
			n = self.square_size
			for h in range(n):
				r = row[:]
				r[h]=1
				for l in range(n):
					r[ hor_vert_diag_width + self.alphabet_size * (h*n + l) + letters[l] ]=1
					
					# setting diagonal positions
					diag_pos = self.horizontal_to_diagonal_column(n, h, l)
					#print('Diagonal col = {}'.format(diag_pos))
					if diag_pos is not None:
						#if h==0: print('{}:H0:{}'.format(self.dictionary[w],  hor_vert_diag_width  + positions_col_width + diag_pos*self.alphabet_size + letters[l] ))
						r[ hor_vert_diag_width  + positions_col_width + diag_pos*self.alphabet_size + letters[l] ]=1

				matrix.append( r )
				matrix2word.append((self.dictionary[w], 'H{}'.format(h), str(r).translate({ord(c): None for c in ' ,'})))

			# vertical positioning
			for v in range(n):
				r = row[:]
				r[n + v]=1

				square_positions = [ v + offset for offset in vertical_offsets ]

				for l in range(n):
				
					# negative coding
					sp = square_positions[l]
					for matrix_col in range( hor_vert_diag_width + self.alphabet_size * sp, hor_vert_diag_width + self.alphabet_size * (sp+1)):
						r[matrix_col]=1
					r[ hor_vert_diag_width + self.alphabet_size * sp + letters[l]] = 0

					# set middle position in positive (for up diagonal match)
					if n%2>0 and v==n//2 and v==l:
						r[ hor_vert_diag_width  + positions_col_width + (n+n//2)*self.alphabet_size + letters[l] ] = 1
				matrix.append( r )
				matrix2word.append((self.dictionary[w], 'V{}'.format(v), str(r).translate({ord(c): None for c in ' ,'})))

			# diagonal placement
			for d in (0,1):
				r = row[:]
				r[n*2+d]=1
				
				for l in range(n):
					dp = self.diagonal_to_diagonal_column(n, d, l)
					for pos in range( hor_vert_diag_width  + positions_col_width + dp*self.alphabet_size,
							hor_vert_diag_width  + positions_col_width + (dp+1)*self.alphabet_size):
						r[pos]=1
					r[ hor_vert_diag_width  + positions_col_width + dp*self.alphabet_size + letters[l] ]=0
				#print(r)
				# TODO: negatives
				matrix.append(r)
				matrix2word.append((self.dictionary[w], 'D{}'.format(d), str(r).translate({ord(c): None for c in ' ,'})))

		for i in matrix2word:
			print(i)

		#dlx.log(self.condense_matrix(matrix), 3)

		self.matrix=matrix	



	@classmethod
	def diagonal_to_diagonal_column(cls, n, updown, letter):
		if updown==0: 
			return letter
		return n+letter

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
				solution_str_array.append( 'R' + str(nodes[0]) + ''.join([ self.matrix_col_to_letter(col) for col in nodes[1:self.square_size+1] ]))
				solution_str_array.sort()

		return '\n'.join( ''.join(r[2:]) for r in solution_str_array ) + '\n'


	def matrix_col_to_letter(self, col):
		return chr((col-self.square_size*2-2)%self.alphabet_size+97)
	
	

#ws = WordSquare('dictionary_3_letter_words.txt', 3)

#ws.solve(8)

	
	@classmethod
	def horizontal_to_diagonal_column(cls, n, row, letter):
		"""
		For a given row and word position, return the diagonal column numbers
		set.

		
 		Assume following numbering:

		0	0       9     	0	0     7  
		1	  1   8		1	  1 6
		2	   2/7		2	  5 2
		3	  6   3		3	4     3
		4	5	4		

		:return: a column number
		:rtype: tuple
		"""
		if letter==row: return row
		if letter==n-row-1:
			return n+letter
		return None
		

class Test_WordSquare( unittest.TestCase ):
	
	def test_horizontal_to_diagonal_column_even_row_1_400(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(4,0,0), 0)
	def test_horizontal_to_diagonal_column_even_row_1_401(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(4,0,1), None)
	def test_horizontal_to_diagonal_column_even_row_1_402(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(4,0,2), None)
	def test_horizontal_to_diagonal_column_even_row_1_403(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(4,0,3), 7)
		

	def test_horizontal_to_diagonal_column_even_row_2_410(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(4,1,0), None)
	def test_horizontal_to_diagonal_column_even_row_2_411(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(4,1,1), 1)
	def test_horizontal_to_diagonal_column_even_row_2_412(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(4,1,2), 6)
	def test_horizontal_to_diagonal_column_even_row_2_413(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(4,1,3), None)
		
	def test_horizontal_to_diagonal_column_even_row_4_430(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(4,3,0), 4)
	def test_horizontal_to_diagonal_column_even_row_4_431(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(4,3,1), None)
	def test_horizontal_to_diagonal_column_even_row_4_432(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(4,3,2), None)
	def test_horizontal_to_diagonal_column_even_row_4_433(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(4,3,3), 3)
		

	def test_horizontal_to_diagonal_column_odd_row_1_500(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,0,0), 0)
	def test_horizontal_to_diagonal_column_odd_row_1_501(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,0,1), None)
	def test_horizontal_to_diagonal_column_odd_row_1_502(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,0,2), None)
	def test_horizontal_to_diagonal_column_odd_row_1_503(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,0,3), None)
	def test_horizontal_to_diagonal_column_odd_row_1_504(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,0,4), 9)
		

	def test_horizontal_to_diagonal_column_odd_row_2_510(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,1,0), None)
	def test_horizontal_to_diagonal_column_odd_row_2_511(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,1,1), 1)
	def test_horizontal_to_diagonal_column_odd_row_2_512(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,1,2), None)
	def test_horizontal_to_diagonal_column_odd_row_2_513(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,1,3), 8)
	def test_horizontal_to_diagonal_column_odd_row_2_514(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,1,4), None)
		
	def test_horizontal_to_diagonal_column_odd_row_3_520(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,2,0), None)
	def test_horizontal_to_diagonal_column_odd_row_3_521(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,2,1), None)
	def test_horizontal_to_diagonal_column_odd_row_3_522(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,2,2), 2)
	def test_horizontal_to_diagonal_column_odd_row_3_523(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,2,3), None)
	def test_horizontal_to_diagonal_column_odd_row_3_524(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,2,4), None)
		
	def test_horizontal_to_diagonal_column_odd_row_4_530(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,3,0), None)
	def test_horizontal_to_diagonal_column_odd_row_4_531(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,3,1), 6)
	def test_horizontal_to_diagonal_column_odd_row_4_532(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,3,2), None)
	def test_horizontal_to_diagonal_column_odd_row_4_533(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,3,3), 3)
	def test_horizontal_to_diagonal_column_odd_row_4_534(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,3,4), None)
		

	def test_horizontal_to_diagonal_column_odd_row_5_540(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,4,0), 5)
	def test_horizontal_to_diagonal_column_odd_row_5_541(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,4,1), None)
	def test_horizontal_to_diagonal_column_odd_row_5_542(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,4,2), None)
	def test_horizontal_to_diagonal_column_odd_row_5_543(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,4,3), None)
	def test_horizontal_to_diagonal_column_odd_row_5_544(self):
		self.assertEqual( WordSquare.horizontal_to_diagonal_column(5,4,4), 4)
		

	def test_diagonal_to_diagonal_column_even_row_1_400(self):
		self.assertEqual( WordSquare.diagonal_to_diagonal_column(4,0,0), 0)
	def test_diagonal_to_diagonal_column_even_row_1_401(self):
		self.assertEqual( WordSquare.diagonal_to_diagonal_column(4,0,1), 1)
	def test_diagonal_to_diagonal_column_even_row_1_402(self):
		self.assertEqual( WordSquare.diagonal_to_diagonal_column(4,0,2), 2)
	def test_diagonal_to_diagonal_column_even_row_1_403(self):
		self.assertEqual( WordSquare.diagonal_to_diagonal_column(4,0,3), 3)
		

	def test_diagonal_to_diagonal_column_even_row_1_410(self):
		self.assertEqual( WordSquare.diagonal_to_diagonal_column(4,1,0), 4)
	def test_diagonal_to_diagonal_column_even_row_1_411(self):
		self.assertEqual( WordSquare.diagonal_to_diagonal_column(4,1,1), 5)
	def test_diagonal_to_diagonal_column_even_row_1_412(self):
		self.assertEqual( WordSquare.diagonal_to_diagonal_column(4,1,2), 6)
	def test_diagonal_to_diagonal_column_even_row_1_413(self):
		self.assertEqual( WordSquare.diagonal_to_diagonal_column(4,1,3), 7)
		
	def test_diagonal_to_diagonal_column_odd_row_1_500(self):
		self.assertEqual( WordSquare.diagonal_to_diagonal_column(5,0,0), 0)
	def test_diagonal_to_diagonal_column_odd_row_1_501(self):
		self.assertEqual( WordSquare.diagonal_to_diagonal_column(5,0,1), 1)
	def test_diagonal_to_diagonal_column_odd_row_1_502(self):
		self.assertEqual( WordSquare.diagonal_to_diagonal_column(5,0,2), 2)
	def test_diagonal_to_diagonal_column_odd_row_1_503(self):
		self.assertEqual( WordSquare.diagonal_to_diagonal_column(5,0,3), 3)
	def test_diagonal_to_diagonal_column_odd_row_1_504(self):
		self.assertEqual( WordSquare.diagonal_to_diagonal_column(5,0,4), 4)
		
	def test_diagonal_to_diagonal_column_odd_row_1_510(self):
		self.assertEqual( WordSquare.diagonal_to_diagonal_column(5,1,0), 5)
	def test_diagonal_to_diagonal_column_odd_row_1_511(self):
		self.assertEqual( WordSquare.diagonal_to_diagonal_column(5,1,1), 6)
	def test_diagonal_to_diagonal_column_odd_row_1_512(self):
		self.assertEqual( WordSquare.diagonal_to_diagonal_column(5,1,2), 7)
	def test_diagonal_to_diagonal_column_odd_row_1_513(self):
		self.assertEqual( WordSquare.diagonal_to_diagonal_column(5,1,3), 8)
	def test_diagonal_to_diagonal_column_odd_row_1_514(self):
		self.assertEqual( WordSquare.diagonal_to_diagonal_column(5,1,4), 9)
		

	def test_word_square_1(self):	
		""" Testing with tiny dictionary: 4-letter words, on 7-letter alphabet  """
		dictionary = ('abed','aced','aged','babe','bade','bead','beef','cafe','cage','cede',
				'dead','deaf','deed','edge','face','fade','feed','gaff','gage','geed',
				'aegd','dddd')
		ws = WordSquare( dictionary, 4, 7)  
		self.assertEqual( ws.solve(10), 4 )

	def test_word_square_2(self):
		dictionary = ('ate','win','led','aid','lie','awl','tie','end','bed','oar','wry','bow','ear','dry','bay','wad')
		ws = WordSquare( dictionary, 3, 26)
		self.assertEqual( ws.solve(8), 2)


	def test_word_square_3(self):
		dictionary = 'dictionary_3_letter_words.txt'
		ws = WordSquare( dictionary, 3, 26)
		self.assertEqual( ws.solve(8), 2)




	


def main():
        unittest.main()

if __name__ == '__main__':
        main()

