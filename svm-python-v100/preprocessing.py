'''
/***********************************************************************/
/*                                                                     */
/*   preprocessing.py                                                  */
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


import re, os,parse_regex,sys,signal,time#, regex

def help():
	print 'USAGE: python preprocessing.py <regex>'

	
# signal handler	
def signal_handler(signum,frame):
	raise Exception('Timed out!')
	
# returns true, if the regexp is matchable in at least 15 sec.	
def checkIsMatchable(alignmentPath, trainFile):
	signal.signal(signal.SIGALRM, signal_handler)
	signal.alarm(15)	# 15 seconds
	boolMatchable = True
	boolCanCreate = True
	try:
		fobj = open(alignmentPath,'r')
		alignment = fobj.read()
		fobj.close()
#		print 'start1'
		boolCanCreate = testRegexpForCompilation(alignment)
		alignment = alignment.replace('\n','\\r?\\n')
		c = re.compile(alignment, re.DOTALL)
#		print 'regexp:' + alignment
		fobj = open(trainFile,'r')
		trainFileContent = fobj.read()
		fobj.close()
#		print 'start2'
		fileList = trainFileContent.split('\n')
#		print 'trainFileContent: ', trainFileContent
#		print 'list: ', fileList
#		print 'start3'
		for ele in fileList:
			fobj = open(ele,'r')
			emailText = fobj.read()
			fobj.close()
			start = time.time()
#			print 'before search'
			m1 = c.search(emailText)
			if m1 is None:
				print 'error, because the alignment does not match the file: ' + ele
#				print 'text: ', emailText
				exit()
				boolCanCreate = False
				break
#			else:
#				print 'string: ', m1.group(7)
#			print 'time: ', time.time() - start, ' match: ', m1.group(1)[0:10]
			signal.alarm(0)
	except Exception:
#		print 'Timed out!'
		boolMatchable = False
	if boolCanCreate:
		return boolMatchable
	else:
		return True
	
	
# checks if the regular expression can be created	
def testRegexpForCompilation(regexp):
	boolRe = True
	try:
		m = re.compile(regexp,re.DOTALL)
	except Exception:
		return False
	return boolRe
	
	
	
'''
require:	reg is a regular expression
			fileList is a list of files
			dst is the destination of the files in the filelist
			path is the destination of the reg
ensure:		returns a reg where (.*) where the matchinglist contains
			only one distinct value with that value
			(example (a(.*)cd(.*)ja -> abcd(.*)ja)
'''
def getAlignRegex(reg,fileList,dst,path):
#	print 'reg: ', reg
#	print 'fileList: ', fileList
#	print 'dst: ', dst
	c1 = re.compile(reg,re.DOTALL)
	list_x = range(reg.count('(.') + 1)
	match_list_x = []
	for a in range(len(list_x) - 1):
		match_list_x.append([])
	for x in range(len(fileList)):
		filename = path + dst + '/' + str(fileList[x])
		try:
			f = open(filename)
		except IOError:
			print 'Error'
			continue
		line = f.read()
#		print 'line: ', line
		m1 = c1.match(line)
		for a in range(len(list_x[1:])):
#			print 'append: ', m1.group(list_x[1:][a])
			match_list_x[a].append(m1.group(list_x[1:][a]))
		f.close		
	#Improve Alignment
	'''
	stringList = regex.get_string_list(reg)
	stringList, match_list_x =  expandForSpecials(stringList,match_list_x)
	reg =  regex.printRegex(regex.Expression(stringList, [regex.Alternative('(.*)') for a in range(len(stringList) - 1)], False))
	'''
	reg = deleteSingleMatchLists(reg,match_list_x)
	return reg

def deleteSingleMatchLists(reg,match_list_x):
	changed = 0	
	matchList = match_list_x[:]
#	print 'Ausdruck zurzeit: ', reg
	for a in range(len(match_list_x)):
#		print 'Liste: ', match_list_x[a]
		test = set(match_list_x[a])
#		print 'Menge: ', test
		# if only one element in matchlist than replace (.*) with this element
		if len(test) == 1:
#			print 'ACHTUNG: ', match_list_x[a][0]
			strg = match_list_x[a][0]
			strg = strg.replace('(','\(')
			strg = strg.replace(')','\)')
			strg = strg.replace('[','\[')
			strg = strg.replace(']','\]')
			strg = strg.replace('$','\$')
			strg = strg.replace('.','\.')
			strg = strg.replace('?','\?')
			strg = strg.replace('@','\@')
			strg = strg.replace('-','\-')
			strg = strg.replace('+','\+')
			idx, end = getIndex(reg,a - changed)
			reg =  reg[:idx] + strg + reg[end + 1:]
			matchList = matchList[:a - changed] + matchList[(a - changed) + 1:]
			#print 'string: ', strg
			#	print 'reg: ', reg
			changed += 1
	#print 'return: ', reg
	return reg, matchList

# get matching_list
def getMatchList(reg,fileList,dst,path):
	c1 = re.compile(reg,re.DOTALL)
	list_x = range(reg.count('(.') + 1)
	match_list_x = []
	for a in range(len(list_x) - 1):
		match_list_x.append([])
	for x in range(len(fileList)):
		filename = path + dst + '/' + str(fileList[x])
		try:
			f = open(filename)
		except IOError:
			print 'Error'
			continue
		line = f.read()
		# replace 'geschuetzte Leerzeichen':
		line = line.replace('\\xA0',' ')
		line = line.replace('\r','')
#		print 'line: ', line
		m1 = c1.match(line)
		for a in range(len(list_x[1:])):
#			print 'append: ', m1.group(list_x[1:][a])
#			print 'line: ', line, '\nreg: ' , reg
			match_list_x[a].append(m1.group(list_x[1:][a]))
		f.close		
	return match_list_x
	

	
	
def transformAlignmentForCharacter(reg,fileList,dst,path,character):
	match_list_x = getMatchList(reg,fileList,dst,path)
	changed = 0
	matchList = match_list_x[:]	
	for i in range(len(match_list_x)):
	#	print 'bin in schleife: ', i
		maxLen = 0
		beforeDot = []
		afterDot = []
		allContainDot = True
		for j in range(len(match_list_x[i])):
			actStrg = match_list_x[i][j]
			if len(match_list_x[i][j]) > maxLen:
				maxLen = len(match_list_x[i][j])
			if match_list_x[i][j].count(character) == 0:
				allContainDot = False
			else:
				beforeDot.append(actStrg[:actStrg.find(character)])
				afterDot.append(actStrg[actStrg.find(character) + 1:])
		if allContainDot == True:
			firstReg = '(.{' + str(min([len(a) for a in beforeDot])) + ',' + str(max([len(a) for a in beforeDot])) + '})'
			secondReg = '(.{' + str(min([len(a) for a in afterDot])) + ',' + str(max([len(a) for a in afterDot])) + '})'
			idx, end = getIndex(reg,i + changed)
			if character == '.':
				addCharacter = '\.'
			elif character == '$':
				addCharacter = '\$'
			else:
				addCharacter = character
			reg = reg[:idx] + firstReg + addCharacter + secondReg + reg[end + 1:]
			matchList = matchList[:i - changed] + [beforeDot] + [afterDot] + matchList[(i + changed) + 1:]
			changed += 1
#	print 'reg: ', reg
#	print 'matchList: ', matchList
#	exit()
	return reg, matchList	

''' search if there is an @ or an $ in each element of the reg'''
def expandForSpecials(regex,matchList):
	print '####################################'
#	print 'vorher: ', regex
	for ccc in range(100):
		if regex.count('(.') > 99:
			return (regex, matchList)
		print ccc,'------------------------'
		print regex
		print '------------------------'
		flagChange = False
		for a in range(len(matchList)):
			if len(matchList[a]) == 0: continue
			atCount 	= 1000
			dollarCount = 1000
			pointCount 	= 1000
			slashCount	= 1000
			maxLen = 0
			for b in range(len(matchList[a])):
				helpAt 		= matchList[a][b].count('@')
				helpDollar	= matchList[a][b].count('$')
				helpPoint	= matchList[a][b].count('.')
				helpSlash	= matchList[a][b].count('/')
				helpLen 	= len(matchList[a][b])
				if helpAt < atCount: atCount = helpAt
				if helpDollar < dollarCount: dollarCount = helpDollar
				if helpPoint < pointCount: pointCount = helpPoint
				if helpSlash < slashCount: slashCount = helpSlash
				if helpLen > maxLen: maxLen = helpLen
				if maxLen > 70: break
			if maxLen < 71:
				if atCount > 0:
					match1 = []
					match2 = []
					for b in range(len(matchList[a])):
						idx = matchList[a][b].rfind('@')
						match1.append(matchList[a][b][0:idx])
						match2.append(matchList[a][b][idx + 1:])
					print 'AT'
					matchList = matchList[:a] + [match1,match2] + matchList[a + 1:]
					idx,end = getIndex(regex,a)
					minimum1 = min([len(match1[b]) for b in range(len(match1))])
					maximum1 = max([len(match1[b]) for b in range(len(match1))])
					minimum2 = min([len(match2[b]) for b in range(len(match2))])
					maximum2 = max([len(match2[b]) for b in range(len(match2))])
					regex = regex[:idx] + '(.{' + str(minimum1) + ',' + str(maximum1) + '})\@' + '(.{' + str(minimum2) + ',' + str(maximum2) + '})'  + regex[end + 1:]
					flagChange = True
					break
				elif dollarCount > 0:
					match1 = []
					match2 = []
					for b in range(len(matchList[a])):
						idx = matchList[a][b].rfind('$')
						match1.append(matchList[a][b][0:idx])
						match2.append(matchList[a][b][idx + 1:])
					print 'DOLLAR'
					matchList = matchList[:a] + [match1,match2] + matchList[a + 1:]
					idx,end = getIndex(regex,a)
					minimum1 = min([len(match1[b]) for b in range(len(match1))])
					maximum1 = max([len(match1[b]) for b in range(len(match1))])
					minimum2 = min([len(match2[b]) for b in range(len(match2))])
					maximum2 = max([len(match2[b]) for b in range(len(match2))])
		#			print 'von bis: ', regex[idx:end]
		#			print 'idx: ', idx, 'end: ', end
					regex = regex[:idx] + '(.{' + str(minimum1) + ',' + str(maximum1) + '})\$' + '(.{' + str(minimum2) + ',' + str(maximum2) + '})'  + regex[end + 1:]
					flagChange = True
					break
				elif pointCount > 0:
					match1 = []
					match2 = []
					for b in range(len(matchList[a])):
						idx = matchList[a][b].rfind('.')
						match1.append(matchList[a][b][0:idx])
						match2.append(matchList[a][b][idx + 1:])
					print 'POINT'
					matchList = matchList[:a] + [match1] + [match2] + matchList[a + 1:]
					idx,end = getIndex(regex[:],a)			
					idx, end = getIndex(regex[:],a)
					minimum1 = min([len(match1[b]) for b in range(len(match1))])
					maximum1 = max([len(match1[b]) for b in range(len(match1))])
					minimum2 = min([len(match2[b]) for b in range(len(match2))])
					maximum2 = max([len(match2[b]) for b in range(len(match2))])
					regex = regex[:idx] + '(.{' + str(minimum1) + ',' + str(maximum1) + '})\.' + '(.{' + str(minimum2) + ',' + str(maximum2) + '})'  + regex[end + 1:]
					flagChange = True
					break
				elif slashCount > 0:
					match1 = []
					match2 = []
					for b in range(len(matchList[a])):
						idx = matchList[a][b].rfind('/')
						match1.append(matchList[a][b][0:idx])
						match2.append(matchList[a][b][idx + 1:])
					print 'SLASH'
					matchList = matchList[:a] + [match1,match2] + matchList[a + 1:]
					idx,end = getIndex(regex,a)
					minimum1 = min([len(match1[b]) for b in range(len(match1))])
					maximum1 = max([len(match1[b]) for b in range(len(match1))])
					minimum2 = min([len(match2[b]) for b in range(len(match2))])
					maximum2 = max([len(match2[b]) for b in range(len(match2))])
					regex = regex[:idx] + '(.{' + str(minimum1) + ',' + str(maximum1) + '})/' + '(.{' + str(minimum2) + ',' + str(maximum2) + '})'  + regex[end + 1:]
					flagChange = True
					break
#		if flagChange:
#	#		return (regex,matchList)
#			print '++++++++++++++++++++++++++++++++'
#			print 'nachher: ', regex
#			return expandForSpecials(regex,matchList)
		if not flagChange:
	#		print '############## return #################'
	#		print 'stringList: ', len(stringList)
	#		print 'matchList: ', len(matchList)
			return (regex, matchList)
	print 'RETURN: ', regex
	return (regex,matchList)

'''
require:	regular expression in the form abc(.{x,y})def(.{x,y})ghi....
			number determines the (.{x,y}) we want to choose
ensure:		returns the index of the number's (.{x,y}) and the end index of the end of (.{x,y})
'''
def getIndex(regex,number):
#	print '\n regex in getIndex: ', regex, '\n'
	begin = 0
	for a in range(number + 1):
		idx = regex[begin:].find('(.')
		begin = begin + idx + 1
	end = regex[begin:].find(')')
	return begin - 1, begin + end

def getPanicRegex(reg):
	# cut off the header
	return '(.*)' + reg[reg.rfind('Received:'):]
	
def transformMatchableRegex(regex,batch):
	# create MatchingLists
	matchList = []
	number = regex.count('(.*)')
	for a in range(number):
		matchList.append([])
	c = re.compile(regex,re.DOTALL)
	for a in range(len(batch)):
		try:
			m = c.match(batch[a])
			for b in range(number):
				matchList[b].append(m.group(b + 1))
		except:
			print 'error'
	# extract the range for the (.*) and replace it
	# for example: (.*) -> (.{0,12})
	for a in range(number):
		idx = regex.find('(.*)')
		minimum = min([len(matchList[a][b]) for b in range(len(matchList[a]))])
		maximum = max([len(matchList[a][b]) for b in range(len(matchList[a]))])
		regex = regex[:idx] + '(.{' + str(minimum) + ',' + str(maximum) + '})' + regex[idx + 4:]
	regex, matchList = expandForSpecials(regex,matchList)
	regex, matchList = deleteSingleMatchLists(regex,matchList)
#	print 'vor expand: ', regex
#	print 'nach expand: ', regex
	return regex
	
	

	
def deleteLeadingEndingBackslash(regex):
	if regex[0] == '(':
		skip = False
		first = False
		second = False
		regex1 = ''
		regex2 = ''
		between = ''
		for x in range(len(regex)):
			if regex[x] == '(' and not skip:
				if len(regex1) == 0:
					regex1 += regex[x]
					first = True
				else:
					regex2 += regex[x]
					second = True
			elif regex[x] == ')' and not skip:
				if first:
					regex1 += regex[x]
					first = False
				if second:
					regex2 += regex[x]
					break
			elif (not first and not second and len(regex1) > 0):
				between += regex[x]
			elif (not first and not second and len(regex1) == 0):
				pre += regex[x]
			else:
				if first:
					regex1 += regex[x]
				if second:
					regex2 += regex[x]
#		print 'eins: ', regex1
#		print 'zwei: ', regex2
#		print 'drei: ', between
		c = re.compile('\(\.\{0,([0-9]+)\}\)',re.DOTALL)
		back = re.compile('[\n]+',re.DOTALL)
		nr1 = c.match(regex1).group(1)
		nr2 = c.match(regex2).group(1)
		if back.match(between) is not None:
			regex = regex.replace(regex1+between+regex2,'(.{0,' + str(int(nr1) + int(nr2) + len(between)) + '})')
	if regex[len(regex)-1] == ')':
		skip = False
		first = False
		second = False
		regex1 = ''
		regex2 = ''
		between = ''
		l = range(len(regex))
		l.reverse()
		for x in l:
			if regex[x] == '(' and not skip:
				if first:
					regex1 += regex[x]
					first = False
				if second:
					regex2 += regex[x]
					break
			elif regex[x] == ')' and not skip:
				if len(regex1) == 0:
					regex1 += regex[x]
					first = True
				else:
					regex2 += regex[x]
					second = True
			elif (not first and not second and len(regex1) > 0):
				between += regex[x]
			else:
				if first:
					regex1 += regex[x]
				if second:
					regex2 += regex[x]
		regex1 = regex1[::-1]
		regex2 = regex2[::-1]
		between = between[::-1]
#		print 'eins: ', regex1
#		print 'zwei: ', regex2
#		print 'drei: ', between
		c = re.compile('\(\.\{0,([0-9]+)\}\)',re.DOTALL)
		back = re.compile('[\n]+',re.DOTALL)
		nr1 = c.match(regex1).group(1)
		nr2 = c.match(regex2).group(1)
		if back.match(between) is not None:
			regex = regex.replace(regex2+between+regex1,'(.{0,' + str(int(nr1) + int(nr2) + len(between)) + '})')
#		print regex
	return regex
	

def deleteEndingBackslash(path):
	if(os.path.isfile(path)):
		fobj = open(path,'r')
		regex = fobj.read()
		fobj.close()
	if(os.path.isfile(path)):
		fobj = open(path,'w')
		if (len(regex) > 0):
			while regex[len(regex)-1] == '\n':
				regex = regex = regex[0:len(regex)-1]
				if (len(regex) == 0):
					break
			fobj.write(regex)
			fobj.close()
	
def delteEndingBackslashs(path):
	if(os.path.isfile(path)):
		fobj = open(path,'r')
		regex = fobj.read()
		fobj.close()
	if(os.path.isfile(path)):
		fobj = open(path,'w')
		if (len(regex) > 0):
			while regex.endswith('\n') or regex.endswith('\r\n'):
				if regex.endswith('\r\n'):
					regex = regex[0:len(regex)-2]
				else:
					regex = regex[0:len(regex)-1]
			fobj.write(regex)
			fobj.close()
	
def deleteEndingBackslashRegex(regex):
	while regex[len(regex)-1] == '\n':
		regex = regex = regex[0:len(regex)-1]
	return regex
	
def splitRegex(regex):
	nrGroups = regex.count('(.')
#	print 'Regex: ', regex
#	print 'nrGroups: ', nrGroups
	c = re.compile('(\(\.\*\)|\(\.\{0,[0-9]+\}\))',re.DOTALL)
	iterList = re.findall(c,regex)
#	print 'len iterlist: ', len(iterList)
	stringlist = get_string_list(regex)
#	print 'stringList: ', stringlist
#	print 'len stringlist: ', len(stringlist)
	splitRegList = []
	globCounter = 0
	splitNumber = 99
	for i in range((nrGroups / splitNumber) + 1):
		reg = ''
		if i != 0:
			reg = reg + iterList[globCounter - 1]
		if i == 0:
			for a in range(min(len(stringlist[globCounter:]) - 1,splitNumber) - 1):
				reg = reg + stringlist[globCounter] + iterList[globCounter]
				globCounter += 1
		else:
			for a in range(min(len(stringlist[globCounter:]) - 1,splitNumber - 1) - 1):
				reg = reg + stringlist[globCounter] + iterList[globCounter]
				globCounter += 1
		if i == (nrGroups / splitNumber):
			reg = reg + stringlist[globCounter] + iterList[globCounter] + stringlist[len(stringlist) -1]
	#		print '##############################REGi=='
	#		print 'stringList: ', stringlist[globCounter] , '###############', stringlist[globCounter+1]
	#		print reg
			#print 'end: ', globCounter, (len(stringlist)-1)
			globCounter += 1
		else:
			reg = reg + stringlist[globCounter] + '(.*)'
	#		print '##############################'
	#		print reg
			globCounter += 1
#		print 'NR: ', i, '\n', reg
#		print 'nrGroups: ', reg.count('(.')
#		print '##############################'
#		print 'Regex: ', reg
		splitRegList.append(reg[:])
	return splitRegList
#	print reg

# delete big white spaces:
# this means more than 3 (.{0,x})\W(.{0,y})\W(.{0,z}) -> (.{0,x+y+z+3})
def deleteBigWhitespaces(path):
	if(os.path.isfile(path)):
		fobj = open(path,'r')
		regex = fobj.read()
		fobj.close()
		while(True):
#			print 'search'
			c = re.compile('\(\.\{0,([0-9]+)\}\)(\W+)\(\.\{0,([0-9]+)\}\)(\W+)\(\.\{0,([0-9]+)\}\)',re.DOTALL)
			iter = c.search(regex)
			if iter is None:
				break
#				print 'found: ', iter.group(0)
			regex = regex.replace(iter.group(0),'(.{0,' + str(int(iter.group(1)) + int(iter.group(3)) + len(iter.group(2)) + len(iter.group(4)) + int(iter.group(5))) + '})')
			fobj = open(path,'w')
			fobj.write(regex)
			fobj.close()
	else:
		print 'error with file in preprocessing.py: ', path, regex
		
def deleteWhitespaces(strg):
	while(True):
#		print 'search'
		c = re.compile('\(\.\{0,([0-9]+)\}\)\(\.\{0,([0-9]+)\}\)',re.DOTALL)
		iter = c.search(strg)
		if iter is None:
			break
#			print 'found: ', iter.group(0)
		strg = strg.replace(iter.group(0),'(.{0,' + str(int(iter.group(1)) + int(iter.group(2))) + '})')
	return strg

	
# delte bigger ranges in regular expressions
# bigger means more then 10000, for example: .{0,10000}	
def deleteBigRanges(path):
	if(os.path.isfile(path)):
		fobj = open(path,'r')
		regex = fobj.read()
		fobj.close()
		count = 0
		c = re.compile('\(\.\{0,([0-9]{5}[0-9]*)\}\)',re.DOTALL)
		while(True):
			if count == 10000:
				break
			count += 1
#			print 'search'			
			iter = c.search(regex)
			if iter is None:
				break
#				print 'found: ', iter.group(0)
			regex = regex.replace(iter.group(0),'(.*)')
			fobj = open(path,'w')
			fobj.write(regex)
			fobj.close()
	else:
		print 'error with file in preprocessing.py: ', path, regex
	

'''
require:	a regular expression with the form a(.{x,y})b(.{x,y})c(.{x,y})... 'regex'
ensure:		returns a string list with the strings among the (.*)
			(example: a(.{x,y})b(.{x,y})c(.{x,y}) -> [a,b,c,''])
'''
def get_string_list(regex):
	count = regex.count('(.')
	list = []
	begin = 0
	for a in range(count):
		idx = regex[begin:].find('(.')#parse_regex.get_index_open(0,regex[begin:])
		list.append(regex[begin:begin + idx])#.replace('\\\\','\\'))
		# find next closing bracket }) of *)
		idx2 = regex[begin:].find('})')#parse_regex.get_index_close(0,regex[begin:])
		idx3 = regex[begin:].find('*)')
		if idx3 < idx2 and idx3 != -1:	idx2 = idx3
#		print 'between: ', regex[begin + idx:begin + idx2]
		begin = begin + idx2 + 2
	list.append(regex[begin:])#.replace('\\\\','\\'))
	'''
	for a in list:
		print a
	'''
	return list
				
def deleteEndingBeginningBackslashRegex(path):
	if(os.path.isfile(path)):
		fobj = open(path,'r')
		regex = fobj.read()
		regex = regex.replace('\r','')
		fobj.close()
	if(os.path.isfile(path)):
		fobj = open(path,'w')
		if (len(regex) > 0):
			countEnd = regex.count('\n')
			for a in range(countEnd):
				if regex[len(regex)-1] == '\n':
					regex = regex[0:len(regex)-1]
				else:
					break
			for a in range(countEnd):
				if regex[0] == '\n':
					regex = regex[1:]
				else:
					break
			countSlashL = regex.count('\\l')
			for a in range(countEnd):
				if len(regex) >= 2:
					if regex[len(regex)-2:] == '\\l':
						regex = regex[0:len(regex)-2]
					else:
						break
				else:
					break
			fobj.write(regex)
			fobj.close()			
				
if __name__ == "__main__":
	if len(sys.argv) != 2:
		help()
		exit()
	if sys.argv[1] != '-h':
		deleteEndingBackslash(sys.argv[1])
		deleteBigRanges(sys.argv[1])
	#	delete because we are unable to extract the header	
		deleteBigWhitespaces(sys.argv[1])
		exit()
	else:
		help()
		exit()
					
