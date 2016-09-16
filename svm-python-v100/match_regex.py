'''
/***********************************************************************/
/*                                                                     */
/*   match_regex.py                                                    */
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

import re, os, time

import parse_regex
	

filename = 'macro_definition.txt'

"""
'''
require:	
ensure:		
'''
def reduce_regex(regex, list):
	print 'list in reduce: ', list
	print '\n\nregex: ', regex
	count1 = regex.count('([')
	count2 = regex.count('|[')
	count = count1 + count2
	begin = 0
	list_regex = []
	for a in range(count):
		idx = regex[begin:].find('([')
		if idx == -1:
			idx = regex[begin:].find('|[')
		in_brackets = parse_regex.find_in_brackets(1,idx + 1,regex)
		list_regex.append(in_brackets)
		begin += idx + 1
	neu_list = []
	#print 'list_regex: ', list_regex
	for a in range(len(list)):
		#print list[a]
		aa = 0
		for b in range(len(list_regex)):
			c1 = re.compile(list_regex[b])
			#print list_regex[b]
			m = c1.match(list[a])
			if m and m.group(0) == list[a]:
				#print list[a]
				aa = 1
		if aa == 0: neu_list.append(list[a])
	#print 'neu_list: ',  neu_list
	ret = '('
	for a in range(len(list_regex) - 1):
		ret = ret + list_regex[a] + '|'
	if len(list_regex) >= 1:
		ret = ret + list_regex[len(list_regex) - 1]
	for a in range(len(neu_list) - 1):
		ret = ret + '|' + neu_list[a]
	if len(neu_list) >= 1:
		ret = ret + '|' + neu_list[len(neu_list) - 1]
	ret = ret + ')'
	if len(list_regex) == 0: ret = ret.replace('(|','(')
	if ret == '()': ret = regex
	print 'return: ', ret, '\n\n\n '
	print allo
	return ret
"""		

'''
require:	regex is a regular expression
ensure:		returns a tuple (list,groupedRegex,stringlist)
			list: is a list wich contains the numbers of the '(' wich are used to group
			groupedRegex: is a grouped regex, where the alternatives of depth 1 are in brackets
			stringlist: is a list of the strings between the alternatives
		example: ab(ab|cd)cd[Ii] -> ([1,3], ab((ab|cd))cd([Ii]))
'''
def calculate_match_regex(regex, flagReplace = True):
	macroList = getMacroList()
	#start = time.time()
	stringlist = []
	output = ''
	outputMacro = ''
	list = []
	listMacro = []
	stopper = 0
	begin = 0
	for x in range(len(regex)):
		if stopper > 0:
			stopper = stopper - 1
			continue
		#print 'an stelle ', x, ' ist ', regex[x]
		if (regex[x] == '(' and x == 0) or (regex[x] == '(' and x > 0 and regex[x - 1] != '\\'):
#			print 'x: ', regex[x]
#			print 'x - 1', regex[x-1]
#			print 'ab: ', regex[x:x+20]
			in_brackets = parse_regex.find_in_brackets(0,x,regex)
#			print 'INBRACKETS: ', in_brackets
			len_with_brackets = len(in_brackets)
			#print 'Laenge', len_with_brackets, ' ', in_brackets
			stopper = len_with_brackets - 1				
			list.append(int(parse_regex.count_brackets(output + regex[begin:x]) + 1))	
			listMacro.append(int(parse_regex.count_brackets(outputMacro + regex[begin:x]) + 1))	
			output = output + regex[begin:x] + '(' + in_brackets + ')'
			outputMacro = outputMacro + regex[begin:x] + '(' + in_brackets + ')'
			stringlist.append(regex[begin:x])
			#print regex[begin:x], 'list ', list		
			begin = x + len_with_brackets
		if (regex[x] == '[' and x == 0) or (regex[x] == '[' and x > 0 and regex[x - 1] != '\\'):
			in_brackets = parse_regex.find_in_brackets(1,x,regex)
			len_with_brackets = len(in_brackets)
			#print 'Laenge', len_with_brackets, ' ', in_brackets
			stopper = len_with_brackets - 1				
			list.append(int(parse_regex.count_brackets(output + regex[begin:x]) + 1))
			listMacro.append(int(parse_regex.count_brackets(outputMacro + regex[begin:x]) + 1))		
			output = output + regex[begin:x] + '(' + in_brackets + ')'
			outputMacro = outputMacro + regex[begin:x] + '(' + in_brackets + ')'
			stringlist.append(regex[begin:x])
			#print regex[begin:x], 'list ', list		
			begin = x + len_with_brackets
		if (regex[x] == '$' and x == 0) or (regex[x] == '$' and x > 0 and regex[x - 1] != '\\') and regex[x + 1] == '{':
			macro = regex[x:x + regex[x:].find('}') + 1]
			# search wich macro is used
			for a in range(len(macroList)):
				if macro == macroList[a][0]:
					replaceRegex = macroList[a][1]
					if replaceRegex[len(replaceRegex) - 1] == '\n':
						replaceRegex = replaceRegex[0:len(replaceRegex)-1]
					break					
			in_brackets = replaceRegex
#			print 'ersetze: ', replaceRegex
			len_with_brackets = len(macro)
			stopper = len_with_brackets - 1				
			list.append(int(parse_regex.count_brackets(output + regex[begin:x]) + 1))	
			listMacro.append(int(parse_regex.count_brackets(outputMacro + regex[begin:x]) + 1))	
			output = output + regex[begin:x] + '(' + in_brackets + ')'
			outputMacro = outputMacro + regex[begin:x] + '(' + macro + ')'
			stringlist.append(regex[begin:x])
			#print regex[begin:x], 'list ', list		
			begin = x + len_with_brackets
			#print allo
		if regex[x] == '\\':
			# saved characters
			if regex[x + 1] == '"' or regex[x + 1] == '.' or regex[x + 1] == '?' or regex[x + 1] == '!' or regex[x + 1] == '$' or regex[x + 1] == '@' or regex[x +1] == '(' or regex[x +1] == ')' or regex[x +1] == '[' or regex[x +1] == ']' or regex[x + 1] == 'n' or regex[x + 1] == 't' or regex[x + 1] == '+' or regex[x + 1] == '-' or regex[x + 1] == '^' or regex[x + 1] == 'x' or regex[x + 1] == '\\' or regex[x + 1] == '*':
				continue
			in_brackets = parse_regex.find_in_brackets(2,x,regex)
			len_with_brackets = len(in_brackets)
			macroOutput = in_brackets
#			print 'IN_Brackets: ', in_brackets
			# unfold macros
			if (flagReplace):
				if in_brackets == '\\l':
					in_brackets = '[\r]?'
				if in_brackets == '\\l*':
					in_brackets = '[\r\n]*'
				if in_brackets == '\\l+':
					in_brackets = '[\r\n]+'
				if in_brackets == '\\e+':
					in_brackets = '[\w._\-\'#+]+'	
				if in_brackets == '\\e':
					in_brackets = '[\w._\-\'#+]'	
				if in_brackets == '\\u+':
					in_brackets = '[\w_\.\-]+'
			#print 'Laenge', len_with_brackets, ' ', in_brackets
			stopper = len_with_brackets - 1				
			list.append(int(parse_regex.count_brackets(output + regex[begin:x]) + 1))
			listMacro.append(int(parse_regex.count_brackets(outputMacro + regex[begin:x]) + 1))	
			output = output + regex[begin:x] + '(' + in_brackets + ')'
#			print 'neuer Output: ', output
			outputMacro = outputMacro + regex[begin:x] + '(' + macroOutput + ')'
#			print 'Macro Output: ', outputMacro
			stringlist.append(regex[begin:x])
			#print regex[begin:x], 'list ', list		
			begin = x + len_with_brackets 
	output = output + regex[begin:]
	outputMacro = outputMacro + regex[begin:]
	stringlist.append(regex[begin:])
	#print 'Zeit fuer calculate_match_regex: ', time.time() - start
	return (list, output,stringlist,listMacro, outputMacro)
			

'''
	calculate coherent regex: ((a|b)+)([abc]) -> ((a|b)+[abc])
'''
def calculateCoherentRegex(regex):
	macroList = getMacroList()
	#start = time.time()
	stringlist = []
	output = ''
	outputMacro = ''
	list = []
	listMacro = []
	stopper = 0
	begin = 0
	for x in range(len(regex)):
		if stopper > 0:
#			print 'skippe: ', regex[x]
			stopper -= 1
			continue
		reg,start,stopper = getNextCoherentRegex(regex[x:])
		stopper = stopper + start
#		print 'REEEEGGGG: ', reg
		while True:
			nextReg,nextStart,nextStopper = getNextCoherentRegex(regex[x + stopper:])
			if nextStart == 1 and nextReg != 'DUMMY':
				reg = reg + nextReg
				stopper = stopper + nextStopper + 1
#				start = start + nextStart
			else:
#				print 'break weg: ', nextReg, 'nextStart: ', nextStart
				break		
		if reg != 'DUMMY':
#			print 'vorstring: ', regex[begin:x + start]
			list.append(int(parse_regex.count_brackets(output + regex[begin:x + start]) + 1))
			output = output + regex[begin:x + start] + '(' + reg + ')'			
			begin = x + stopper + 1
#			print 'reg: ', reg
#	print output, list
	return (list, output)

'''
calculate the next complex subexpression
'''
def getNextCoherentRegex(regex):
	macroList = getMacroList()
	output = ''
	start = 0
	for x in range(len(regex)):
		if (regex[x] == '(' and x == 0) or (regex[x] == '(' and x > 0 and regex[x - 1] != '\\'):
			in_brackets = parse_regex.find_in_brackets(0,x,regex)
			len_with_brackets = len(in_brackets)
			start = x
			stopper = len_with_brackets - 1	
			return in_brackets,start,stopper
		if regex[x] == '\\':
			# saved characters
			if regex[x + 1] == '"' or regex[x + 1] == '.' or regex[x + 1] == '?' or regex[x + 1] == '!' or regex[x + 1] == '$' or regex[x + 1] == '@' or regex[x +1] == '(' or regex[x +1] == ')' or regex[x +1] == '[' or regex[x +1] == ']' or regex[x + 1] == 'n' or regex[x + 1] == 't' or regex[x + 1] == '+' or regex[x + 1] == '-' or regex[x + 1] == '^' or regex[x + 1] == 'x' or regex[x + 1] == '\\':
				continue
			in_brackets = parse_regex.find_in_brackets(2,x,regex)
			len_with_brackets = len(in_brackets)
			stopper = len_with_brackets - 1	
			if in_brackets == '\\l':
				in_brackets = '[\r]?'
			if in_brackets == '\\l*':
				in_brackets = '[\r\n]*'
			if in_brackets == '\\l+':
				in_brackets = '[\r\n]+'
			if in_brackets == '\\e+':
				in_brackets = '[\w._\-\'#+]+'	
			if in_brackets == '\\e':
				in_brackets = '[\w._\-\'#+]'	
			if in_brackets == '\\u+':
				in_brackets = '[\w_\.\-]+'
			start = x
			return in_brackets, start, stopper
		if (regex[x] == '$' and x == 0) or (regex[x] == '$' and x > 0 and regex[x - 1] != '\\') and regex[x + 1] == '{':
			macro = regex[x:x + regex[x:].find('}') + 1]
			# search wich macro is used
			for a in range(len(macroList)):
				if macro == macroList[a][0]:
					replaceRegex = macroList[a][1]
					if replaceRegex[len(replaceRegex) - 1] == '\n':
						replaceRegex = replaceRegex[0:len(replaceRegex)-1]
					break					
			in_brackets = replaceRegex
#			print 'ersetze: ', replaceRegex
			len_with_brackets = len(macro)
			stopper = len_with_brackets - 1		
			start = x	
			return in_brackets, start, stopper
		if (regex[x] == '[' and x == 0) or (regex[x] == '[' and x > 0 and regex[x - 1] != '\\'):
			in_brackets = parse_regex.find_in_brackets(1,x,regex)
			len_with_brackets = len(in_brackets)
			start = x
			stopper = len_with_brackets - 1	
			return in_brackets, start, stopper
	return 'DUMMY',0,0

'''
replace substitutions for \e ...
'''			
def substitute(regex):
	regex = regex.replace('[\w_\.\-]+','\\u+')
	regex = regex.replace('[\w._\-\'#+]+','\\e+')
	return regex

		
'''
require:	regex is a regular expression
ensure:		returns a regular expression, where all alternatives in regex of depth 1 are
			replaced by (.*), example: ab[a-z]+cd -> ab(.*)cd
'''
def calculate_simple_regex(regex):
	output = ''
	list = []
	stopper = 0
	begin = 0
	for x in range(len(regex)):
		if stopper > 0:
			stopper = stopper - 1
			continue
		if regex[x] == '(' and regex[x - 1] != '\\':
			in_brackets = parse_regex.find_in_brackets(0,x,regex)
			#print in_brackets
			len_with_brackets = len(in_brackets)
			#print 'Laenge', len_with_brackets, ' ', in_brackets
			stopper = len_with_brackets - 1				
			list.append(int(parse_regex.count_brackets(output + regex[begin:x]) + 1))	
			output = output + regex[begin:x] + '(.*)'
			#print regex[begin:x], 'list ', list		
			begin = x + len_with_brackets
		if regex[x] == '[' and regex[x-1] != '\\':
			in_brackets = parse_regex.find_in_brackets(1,x,regex)
			len_with_brackets = len(in_brackets)
			#print 'Laenge', len_with_brackets, ' ', in_brackets
			stopper = len_with_brackets - 1				
			list.append(int(parse_regex.count_brackets(output + regex[begin:x]) + 1))	
			output = output + regex[begin:x] + '(.*)'
			#print regex[begin:x], 'list ', list		
			begin = x + len_with_brackets
		if regex[x] == '\\':
			# saved characters
			if regex[x + 1] == '"' or regex[x + 1] == '.' or regex[x + 1] == '?' or regex[x + 1] == '!' or regex[x + 1] == '$' or regex[x + 1] == '@' or regex[x +1] == '(' or regex[x +1] == ')' or regex[x +1] == '[' or regex[x +1] == ']' or regex[x + 1] == 'n' or regex[x + 1] == 't' or regex[x + 1] == '+' or regex[x + 1] == '-' or regex[x + 1] == '^' or regex[x + 1] == '\\':
				continue
			in_brackets = parse_regex.find_in_brackets(2,x,regex)
			len_with_brackets = len(in_brackets)
			#print 'Laenge', len_with_brackets, ' ', in_brackets
			stopper = len_with_brackets - 1				
			list.append(int(parse_regex.count_brackets(output + regex[begin:x]) + 1))	
			output = output + regex[begin:x] + '(.*)'
			#print regex[begin:x], 'list ', list		
			begin = x + len_with_brackets 
	output = output + regex[begin:]
	return output



if __name__ == "__main__":
	filename = '../../data/batches/regexp.TXT'
	for line in file(filename):
			path = line[:line.find(':')].replace(' ','')
			print 'path: ', path
			print 'PFAD EINDE'
			(w,y) =  calculate_match_regex(line[line.find(':') + 2:])
	list = os.listdir('data/' + path + '/')
	print 'y : ', y
	c2 = re.compile(r"[\w\W\D\d]*" + y + "[\w\W\D\d]*")
	count = 0	
	match_list = []
	for a in range(len(w)):
		match_list.append([])
	for x in range(len(list)):
		count = count + 1
		if count == 100:
			break
		filename = 'data/' + path + '/' + str(list[x])
		try:
			f = open(filename)
		except IOError:
			print 'Error'
			continue
		line = f.read()
		m = c2.match(line)
		for a in range(len(w)):			
			match_list[a].append(m.group(w[a]))
		f.close
	print 'liste: ', match_list

"""	
def getMacroList():
	filename = 'macro_definition.txt'
	list = []
	for  line in file(filename):
		macro = line[:line.find(';')]
		regex = line[line.find(';') + 1:]
		list.append((macro,regex))
	return list
"""

def getMacroList():
	line = file(filename).read()
	indexLine = line.replace('\\$','AA')
	number = indexLine.count('$')
	begin = 0
	list = []
	for  a in range(number/2):
		idx1 = indexLine[begin:].find('$')
		idx2 = indexLine[begin + idx1 + 1:].find('$')
		newLine = line[begin + idx1:begin + idx2 + 2]
		begin += idx1 + idx2 + 2
#		print 'betrachte: ', newLine
		macro = newLine[:newLine.find(';')]
		regex = newLine[newLine.find(';') + 1:]#.replace('$','')
		if regex[len(regex) - 1] == '$':
			regex = regex[:len(regex) - 1]
		list.append((macro,regex))
	return list



def calculate_match_regexPanicMode(regex):
	macroList = getMacroList()
	#start = time.time()
	stringlist = []
	output = ''
	outputMacro = ''
	outputPanic = ''
	list = []
	listMacro = []
	listPanic = []
	stopper = 0
	begin = 0
	for x in range(len(regex)):
		if stopper > 0:
			stopper = stopper - 1
			continue
		#print 'an stelle ', x, ' ist ', regex[x]
		if (regex[x] == '(' and x == 0) or (regex[x] == '(' and x > 0 and regex[x - 1] != '\\'):
			#print 'x: ', regex[x]
			#print 'x - 1', regex[x-1]
			in_brackets = parse_regex.find_in_brackets(0,x,regex)			
			len_with_brackets = len(in_brackets)
			if in_brackets.replace('\\(','AA').count('(') > 0 or in_brackets.replace('\\[','AA').count('[') > 0:
				pan_brackets = '.*'
			else:
				pan_brackets = in_brackets
			#print 'Laenge', len_with_brackets, ' ', in_brackets
			stopper = len_with_brackets - 1				
			list.append(int(parse_regex.count_brackets(output + regex[begin:x]) + 1))	
			listMacro.append(int(parse_regex.count_brackets(outputMacro + regex[begin:x]) + 1))	
			listPanic.append(int(parse_regex.count_brackets(outputPanic + regex[begin:x]) + 1))	
			output = output + regex[begin:x] + '(' + in_brackets + ')'
			outputMacro = outputMacro + regex[begin:x] + '(' + in_brackets + ')'
			outputPanic = outputPanic + regex[begin:x] + '(' + pan_brackets + ')'
			stringlist.append(regex[begin:x])
			#print regex[begin:x], 'list ', list		
			begin = x + len_with_brackets
		if (regex[x] == '[' and x == 0) or (regex[x] == '[' and x > 0 and regex[x - 1] != '\\'):
			in_brackets = parse_regex.find_in_brackets(1,x,regex)
			len_with_brackets = len(in_brackets)
			#print 'Laenge', len_with_brackets, ' ', in_brackets
			stopper = len_with_brackets - 1				
			list.append(int(parse_regex.count_brackets(output + regex[begin:x]) + 1))
			listMacro.append(int(parse_regex.count_brackets(outputMacro + regex[begin:x]) + 1))
			listPanic.append(int(parse_regex.count_brackets(outputPanic + regex[begin:x]) + 1))			
			output = output + regex[begin:x] + '(' + in_brackets + ')'
			outputMacro = outputMacro + regex[begin:x] + '(' + in_brackets + ')'
			outputPanic = outputPanic + regex[begin:x] + '(' + in_brackets + ')'
			stringlist.append(regex[begin:x])
			#print regex[begin:x], 'list ', list		
			begin = x + len_with_brackets
		if (regex[x] == '$' and x == 0) or (regex[x] == '$' and x > 0 and regex[x - 1] != '\\') and regex[x + 1] == '{':
			macro = regex[x:x + regex[x:].find('}') + 1]
			# search wich macro is used
			for a in range(len(macroList)):
				if macro == macroList[a][0]:
					replaceRegex = macroList[a][1]
					if replaceRegex[len(replaceRegex) - 1] == '\n':
						replaceRegex = replaceRegex[0:len(replaceRegex)-1]
					break					
			in_brackets = replaceRegex
			len_with_brackets = len(macro)
			stopper = len_with_brackets - 1				
			list.append(int(parse_regex.count_brackets(output + regex[begin:x]) + 1))	
			listMacro.append(int(parse_regex.count_brackets(outputMacro + regex[begin:x]) + 1))
			listPanic.append(int(parse_regex.count_brackets(outputPanic + regex[begin:x]) + 1))	
			output = output + regex[begin:x] + '(' + in_brackets + ')'
			outputPanic = outputPanic + regex[begin:x] + '(' + in_brackets + ')'
			outputMacro = outputMacro + regex[begin:x] + '(' + macro + ')'			
			stringlist.append(regex[begin:x])
			#print regex[begin:x], 'list ', list		
			begin = x + len_with_brackets
			#print allo
		if regex[x] == '\\':
			# saved characters
			if regex[x + 1] == '"' or regex[x + 1] == '.' or regex[x + 1] == '?' or regex[x + 1] == '!' or regex[x + 1] == '$' or regex[x + 1] == '@' or regex[x +1] == '(' or regex[x +1] == ')' or regex[x +1] == '[' or regex[x +1] == ']' or regex[x + 1] == 'n' or regex[x + 1] == 't' or regex[x + 1] == '+' or regex[x + 1] == '-' or regex[x + 1] == '^':
				continue
			in_brackets = parse_regex.find_in_brackets(2,x,regex)
			len_with_brackets = len(in_brackets)
			macroOutput = in_brackets
#			print 'IN_Brackets: ', in_brackets
			# unfold macros
			if in_brackets == '\\l':
				in_brackets = '[\r]?'
			if in_brackets == '\\l*':
				in_brackets = '[\r\n]*'
			if in_brackets == '\\l+':
				in_brackets = '[\r\n]+'
			if in_brackets == '\\e+':
				in_brackets = '[\w._\-\'#+]+'	
			if in_brackets == '\\e':
				in_brackets = '[\w._\-\'#+]'	
			if in_brackets == '\\u+':
				in_brackets = '[\w_\.\-]+'
			#print 'Laenge', len_with_brackets, ' ', in_brackets
			stopper = len_with_brackets - 1				
			list.append(int(parse_regex.count_brackets(output + regex[begin:x]) + 1))
			listMacro.append(int(parse_regex.count_brackets(outputMacro + regex[begin:x]) + 1))	
			listPanic.append(int(parse_regex.count_brackets(outputPanic + regex[begin:x]) + 1))	
			output = output + regex[begin:x] + '(' + in_brackets + ')'
			outputPanic = outputPanic + regex[begin:x] + '(' + in_brackets + ')'
#			print 'neuer Output: ', output
			outputMacro = outputMacro + regex[begin:x] + '(' + macroOutput + ')'			
#			print 'Macro Output: ', outputMacro
			stringlist.append(regex[begin:x])
			#print regex[begin:x], 'list ', list		
			begin = x + len_with_brackets 
	output = output + regex[begin:]
	outputMacro = outputMacro + regex[begin:]
	stringlist.append(regex[begin:])
	#print 'Zeit fuer calculate_match_regex: ', time.time() - start
	return (list, output,stringlist,listMacro, outputMacro, listPanic, outputPanic)
	
	
def group_alternatives(regex):
	regexReplace = regex.replace('\|','#DUMMY#')
	regexReplace = regexReplace.replace('\(','#DUMMY1#')
	regexReplace = regexReplace.replace('\)','#DUMMY2#')
	
	brackOpenCount = 0
	brackCount = 0
	returnReg = ''
	brackList = []
	altList = []
	idx = 0
	for a in range(len(regexReplace)):
		if regexReplace[a] == '|' and brackOpenCount == 0:
			brackList.append(returnReg.count('(') + 1)
			returnReg += '(' + regexReplace[idx:a] + ')|'			
			altList.append(regexReplace[idx:a].replace('#DUMMY1#','\(').replace('#DUMMY2#','\)').replace('#DUMMY#','\|'))			
			idx = a + 1
		elif regexReplace[a] == '(':
			brackOpenCount += 1
		elif regexReplace[a] == ')':
			brackOpenCount -= 1
	brackList.append(returnReg.count('(') + 1)
	returnReg += '(' + regexReplace[idx:] + ')'
	altList.append(regexReplace[idx:].replace('#DUMMY1#','\(').replace('#DUMMY2#','\)').replace('#DUMMY#','\|'))
#	print returnReg
#	print brackList
#	print altList
	returnReg = returnReg.replace('#DUMMY1#','\(').replace('#DUMMY2#','\)').replace('#DUMMY#','\|')
	return brackList,returnReg,altList
