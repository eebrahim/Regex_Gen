'''
/***********************************************************************/
/*                                                                     */
/*   parse_tree.py                                                     */
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

import re, parse_regex, time, regex, match_regex


'''
require:	Matching_list is a list of the Machtinglists for the alternatives
			with depth 1
			regex is a regular expression
			number determines wich text: x^number of the batch x is created by
			the regex
			'position' determines wich number is no dummy, -1, iff all alternatives are not dummy
ensure:		the parse Tree T(regex,x^number) for the expression regex
			and the text x^number
'''
def getParseTree(Matching_list,regex,number, position = -1):	
#	print 'Regex: ', regex
#	print 'testausgabe. ', regex.getAlternatives()[2]
#	print 'stringList: ', regex.getStringlist()
	startpunkt = time.time()
	output_string = ''
	output_list = []
	begin = 0
	flagStop = False
	for a in range(len(regex.getAlternatives())):
		# if it is a dummy from fmvc
		if position != -1:
			if regex.getAlternatives()[a].getType() == -1:
				if flagStop == False:
					continue
				else:
					break
		flagStop = True
#		print 'drucke: ', regex
#		print 'betrachte: ', regex.getAlternatives()[a].getString()
#		print 'zeit bis hier hin: ', time.time() - startpunkt
		sub_regex = regex.getAlternatives()[a]
		# if it is no dummy from fmvc
		if position == -1:
			fullString = replaceEscaped(regex.getStringlist()[a])
			for b in range(len(fullString)):
#				print 'fuege hinzu ParseTree: ', regex.getStringlist()[a][b]
				output_list.append([fullString[b]])
#		print 'sub_regex: ', sub_regex.getString()
		start = time.time()
		list = getSubTree(sub_regex,Matching_list[a][number])
#		print 'list: ', list
#		print 'Zeit in getSubTree: ', time.time() - start, 'fuer', sub_regex.getString()
#		if sub_regex.getString().count('DUMMY') == 0:
#			print list
		if len(list) > 0:
			if list[0][0] != '#': list.insert(0,'#' + sub_regex.getString() + ':')
		if len(list) > 1:
			output_list.append(list)
	# if it is no dummy from fmvc:
	if position == -1:
		fullString = replaceEscaped(regex.getStringlist()[len(regex.getStringlist()) - 1])
		dim = len(fullString)
		for b in range(dim):
#			print 'betrachte: ', regex.getStringlist()[a]
			output_list.append([fullstring[b]])					
#	print output_list
#	print allo
#	print 'zeit in getParseTree: ', time.time() - startpunkt
	return output_list
		
'''
require:	regex represents a regex of one alternative (example [a-z], (a|b), \D*)
			string represents a string of characters wich is created by regex
ensure: 	computes the parse tree T(regex,string) for the regex and the string
'''
def getSubTree(regex,string):
	out_list = []
	case = 0	
#	print 'in getSubTree: ', regex.getString()
	if regex.getType() == -1:
		case = 4
	elif regex.getType() >= 1 and regex.getType() <= 5:
		case = 2
	elif regex.getType() >= 6 and regex.getType() <= 10:
		case = 3
	else:
		case = 5	
	# type 1 - 5
	if case == 2:		
		reg = regex.getString()
		reg = replaceEscaped(reg)
		help_regex = reg[1:(len(reg) - 1)]
		# check if it is a regex like \e+ or \S+
		if not reg.startswith('['):
			innerRegex = reg[0:2]
		else:
			innerRegex = reg[1:reg.rfind(']')]
		offset = 0
		string = replaceEscaped(string)
		for i in range (len(string)):							
			teststring = string[i]
			# ueberpruefe welcher ausdruck gewaehlt wurde
			help_list = []
			help_list.append('#' + innerRegex + ':')
			help_list.append(teststring)
			out_list.append(help_list)
		out_list.insert(0,'#' + reg + ':')
	# type 6 - 10
	elif case == 3:		
		# special (.*) matches all strings
		if regex.getString() == '(.*)':
			string = replaceEscaped(string)
			for i in range (len(string)):			
				teststring = string[i]
				help_list = []
				help_list.append('#' + '.' + ':')
				help_list.append(teststring)
				out_list.append(help_list)
			out_list.insert(0,'#' + regex.getString() + ':')
			return out_list
#		print 'string: ', string
#		print 'betrachte: ', regex.getString()
#		print 'matchList: ', regex.getMatchinglist().getList()[0:1]
		# versuch mit neuem ding:
		reg_list = regex.getAlterlist()
#		print 'reg_list: ', reg_list
		innerRegex = regex.getString()[1:regex.getString().rfind(')')]
		innerRegex = replaceEscaped(innerRegex)
		# teste welche alternative gewaehlt wird
		chosen = -1
		laenge = 0
#		print 'STRING vorher: ', string
		while len(string) != 0:
#			print 'string: ', string, 'soll gematcht werden von: ', reg_list
#			print 'Reg_list: ', reg_list
			laenge = 0
			for i in range(len(reg_list)):
				#setzte dummywert... damit er nicht aussteigt wenn es nicht matcht
				help_teststring = 'DUMMY'
#				print 'Alternative reg_list[i]', reg_list[i]
				c = re.compile(replaceSpecials(reg_list[i]))
#				print 'versuche es mit: ', replaceSpecials(reg_list[i])				
				if c.match(string) is not None:
					help_teststring = c.match(string).group(0)
					if string.find(help_teststring) == 0 and len(help_teststring) > laenge:
						chosen = i
						teststring = help_teststring
	#					print 'TESTSTRING: ', teststring, 'gematcht'				
						laenge = len(teststring)
			string = string[len(teststring):]
			if teststring == 'DUMMY' or teststring == '':
					string = ''
			containAlt = computeContainAlt(reg_list,regex,chosen)			
			help_list = []
			begin = 0
			L,R,stringlist, listMacro, regexMacro = match_regex.calculate_match_regex(reg_list[chosen])
			c1 = re.compile(replaceSpecials(R),re.DOTALL)
			match = c1.match(teststring)
#			print 'containAlt: ', containAlt, 'von: ', regex.getString()
#			print 'matche mit: ', replaceSpecials(R)
#			print 'StringList: ', stringlist
			fullString = replaceEscaped(stringlist[0])
			for i in range(len(fullString)):
				help_list.append([fullString[i]])
			for i in range(len(containAlt)):
				if containAlt[i][1].getString() == '': break
				if teststring != 'DUMMY':
#					print 'rufe auf: ',containAlt[i][1].getString(),  match.group(i + 1), replaceSpecials(R), L[i]
					list = getSubTree(containAlt[i][1],match.group(L[i]))
				else:
					list = []
					string = ''
				list = flatten(list)
				if len(list) > 1:
#					print 'fuege hinzu: ', list
					help_list.append(list)
				fullString = replaceEscaped(stringlist[i + 1])
				for ca in range(len(fullString)):
					help_list.append([fullString[ca]])
			flag = False
			#help_list.insert(0,'#' + replaceEscaped(regex.getString()) + ':')
			help_list.insert(0,'#' + innerRegex + ':')
			out_list.append(help_list)
		if len(out_list) != 0:
			if out_list[0][0] != '#':
			#	out_list.insert(0,'#' + innerRegex + ':')
				out_list.insert(0,'#' + replaceEscaped(regex.getString()) + ':')
	#	print 'out_list: ', out_list
	elif case == 4:
#		inner_regexp = parse_regex.get_in_brackets(0,regex)
#		reg_list = []
		out_list = []
#		help_regex = inner_regexp
#		offset = 0
		fullString = replaceEscaped(string)
		for i in range (len(fullString)):
			out_list.append(['#' + 'DUMMY' + ':', fullString[i]])
		out_list.insert(0,'#' + '[DUMMY]*' + ':')
		#out_list.append(help_list)		
	elif case == 5:
		fullString = replaceEscaped(string)
		for i in range (len(fullString)):
			out_list.append(['#' + regex.getString() + ':', fullString[i]])
		out_list.insert(0,'#' + regex.getString() + ':')
	return out_list
			
			
'''
require:	regex
ensure:		returns the tuple (number, help_out)
			number computes the number of alternatives - 1
			help_out computes the the string of regex, where the alternatives
			of depth higher than one are replaced (example: a|(b|c) - > a|(bAc))
'''
def countAlternatives(regex):
	count = 0
	number = 0
	help_out = regex
	for a in range(len(regex)):
		if regex[a] == '(':
			if a - 1 >= 0:
				if regex[a-1] != '\\': count +=1
			else:
				count += 1
		if regex[a] == ')': 
			if a - 1 >= 0:
				if regex[a-1] != '\\': count -=1
			else:
				count -=1
		if regex[a] == '|' and regex[a - 1] != '\\' and count == 0: number += 1
		if regex[a] == '|' and count > 0: help_out = help_out[:a] + 'A' + help_out[a+1:]
	return number,help_out

	
"""
def sortString(string):
	#start = time.time()
	list = []
	re = ''
	for a in range(len(string)):
		list.append(string[a])
	list = sorted(list, key=coll.sort_key)
	for a in range(len(list)):
		re = re + list[a]
	#NEU: 14.3. replace
	#print 'zeit fuer sort: ', time.time() - start
	return re.replace('\\','')
"""
	
	
'''
requires:	list
ensure:		returns a list, wich do not contain nonrelevant grouping []
'''
def flatten(list):
	help_list = list
	while True:
		if len(help_list) == 1:
			if help_list[0].count('#') == 0:
				help_list = help_list[0]
			else:
				break
		else:
			break
	return help_list

		
		
pathList = []
'''
require: 	inputList is a string wich represents the root
			parseTree is the parseTree for the regex of inputList and a text
ensure:		set the global value pathList, so this value contains the paths for 
			the characters in text in the parseTree
'''
def getPathList(inputList, parseTree):
	lenparseTree = len(parseTree)
	for a in range(lenparseTree):
		laenge = len(parseTree[a])
		if laenge > 1:
			neuList = inputList[:]
			#neuList.append(sortString(parseTree[a][0]))
#			print 'da bin ich: ', parseTree[a][0]
			neuList.append((parseTree[a][0],laenge - 1))
	#		print 'rufe auf: ', neuList, 'und: ', parseTree[a][1:]
			getPathList(neuList,parseTree[a][1:])
		else:
#			print 'liste: ', inputList
#			print 'baum: ', parseTree[a]
			#inputList.append(sortString(parseTree[0]))
	#		inputList.append(parseTree[a][0])
	#		pathList.append(inputList[:])
	#		inputList = []	
			dummy = inputList[:]
			dummy.append((parseTree[a][0],1))
			pathList.append(dummy[:])

'''
'''
def createPathList(y,RegexpPosition,BatchPosition, complete = False):
#	print 'position: ', RegexpPosition
	pathList = []
#	print 'createPathList for: ', regex.printRegex(y)
#	print 'len: ', len(y.getAlternatives()) - RegexpPosition, 'cmplete: ', complete
	for a in range(len(y.getAlternatives()) - RegexpPosition):
#		print 'betrachte: ', y.getAlternatives()[a + RegexpPosition].getString()
		if complete:
			string = replaceEscaped(y.getStringlist()[a + RegexpPosition])
			for b in range(len(string)):
				pathList.append([(string[b],1)])
		elif y.getAlternatives()[a + RegexpPosition].getString() == '\S+' and a + RegexpPosition >= 1:
			# case \S+ \S+
			if y.getAlternatives()[a + RegexpPosition].getString() == '\S+' and y.getAlternatives()[a + RegexpPosition - 1].getString() == '\S+' and replaceEscaped(y.getStringlist()[a + RegexpPosition]) == ' ':
			#	print 'bin da'
			#	print 'before: ', pathList
				pathList.append([(' ',1)])
	#	print y.getAlternatives()[a + RegexpPosition].getString()
	#	print y.getAlternatives()[a + RegexpPosition].getMatchinglist()[BatchPosition]
		actType =  y.getAlternatives()[a + RegexpPosition].getType()
		actReg = y.getAlternatives()[a + RegexpPosition].getString()
		actReg = replaceEscaped(actReg)
	#	print 'betrachte: ', actReg, 'mit dem Typ: ', actType
		if actType >= 1 and actType <= 5:
			matchList = replaceEscaped(y.getAlternatives()[a + RegexpPosition].getMatchinglist().getList()[BatchPosition])
			if not actReg.startswith('['):
				innerRegex = actReg[0:2]
			else:
				innerRegex = actReg[1:actReg.rfind(']')]
			laenge = len(matchList)
#			print 'innerRegex: ', innerRegex, 'MatchList: ', matchList
			for b in range(laenge):
#				print 'mach was'
				one = (matchList[b],1)
				two = ('#' + innerRegex + ':',1)
				three = ('#' + actReg + ':',laenge)
				pathList.append([one,two,three])
		elif actType >= 6 and actType <= 10:
		#	print 'muss ich noch machen'
			# regex like ( \S+)+....
			if actReg.startswith('( \\S+)'):
				ending = actReg[actReg.index(')'):]
				matchList = replaceEscaped(y.getAlternatives()[a + RegexpPosition].getMatchinglist().getList()[BatchPosition])
				splitList = matchList.split(' ')
				splitList = splitList[1:]
				for zz in range(len(splitList)):
					one = (' ',1)
					two = ('# \\S+:',len(splitList)+1)
					three = ('# \\S+:',len(splitList))
					pathList.append([one,two,three])
					for b in range(len(splitList[zz])):
						one = (splitList[zz][b],1)
						two = ('#\S:',1)
						three = ('#\S+:',len(splitList[zz]))
						four = ('# \S+:',max(2,len(splitList)))
						five = ('# \S+:',len(splitList))
						pathList.append([one,two,three,four,five])
			else:
				matchList = replaceEscaped(y.getAlternatives()[a + RegexpPosition].getMatchinglist().getList()[BatchPosition])
				innerRegex = actReg[1:actReg.rfind(')')]
				laenge = len(matchList)
				for b in range(laenge):
					one = (matchList[b],1)
					two = ('#' + innerRegex + ':',laenge)
					three = ('#' + actReg + ':',1)
					pathList.append([one,two,three])
		elif actType == 11:
			matchList = replaceEscaped(y.getAlternatives()[a + RegexpPosition].getMatchinglist().getList()[BatchPosition])
			innerRegex = actReg
			laenge = len(matchList)
			for b in range(laenge):
				one = (matchList[b],1)
				two = ('#' + innerRegex + ':',laenge)
				three = ('#' + actReg + ':',1)
				pathList.append([one,two,three])
		else:
			break
	if complete:
		string = replaceEscaped(y.getStringlist()[len(y.getStringlist()) - 1])
		for b in range(len(string)):
			pathList.append([(string[b],1)])
#	print 'return pathList: ', pathList
	return pathList
		

'''
require: 	two strings string1 and string2
ensure:		returns True iff string1 is a permutation of string2, otherwise False
'''
def compare(string1,string2):	
#	print 'string1: ', string1
#	print 'string2: ', string2
	if len(string1) == len(string2):
		for a in range(len(string1)):
			if string1.count(string1[a]) != string2.count(string1[a]):
				return False
	else:
		return False	
	return True
	

		
'''
require: 	two lists, each represents a path through a tree
ensure: 	returns how many labels on the two pathes are not equal
'''
def penalty(path1, path2):
#	print 'path1: ', path1
#	print 'path2: ', path2
	a = 1
	b =  1
	if len(path1) == 1:
		v_i = path1[0]
		a = 0
	else:
		v_i = path1[1]
	
	if len(path2) == 1:
		w_i = path2[0]
		b = 0
	else:
		w_i = path2[1]
	#print 'v_i: ', v_i
	#print 'w_i: ', w_i
	#print allo
	if len(path1) == 1 and len(path2) == 1:
		return 0	
	else:
		if compare(v_i,w_i) == False:
			#print 'v_i False: ', v_i
			#print 'w_i False: ', w_i
			return 1 + penalty(path1[a:],path2[b:])
		else:
			#print 'v_i True: ', v_i
			#print 'w_i True: ', w_i
			return penalty(path1[a:],path2[b:])

def penaltyIterativ(path1,path2):
	path1 = path1[1:]
	path2 = path2[1:]
	len1 = len(path1)
	len2 = len(path2)
	if len1 > len2:
		one = path2[:]
		two = path1[:]
	else:
		one = path1[:]
		two = path2[:]
	for a in range(len(one)):
		if one[a][1] != one[a][1]:
			return (float(len(one) - a + abs(len1 - len2)) / float(max(len1,len2)) , float(min(one[a][1],one[a][1])))
		if compare(one[a][0],two[a][0]) == False:
			return (float(len(one) - a + abs(len1 - len2)) / float(max(len1,len2)), float(min(one[a][1],one[a][1])))
	return (0.0, 1.0)


# 11.10.2011	
def penaltyIterativNewApproach(path1,path2):
	path1 = path1[1:]
	path2 = path2[1:]
	len1 = len(path1)
	len2 = len(path2)
	if len1 > len2:
		one = path2[:]
		two = path1[:]
	else:
		one = path1[:]
		two = path2[:]
	loss = 0.0
	for a in range(len(one)):
#		print 'compare: ', one[a], two[a]
		reg1 = one[a][0][1:len(one[a][0])-1]
		reg2 = two[a][0][1:len(two[a][0])-1]
#		print 'reg1: ', reg1, 'reg2: ', reg2
		lambdaReg1 = lambda_r(reg1)
		lambdaReg2 = lambda_r(reg2)
#		print 'lam1: ', lambdaReg1, 'lam2: ', lambdaReg2
		tmpLoss = 0.0
		if lambdaReg1 != lambdaReg2:
			tmpLoss += 1.0
		if compare(one[a][0],two[a][0]) == False:
			tmpLoss += 1.0
		tmpLoss = tmpLoss / 2.0
		loss += tmpLoss
	loss = loss / float(len(one))
#	print 'loss: ' , loss
	return (loss, 1.0)	
	
'''
replace the specials, so that the re.compile(regex) works
'''
def replaceSpecials(regex):
	neu = regex.replace('\\e','[\w._\-\'#+]')
	neu = neu.replace('\\u','[\w_\.\-]')
	neu = neu.replace('\\l*','[\r\n]*')
	neu = neu.replace('\\l','[\r\n]*') # ACHTUNG
	neu = neu.replace('\\o','[ \t]')
	neu = neu.replace('${NL}','[^\n]*\n')
	neu = neu.replace('${AVAST}','[\(\X\-Antivirus\: avast!Clean\|StatusNotTested\r\n\)]*')
	neu = neu.replace('${IP}','\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
	neu = neu.replace('${WND_SP}','[A-Za-z0-9\-\!\'\"\&\.\?_,]+')
	return neu
	
'''
computes a list of alternatives wich are in the regex of list reg_list with index idx
'''
def computeContainAlt(reg_list,regex,idx):
	chosen = idx
	start = 0
	end = 0
	containAlt = []
	# how many alternatives we have to skip
	for a in range(chosen):
		list,reg,stringlist, listMacro, regexMacro = match_regex.calculate_match_regex(reg_list[a])
		start += len(list)
	list,reg,stringlist, listMacro, regexMacro = match_regex.calculate_match_regex(reg_list[chosen])
	end = start + len(list)
	for a in range(end - start):
#		print 'will machen: ', start + a, 'mit: ', regex.getContain()[start + a]
		containAlt.append((idx, regex.getContain()[start + a]))
	return containAlt	
	
'''
returns true if it is an escaped character
'''
def check_escaped(string):
	if string == '$':
		return True
	elif string == '-':
		return True
	elif string == '.':
		return True
	elif string == '(':
		return True
	elif string == ')':
		return True
	elif string == '[':
		return True
	elif string == ']':
		return True
	elif string == '"':
		return True
	elif string == '?':
		return True
	elif string == '@':
		return True
	elif string == '+':
		return True
	return False
	
def replaceEscaped(string):
	string = string.replace('\\$','$')
	string = string.replace('\\-','-')
	string = string.replace('\\.','.')
	string = string.replace('\\(','(')
	string = string.replace('\\)',')')
	string = string.replace('\\[','[')
	string = string.replace('\\]',']')
	string = string.replace('\\"','"')
	string = string.replace('\\?','?')
	string = string.replace('\\@','@')
	string = string.replace('\\+','+')
	string = string.replace('\\*','*')
	string = string.replace('\\_','_')
	string = string.replace('\\xA0',' ')
	string = string.replace('\\xa0',' ')
	string = string.replace('\xa0',' ')
	string = string.replace('\xA0',' ')
	string = string.replace('\ ',' ')
	return string
	
def lambda_r(altString):
	crange1 = re.compile('[\w\W]+\{\d+\}', re.DOTALL)
	crange2 = re.compile('[\w\W]+\{\d+,\d+\}', re.DOTALL)
	reVec = [0.0 for a in range(18)]
	
	range1Match = crange1.match(altString)
	range2Match = crange2.match(altString)
	range1 = 0
	if range1Match is not None:
		if len(range1Match.group(0)) == len(altString):
			range1 = 1
	range2 = 0
	if range2Match is not None:
		if len(range2Match.group(0)) == len(altString):
			range2 = 1	
	if altString == '(.*)':
		reVec[0] = 0.0
	elif altString == '':
		reVec[0] = 1.0
	elif len(altString) == 1:
		reVec[1] = 1.0
	elif altString == '0-9':
		reVec[2] = 1.0
	elif altString == 'a-z':
		reVec[3] = 1.0
	elif altString == 'A-Z':
		reVec[4] = 1.0
	elif altString == 'a-f':
		reVec[5] = 1.0
	elif altString == 'A-F':
		reVec[6] = 1.0
	elif altString == '\\S':
		reVec[7] = 1.0
	elif altString == '\\e':
		reVec[8] = 1.0
	elif altString == '\\d':
		reVec[9] = 1.0
	elif altString.endswith('*'):
		reVec[11] = 1.0
	elif altString.endswith('?'):
		reVec[12] = 1.0
	elif altString.endswith('+'):
		reVec[13] = 1.0
	elif range1 == 1:
		reVec[14] = 1.0
	elif range2 == 1:
		reVec[15] = 1.0
	elif altString.startswith('(') and altString.endswith(')') and not altString.startswith('(.*)') and not altString.endswith('(.*)') and (altString.count('|') - altString.count('\\|') >= 0):
		reVec[16] = 1.0
	elif altString.startswith('[') and altString.endswith(']'):
		reVec[17] = 1.0
	else:
		reVec[10] = 1.0
	# print out which one is one
#	for a in range(len(reVec)):
#		if reVec[a] == 1.0:
#			print 'number: ', a ,' is 1.0' 
	return reVec