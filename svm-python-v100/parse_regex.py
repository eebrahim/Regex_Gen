'''
/***********************************************************************/
/*                                                                     */
/*   parse_regex.py                                                    */
/*                                                                     */
/*   Part of the algorithm for learning a model to predict a regular   */
/*   expression for a given batch.                                     */
/*                                                                     */
/*   Author: Paul Prasse                                               */
/*   Date: 14.09.2012                                                  */
/*                                                                     */
/*   Copyright (c) 2012  Paul Prasse - All rights reserved             */
/*                                                                     */
/*   This software is available for non-commercial use only. It must   */
/*   not be modified and distributed without prior permission of the   */
/*   author. The author is not responsible for implications from the   */
/*   use of this software.                                             */
/*                                                                     */
/***********************************************************************/
'''


import time

'''
require:	index determines the index of the quantor in string 'line'
			line is the regular expression
ensure:		returns the quantor wich is at the positon 'index' in the
			regular expression 'line'
'''
def find_append(index, line):
	for x in range(len(line) - (index + 1)):
		if line[index + x + 1] == ' ':
			continue
		elif line[index + x + 1] =='?':
			return line[index + 1:x+index + 2]
		elif line[index + x + 1] =='+':
			return line[index + 1:x+index + 2]
		elif line[index + x + 1] =='*':
			return line[index + 1:x+index + 2]
		elif line[index + x + 1] =='{':
			return find_in_brackets(3,index+x+1,line)
		else:
			return ''
	return ''
	
"""
'''
require:	regulare expression 'string'
ensure: 	delete grouping brackets (example ab([a-z]+)de -> ab[a-z]+de
'''
def delete_brackets(string):
	strg = str(string)
	if strg[0] == '(' and strg[1] == '(' and strg[len(strg) - 1] == ')':
		return strg[1:len(strg) -1]
	elif strg[0] == '(' and strg[1] == '[' and strg[len(strg) - 1] == ')' :
		return strg[1:len(strg) -1]
	else:
		return string
"""

'''
require:	a flag wich determines wich type of alternativ is used 'number'
				0: alternativ of the form (a|b|c)
				1: alternativ of the form [abc]
			a alternativ 'string'
ensure:		returns the string wich is in the alternativ
			(example [abc] -> abc)
'''
def get_in_brackets(number,string):
#	print 'number: ', number
#	print 'string: ', string
	if number == 0:
		idx = get_index_open(0,string)
		idx2 = get_index_close(0,string)
		countOpen 				= string[idx:idx2 + 1].count('(')
		countOpenSlash 			= string[idx:idx2 + 1].count('\(')
		countOpenSlashSlash 	= string[idx:idx2 + 1].count('\\\(')
		countClose				= string[idx:idx2 + 1].count(')')
		countCloseSlash			= string[idx:idx2 + 1].count('\)')
		countCloseSlashSlash	= string[idx:idx2 + 1].count('\\\)')
		while 	countOpen - (countOpenSlash - countOpenSlashSlash) != countClose - (countCloseSlash - countCloseSlashSlash):
			idx2 = idx2 + get_index_close(0,string[idx2 + 1:]) + 1
			countOpen 				= string[idx:idx2 + 1].count('(')
			countOpenSlash 			= string[idx:idx2 + 1].count('\(')
			countOpenSlashSlash 	= string[idx:idx2 + 1].count('\\\(')
			countClose				= string[idx:idx2 + 1].count(')')
			countCloseSlash			= string[idx:idx2 + 1].count('\)')
			countCloseSlashSlash	= string[idx:idx2 + 1].count('\\\)')
		return string[idx:idx2]
	elif number == 1:
	#	print 'number: ', number
	#	print 'string: ', string
		idx = string.find('[')
		idx2 = string.find(']')
		countOpen 				= string[idx:idx2 + 1].count('[')
		countOpenSlash 			= string[idx:idx2 + 1].count('\[')
		countOpenSlashSlash 	= string[idx:idx2 + 1].count('\\\[')
		countClose				= string[idx:idx2 + 1].count(']')
		countCloseSlash			= string[idx:idx2 + 1].count('\]')
		countCloseSlashSlash	= string[idx:idx2 + 1].count('\\\]')
	#	print 'eins: ', countOpen
	#	print 'zwei: ', countOpenSlash
	#	print 'drei: ', countOpenSlashSlash
	#	print 'vier: ', countClose
	#	print 'fuenf: ', countCloseSlash
	#	print 'sechs: ', countCloseSlashSlash
	#	print 'erg1: ', countOpen - (countOpenSlash - countOpenSlashSlash)
	#	print 'erg2: ', countClose - (countCloseSlash - countCloseSlashSlash)
		while 	countOpen - (countOpenSlash - countOpenSlashSlash) != countClose - (countCloseSlash - countCloseSlashSlash):
			idx2 = idx2 + get_index_close(1,string[idx2 + 1:]) + 1
			countOpen 				= string[idx:idx2 + 1].count('[')
			countOpenSlash 			= string[idx:idx2 + 1].count('\[')
			countOpenSlashSlash 	= string[idx:idx2 + 1].count('\\\[')
			countClose				= string[idx:idx2 + 1].count(']')
			countCloseSlash			= string[idx:idx2 + 1].count('\]')
			countCloseSlashSlash	= string[idx:idx2 + 1].count('\\\]')
		#	print 'string: ', string[idx:idx2 + 1]
		#	print 'eins: ', countOpen
		#	print 'zwei: ', countOpenSlash
		#	print 'drei: ', countOpenSlashSlash
		#	print 'vier: ', countClose
		#	print 'fuenf: ', countCloseSlash
		#	print 'sechs: ', countCloseSlashSlash
		#	print 'erg1: ', countOpen - (countOpenSlash - countOpenSlashSlash)
		#	print 'erg2: ', countClose - (countCloseSlash - countCloseSlashSlash)
		return string[idx + 1:idx2]

'''
require:	a flag wich determines wich type of alternativ we want to find
				0: alternativ of the form (a|b|c)
				1: alternativ of the form [abc]
			a regular expression 'string'
ensure:		returns the index of the first alternativ of the type 'number'
			in 'string'
'''
def get_index_open(number,string):
	begin = 0
	if number == 0:
		while True:
			b = string[begin:].find('(')
			if b == -1:
				return -1
			if b == 0:
				break
			else:
				if string[begin + b - 1] == '\\':
					begin = begin + b + 1
					continue
				else:
					break
		return b + begin
	elif number == 1:
		while True:
			b = string[begin:].find('[')
			if b == -1:
				return -1
			if b == 0:
				break
			else:
				if string[begin + b - 1] == '\\':
					begin = begin + b + 1
					continue
				else:
					break
		return b + begin
	
	
'''
require:	a flag wich determines wich type of alternativ we want to find
				0: alternativ of the form (a|b|c)
				1: alternativ of the form [abc]
			a regular expression 'string'
ensure:		returns the index of the closing bracket for the first 
			alternativ of the type 'number' in 'string'	
'''
def get_index_close(number,string):
	begin = 0
	if number == 0:
		while True:
			b = string[begin:].find(')')
			if b == -1:
				return -1
			if b == 0:
				break
			else:
				if string[begin + b - 1] == '\\':
					begin = begin + b + 1
					continue
				else:
					break
		return b + begin
	elif number == 1:
		while True:
			b = string[begin:].find(']')
			if b == -1:
				return -1
			if b == 0:
				break
			else:
				if string[begin + b - 1] == '\\':
					begin = begin + b + 1
					continue
				else:
					break
		return b + begin
					
# 0: (), 1: [], 2:\, 3:{}
'''
require:	a flag wich detemines what type of bracket 'number'
				0: ()
				1: []
				2: \
				3: {}
			the index of the beginnig of the bracket in the regular expression 'index'
			a regular expression 'line'
ensure:		returns the string incl. the brackets wich is at index 'index' and of type 'number'
			(example: (1,2,ab[abc]de) -> [abc])
'''
def find_in_brackets(number,index,line):
	count = 1
	for x in range(len(line) - index + 1):
		if number == 0:
			if line[x + index + 1] == '(':
				if line[x + index] != '\\':
					count = count + 1
			elif line[x + index + 1] == ')':
				if line[x + index] != '\\':
					count = count - 1			
			if count == 0:
				return line[index:x+index + 2] + find_append(index + x + 1, line)
				
		elif number == 1:
			if line[x + index + 1] == '[':
				if line[x + index] != '\\':
					count = count + 1
			elif line[x + index + 1] == ']':
				if line[x + index] != '\\':
					count = count - 1			
			if count == 0:				
				return line[index:x+index + 2] + find_append(index + x + 1, line)
				
		elif number == 2:
			if line[index] == '\\':
				return line[index:index + 2] + find_append(index + 1, line)				
		elif number == 3:
			if line[x + index + 1] == '{':
				count = count + 1
			elif line[x + index + 1] == '}':
				count = count - 1			
			if count == 0:
				return line[index:x+index + 2]


'''
require: 	regular expression 'string'
ensure:		returns the number of character '(' wich is not saved '\('
'''
def count_brackets(string):
	return string.count('(') - string.count('\\(')


if __name__ == "__main__":
	filename = '../../data/batches/regexp.TXT'
	for line in file(filename):
		print 'Hallo'
		for x in range(len(line)):
			#print 'du auch'
			if line[x] == '(':
				print find_in_brackets(0,x,line)
				s.add(find_in_brackets(0,x,line))
			elif line[x] == '[':
				print find_in_brackets(1,x,line)
				s.add(find_in_brackets(1,x,line))
			elif line[x] == '\\':
				print find_in_brackets(2,x,line)
				s.add(find_in_brackets(2,x,line))
		print 'noch mal distinct:'
		print s
		
