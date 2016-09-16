'''
/***********************************************************************/
/*                                                                     */
/*   regex.py                                                          */
/*                                                                     */
/*   Basic algorithm for learning a model to predict a regular         */
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



"""A module for SVM^python for regex learning."""

# The svmlight package lets us use some useful portions of the C code.
import svmlight
import  sys, os, re, string, time
from copy import deepcopy
#sys.path.append('../../alignment/src/trunk/python_implementation/src')
import match_regex, parse_regex, parse_tree, preprocessing


alignmentDir = 'alignment_cpp/'

# These parameters are set to their default values so this declaration
# is technically unnecessary.
svmpython_parameters = {'index_from_one':True}
#parameter_feature = [4,4,3,3,3,4,4,2,2,2,2,2,2,2,2,2,2,2,2,2,3,3]
# save the values, to same cpu-time
y_regex =[]
y_values =[]
y_matchings = []
batches = []
batchNames = []

# save lists for the loss functions:
y_parseTree = []
y_parseTreeApprox = []
y_fullPathListTree = []
flagApprox = False
upperTrainBound = 100
list_compare = []
# loss for specials in brackets, e.g. [0-9]+
list_loss = []
# list for replacements wich are possible for a .*
list_class = []
# list of all macros wich can be inserted in the regex:
macroList = []
# list of all possible Macros from file 'macro_definition.txt'
possMacroList = match_regex.getMacroList()
# 4 = tree-loss with full tree
flagLoss = 4

# examples are stored here
ybar_matchings = []

# list to store wich regexp we have to compare
list_poss = []

# extra parameters wich are added behind the matching list
extra_parameters = 5
# number of different types and specials
number_types = 11
number_specials = 7
number_features = 18
# match_feature
number_extra_feature = 1
# list of shortcuts:
shortCutList = ['A-Z','a-z','0-9','A-F','a-f','\\e','\\S']
par_sm = 1
par_sparm = 1
examples = []
testExamples = []
flagTrainError = False
'''
unitVector = True -> psi like in diploma thesis: unit vector
unitVector = False -> psi like loss function vectains a 1 for the type of regExp (1-10) and a 1 for every shortcut (a-z,...)
'''
unitVector = False

actModel = ''
# flag for trace-option
flagTrace = False
outputPicture = 'tree_loss_gen.png'

'''
Class for the alternatives is defined
'''
class Alternative:
	def __init__(self, str = '', mat = [], typ = -1, sho = [0 for a in range(number_specials)], con = [],alt = []):
		# string of the alternativ
		self.string = str
#		# depth of the alternativ
#		self.depth = dep
		# matchingList of the alternative
		self.matchinglist = mat
		# type of the alternativ
		self.type = typ
		# list of shortcuts of the form a-z,....
		self.shortcut = sho
		# list of alternatives wich are inside the current alternativ
		self.contain = con
		# list of alternatives iff type 6 - 10
		self.alterlist = alt
		self.NoLoss = True
		# stores the list of the top level alternatives in the form of the types Lambda(r)
		self.topLevelAlternativeTypes = []
		# stores the typ Lambda(r) of the alternative itself
		self.lambdaType = []
	def setString(self, str):
		self.string = str
	def getString(self):
		return self.string
	def setMatchinglist(self,list):
		self.matchinglist = list
	def getMatchinglist(self):
		return self.matchinglist
#	def setDepth(self,int):
#		self.Depth = int
#	def getDepth(self):
#		return self.depth
	def setType(self,int):
		self.type = int
	def getType(self):
		return self.type
	def setShortcut(self,list):
		self.shortcut = list
	def getShortcut(self):
		return self.shortcut
	def setContain(self,list):
		self.contain = list
	def getContain(self):
		return self.contain
	def setAlterlist(self,list):
		self.alterlist = list
	def getAlterlist(self):
		return self.alterlist
	def addAlternative(self,alternative):
		self.contain.append(alternative)
	def reset(self):
		self.type = -1
		self.string = '[DUMMY]*'
		self.shortcut = [0 for a in range(number_specials)]
	def setNoLoss(self,bool):
		self.NoLoss = bool
	def getNoLoss(self):
		return self.NoLoss
	def setPreString(self,string):
		self.PreString = string
	def getPreString(self):
		return self.PreString
	def setPostString(self,string):
		self.PostString = string
	def getPostString(self):
		return self.PostString
	# flag is 1 if this alternative is a beginning
	# for example \S+( \S+)? only the first \S+ is a beginning
	def setBeginning(self,begin):
		self.Beginnig = begin
	def getBeginning(self):
		if hasattr(self,'Beginning'):
			return self.Beginnig
		else:
			return 0
	def setTopLevelAlternativeTypes(self,typeList):
		self.topLevelAlternativeTypes = typeList
	def getTopLevelAlternativeTypes(self):
		return self.topLevelAlternativeTypes
	def setLambdaType(self,lambda_r):
		self.lambdaType = lambda_r
	def getLambdaType(self):
		return self.lambdaType
	


'''
class for a regular expression, wich contains of a stringlist [s_1,s_2,...,s_n]
and a list of alternatives = [a_1,a_2,...,a_n-1]
y = s_1 a_1 s_2 ... s_n-1 a_n-1 s_n
'''
class Expression:
	def __init__(self, str = [], alt = [], train = False):
		# stringlist
		self.stringlist = str
		# alternativlist
		self.alternatives = alt
		# flag if it is a training-sample
		self.traindata = train
		# flag if expression is a dummy, position wich is not a dummy or -1 if it is no dummy
		self.dummy = -1
		self.SubExpressionList = []
	def getTrain(self):
		return self.traindata
	def getStringlist(self):
		return self.stringlist
	def setStringlist(self,str):
		self.stringlist = str
	def getAlternatives(self):
		return self.alternatives
	def setAlternatives(self,alt):
		self.alternatives = alt
	def getDummy(self):
		return self.dummy
	def setDummy(self,int):
		self.dummy = int
	def setID(self,id):
		self.id = id
	def getID(self):
		return self.id	
	def setStartEndList(self,list):
		self.startEndList = list
	def getStartEndList(self):
		return self.startEndList
	def setSubExpressionList(self,subList):
		self.SubExpressionList = subList
	def getSubExpressionList(self):
		return self.SubExpressionList


'''
class for a batch, wich contains of a stringlist [s_1,s_2,...,s_n] from the alingnment the number 'a' of 
(.^*) in that alignment and the matchinglists [m_1,m_2,...,m_a] for the (.^*)
a text can be extracted in the following way:
 t_i = s_1 m_1 s_2 ... s_n-1 m_a s_n
'''
class Batch:
	def __init__(self, str = [], num = 0, mat = []):
		# stringlist
		self.stringlist = str
		# alternativlist
		self.number = num
		# matchlists
		self.matchinglist = mat
	def getStringlist(self):
		return self.stringlist
	def setStringlist(self,str):
		self.stringlist = str
	def getNumber(self):
		return self.number
	def setNumber(self,num):
		self.number = num
	def getMatchinglist(self):
		return self.matchinglist
	def setMatchinglist(self,mat):
		self.matchinglist = mat
	def setID(self,id):
		self.id = id
	def getID(self):
		return self.id	
	def setListNoLoss(self,list):
		self.ListNoLoss = list
	def getListNoLoss(self):
		return self.ListNoLoss


'''
class Loss wich stores the errors for the special
Macro identifies wich type of macro is used
errorList is a list wich stores the error for a x^j of the batch x
'''
class Loss:
	def __init__(self,error_li = [[]]):
		self.error_list = error_li
	def getErrorList(self):
		return self.error_list

'''
'''
class MatchingList:
	def __init__(self, li = []):
		self.list = li
		self.featureVector = []
	def getList(self):
		return self.list
	def setList(self,li):
		self.list = li
	def getDistinctCharacterSet(self):
		return self.distinctCharacterSet
	def setDistinctCharacterSet(self,tuple):
		self.distinctCharacterSet = tuple
	def getAttrAlternatives(self):
		return self.AttrAlternatives
	def setAttrAlternatives(self,tuple):
		self.AttrAlternatives = tuple
	def getMaxMinDistinctLength(self):
		return self.MaxMinDistinctLength
	def setMaxMinDistinctLength(self,tuple):
		self.MaxMinDistinctLength = tuple
	def getContainSpecials(self):
		return self.ContainSpecials
	def setContainSpecials(self,tuple):
		self.ContainSpecials = tuple
	def setMatchesEPlus(self,bool):
		self.MatchesEPlus = bool
	def getMatchesEPlus(self):
		return self.MatchesEPlus
	def setFeatureVector(self,vec):
		self.featureVector = vec
	def getFeatureVector(self):
		return self.featureVector
		
'''
'''
class Macro:
	def __init__(self, alternativeList, stringList, lossList, startStringList, endStringList, macroType):
		self.alternativeList = alternativeList
		self.startStringList = startStringList
		self.endStringList = endStringList
		self.stringList = stringList
		self.macroType = macroType
	def getStringlist(self):
		return self.stringList
	def getAlternativelist(self):
		return self.alternativeList
	def getStartStringList(self):
		return self.startStringList
	def getEndStringList(self):
		return self.endStringList
	def getMacroType(self):
		return self.macroType

def read_struct_examples(filename, sparm):
	global examples
	global testExamples
	global flagTrainError
	if flagTrace:
		pycallgraph.start_trace()
    # This reads example files of the type read by SVM^multiclass.	
	sparm.num_features = sparm.num_classes = 0
    # Open the file and read each example.    
	examples = []
	testExamples = []
	stopper = 0
	id = 0
	path = ''
	filenameBakup = filename
	for line in file(filename):
		batchName = line
		startTime = time.time()
		if line == '\n':
			break
		stopper +=1
		if False:
			continue
		id += 1
		dst = line[0:line.find(';')]
		if (os.path.isfile(path + dst + '/label.txt')):
			fobj = open(path + dst + '/label.txt','r')
			regex = fobj.read()
			# replace \l
			regex = regex.replace('\\l\n','\n')
			fobj.close()
		else:
			print 'error: ', path + dst + '/label.txt' + 'does not exist'
			print allo
		regex = '(.*)' + regex + '(.*)'
		#replace the character \r?
		regex = replaceNewLineAppend(regex)
		cop = regex
		list,regex,stringlist, listMacro, regexMacro = match_regex.calculate_match_regex(regex)
		print 'read: ', dst
		c1 = re.compile(replaceSpecials(regex),re.DOTALL)
		file_list_help = os.listdir(path + dst + '/')
		file_list = []
		for a in range(len(file_list_help)):
			if file_list_help[a].count('.in') > 0:
				file_list.append(file_list_help[a])
		file_list.sort()
		file_list_x = []
		match_list = []
		match_list_x = []
		if (os.path.isfile(path + dst + '/alignment.txt')):
			fobj = open(path + dst + '/alignment.txt','r')
			regex_x = fobj.read()
			fobj.close()
		else:
			if os.path.isfile(path + dst + '/filelist.txt'):				
				print 'create alignment for: ', dst
				os.system(alignmentDir + 'Align -q -n -i 1 -f ' + path + dst + 'filelist.txt > ' + path + dst + '/alignment.txt')
				preprocessing.delteEndingBackslashs(path + dst + '/alignment.txt')
				fobj = open(path + dst + '/alignment.txt','r')
				regex_x = fobj.read()
				fobj.close()
			else:
				print 'file ' + path + dst + '/filelist.txt does not exist\n unable to create alignment'
				print allo		
		# calculate the amount of regex's:
		list_x = range(regex_x.count('(.') + 1)
		for a in range(len(list)):
			match_list.append([])
		for a in range(len(list_x) - 1):
			match_list_x.append([])
		# how many distinct characters are in one matching_list
		distinct_characters_x = set()
		distinct_characters_y = set()
		batch_list = []
		# list to store the start and the ending of the match for the real regexp
		# for example: (.*) abc[a-z]* (.*) only abc[a-z]* is important
		startEndList = []
		# list, to store wich matchinglists are not considered in the real regex, used for learning
		listNoLoss = [False for a in range(len(list_x[1:]))]	

		# replace linebreak	
		#regex_x_ali = regex_x.replace('\n','\\r?\\n')
		#regex_x = 'Subject: Complimentary website analysis for (.*)\.com - Rank top in the search engines!(.*)'
		c2 = re.compile(regex_x,re.DOTALL)		
		for x in range(len(file_list)):
			filename = path + dst + '/' + str(file_list[x])
			#preprocessing.deleteEndingBackslash(filename)
			try:
				f = open(filename)
			except IOError:
				print 'Error'
				continue
			line = f.read()
			# replace 'geschuetzte Leerzeichen':
			line = line.replace('\\xA0',' ')
			line = line.replace('\r','')
			batch_list.append(line)
			m2 = c2.match(line)
			m1 = c1.match(line)		
			for a in range(len(list)):
				match_list[a].append(m1.group(list[a]))
			start = m1.end(list[0])
			end = m1.start(list[len(list) - 1])
			startEndList.append((start,end))
			# list, to store wich matchinglists are not considered in the real regex, used for learning
			helplistNoLoss = [False for a in range(len(list_x[1:]))]
			for a in range(len(list_x[1:])):
				if m2 is None:
					print 'lin: ', line
					print 'ali: ', regex_x
					print 'filename: ', filename
				match_list_x[a].append(m2.group(list_x[1:][a]))
				if not (m2.start(list_x[1:][a]) < start or m2.start(list_x[1:][a]) > end):
					helplistNoLoss[a] = True
			f.close
			listNoLoss = [listNoLoss[a] or helplistNoLoss[a] for a in range(len(listNoLoss))]
		batches.append(batch_list)
		batchNames.append(batchName)
		
		matchList = []
		for a in range(len(match_list)):
			matchList.append(computeMatchList(match_list[a]))
		matchListx = []
		for a in range(len(match_list_x)):
			matchListx.append(computeMatchList(match_list_x[a]))
		y_stringlist = stringlist
		y_alternatives = getListOfAlternatives(listMacro,regexMacro,matchList)			
		y_SubExpressionList = getListOfAlternativesNew(listMacro,regexMacro,matchList,stringlist,batch_list,cop)
		
		
		x_stringlist = get_string_list(regex_x)
		x_number = len(list_x) - 1
		x_matchlist = matchListx
		x = Batch(x_stringlist,x_number,x_matchlist)
		x.setID(id - 1)
		x.setListNoLoss(listNoLoss)
		y = Expression(y_stringlist,y_alternatives,True)
		
	
		
		y.setID(id - 1)
		y.setStartEndList(startEndList)
		y.setSubExpressionList(y_SubExpressionList)
		
			
		# add trainingdata
		examples.append((x,y))
		y_regex.append(y)
		#add for each position an empty list in list_loss
		list_class.append(createClassList(x))
		ybar_matchings.append(match_list_x)
		y_matchings.append(matchList)
		L_y = y_alternatives
		y_values.append(calc_psi)
		list_poss.append([])
		for a in range(len(match_list_x)):
			list_poss[len(y_matchings) - 1].append([])
		helper_list = []
		# structs for the loss function get initialized
		anfang = time.time()
		if flagLoss == 4:
			helpList = []
			for ii in range(len(batch_list)):
				if ii == upperTrainBound:
					break
				ytree = parse_tree.getParseTree(match_list,y,ii)
				parse_tree.pathList = []
				parse_tree.getPathList([],ytree)
				yPathList = parse_tree.pathList[:]
	
				if len(yPathList) != len(batch_list[ii]):
					print 'error for: ', printRegex(y)
					st = ''
					for bbb in range(len(yPathList)):
						st = st + yPathList[bbb][len(yPathList[bbb]) - 1][0]
					print 'string: ', st
					print 'batch     : ', batch_list[ii]
					for a in range(len(batch_list[ii])):
						if batch_list[ii][a] != yPathList[a][len(yPathList[a]) - 1][0]:
							print 'error: ', batch_list[ii][a:]
							break
					print allo
				helpList.append(yPathList)
			y_fullPathListTree.append(helpList)
		list_loss.append(createLossList(x,y,list_class,sparm))
		sparm.num_classes = number_types + number_specials
		sparm.num_features = number_features
		print 'time for preprocessing: ', time.time() - startTime
	skip = True
	print len(examples),'examples read.'
	TrainingstatList = [(0,0) for a in range(len(examples))]
	return examples

	
def loss(y, ybar, sparm, position = 0):
#	print 'vergleiche: ', printRegex(y), ' mit: ', printRegex(ybar)
	error = 0	
	if flagLoss == 4:
		# find the corrosponding y
		i = y.getID()
		start_all = time.time()
		st = ''
		for ddd in range(len(ybar.getAlternatives())):
			st = st + ybar.getStringlist()[ddd] + ybar.getAlternatives()[ddd].getString()
		st = st + ybar.getStringlist()[len(ybar.getStringlist()) - 1]
		# test if there are dummy elements in the regex if True then consider the whole regex
		if ybar.getDummy() == -1:
			# for all batches:
			for a in range(len(batches[i])):
				if a == upperTrainBound:
					break
				start ,end = y.getStartEndList()[a]
				ybarPathList = parse_tree.createPathList(ybar,0,a,True)
				help_error = 0.0
				# correct mapping if there would be an error:
				dim = end - start
				if start + dim > len(ybarPathList):
					dim -= start + dim - len(ybarPathList)
				# for all path's:
#				print 'dim: ', dim
				count = 0
				for b in range(dim):						
#					print 'len: ', len(batches[i][a]), 'idx: ', b + start, 'b: ', b, 'dim: ', dim, 'len(ybarPathList', len(ybarPathList)
					path2 = ybarPathList[b + start][:]
					path1 = y_fullPathListTree[i][a][b + start][:]							
					path1.reverse()
					if path1[0] != path2[0]:
						print 'eins: ', path1[0], 'zwei: ', path2[0], 'in: ', b
						bool = False
						out = 0
						for coo in range(len(ybarPathList)):
							if coo < start:
								continue
							if coo > end:
								continue
							if bool or (y_fullPathListTree[i][a][coo][len(y_fullPathListTree[i][a][coo]) - 1] != ybarPathList[coo][0][0]):
								print coo, y_fullPathListTree[i][a][coo][len(y_fullPathListTree[i][a][coo]) - 1], 'gegen: ', ybarPathList[coo][0]	
								bool = True
								out = out + 1
								if out >= 150:
									break		
						print 'BATCH: ', batches[i][a], 'ID: ', i	
						st = ''
						for bbb in range(len(y_fullPathListTree[i][a])):
							st = st + y_fullPathListTree[i][a][bbb][len(y_fullPathListTree[i][a][bbb]) - 1][0]
						print 'meinstring: ', st
						print y.getID()
						print allo
					# skip parts of alignment
					if len(path2) == 1:
						# perfect matching alignment:
						if len(path1) == 1:
							count += 1
							help_error += 0
						# error in alignment
						else:
							count += 1
							help_error += 1
						continue
					(max_level,min_edges) = parse_tree.penaltyIterativ(path1,path2)
					count += 1
					# zero-one loss for each error
					help_error += float(max_level)# / min_edges)
				if count != 0:
					help_error = help_error / (count)
#				help_error = help_error / 10000
				error += float(help_error)
			if len(batches[i]) != 0: error = error / float(min(len(batches[i]),upperTrainBound))
		else:
			for a in range(len(batches[i])):
				if a == upperTrainBound:
					break
				start ,end = y.getStartEndList()[a]
				# set the values for start and end of the string we consider
				vor_stringList = ybar.getStringlist()[:position]
				vor_matchList = ybar_matchings[i][:position]
				start_path = 0
				for co in range(len(vor_stringList)): 
					start_path += len(parse_tree.replaceEscaped(vor_stringList[co]))
				start_index = start_path + len(parse_tree.replaceEscaped(ybar.getStringlist()[position]))
				for co in range(len(vor_matchList)): 
					if len(vor_matchList[co][a]) > 0: start_path += 1
				end_path = start_path + len(parse_tree.replaceEscaped(ybar.getStringlist()[position]))
				if len(ybar_matchings[i][position]) > 0: end_path += 1
				for co in range(len(vor_matchList)): 
					start_index += len(parse_tree.replaceEscaped(vor_matchList[co][a]))
				end_index = start_index
				end_index += len(parse_tree.replaceEscaped(ybar_matchings[i][position][a]))
				ybarPathList = parse_tree.createPathList(ybar,position,a)
				help_error = 0.0
				'''
				only consider the part of the regex, we can used to learn
				'''				
				if start_index < start and end_index < start:
#					print 'return 0.0 wegen: ', position
					return 0.0
				if start_index > end and end_index > end:
#					print 'return 0.0 wegen: ', position
					return 0.0
				count = 0
				for b in range(end_index - start_index):						
					path1 = y_fullPathListTree[i][a][b + start_index][:]
					path2 = ybarPathList[b][:]
					path1.reverse()
				#	print 'path1: ', path1
				#	print 'path2: ', path2
					if path1[0] != path2[0]:
						print start_index	
						for coo in range(len(y_fullPathListTree[i][a])):
							try:
								print y_fullPathListTree[i][a][start_index + coo][len(y_fullPathListTree[i][a][start_index + coo]) - 1], ' and: ', ybarPathList[coo][0]
							except:
									print 'batch: ', batches[i][a], 'number: ', a, 'length: ', len(batches[i][a]), 'length: ', len(y_fullPathListTree[i][a]), 'length: ', len(ybarPathList), 'position: ', position
									for co in range(len(vor_stringList)):
										st = parse_tree.replaceEscaped(vor_stringList[co])
										print 'string: ', st, 'len: ', len(st)
									st = ''
									for bbb in range(len(y_fullPathListTree[i][a])):
										st = st + y_fullPathListTree[i][a][bbb][len(y_fullPathListTree[i][a][bbb]) - 1][0]
									print 'string: ', st[start_index:]
									print allo
						# exit with error
						print allo
					if len(path2) == 1:
						# perfect matching alignment:
						if len(path1) == 1:
							count += 1
							help_error += 0
						# error in alignment
						else:
							count += 1
							help_error += 1
						continue
					count += 1
					(max_level,min_edges) = parse_tree.penaltyIterativ(path1,path2)
				#	print 'max_level: ', max_level, ' min_edges: ', min_edges
					# zero-one loss for each error
					help_error += float(max_level)# / min_edges)
				if count != 0:
					help_error = help_error / count
				error += float(help_error)
			if len(batches[i]) != 0: error = error / float(min(len(batches[i]),upperTrainBound))
		return error
	return error	
	
def init_struct_model(sample, sm, sparm):	 
    # In the corresponding C code, the counting of features and
    # classes was done in the model initialization, not here.
    #sm.size_psi = sum(parameter_feature) #sparm.num_features * sparm.num_classes
    # Neu 3.4.2010 neuer wert fuer grossen featurevector
    #sm.size_psi = ((number_types + number_specials) * number_features) + number_extra_feature
    sm.size_psi = ((5 * len(get_possiblilities()) + 5) * number_features)*2
    print 'size_psi set to',sm.size_psi


def classify_struct_example(x, sm, sparm):
#	print 'Classify'
	return find_most_violated_constraint(x, 'hello',sm,sparm,False)
	
	
def write_label(fp, y):
	fp.write(printRegex(y) + '\n----------\n')

	
def find_most_violated_constraint(x, y, sm, sparm, fmvc = True):
	global actModel
	global examples
	global testExamples
	if fmvc == False:
		print 'Classify : ', batchNames[x.getID()]
	if actModel != sm.w and fmvc == True and False:
		losssum = 0
		for a in range(len(examples)):
			losssum += loss(examples[a][1],find_most_violated_constraint(examples[a][0],y,sm,sparm,False),sparm)
		losssumTest = 0
		for a in range(len(testExamples)):
			losssumTest += loss(testExamples[a][1],find_most_violated_constraint(testExamples[a][0],testExamples[a][1],sm,sparm,False),sparm)
		actModel = sm.w
		if len(examples) != 0:
			print 'TrainERROR: ', losssum/len(examples)
		if len(testExamples) != 0:
			print 'TestERROR: ', losssumTest / len(testExamples)
	matching_list_x = x.getMatchinglist()
	number = x.getNumber()
	string_list = x.getStringlist()
	# predict a regular expression
	if not fmvc:
		out = [Alternative('[DUMMY]*',matching_list_x[a]) for a in range(number)]
		ret = [Alternative('[DUMMY]*',matching_list_x[a]) for a in range(number)]
		helpStringList = []
		helpAlternatives = []
		for a in range(number):
			replacement = getMaxRegex([],out[:],ret,string_list,a,fmvc,0.0,y,x,sm,sparm)
			# add strings to the stringList if replacement is of the form: string_1[]sring_2[]string_3, where string_1 or string_3 != '', 
			# for example: [hH]ttp:// : we have to add ttp:// to the next Stringlist
			# in: xyz[hH]: we have to add xyz to the previous stringlist
			if replacement.getStringlist()[0] != '':
				helpStringList[len(helpStringList)-1] = helpStringList[len(helpStringList)-1] + replacement.getStringlist()[0]
			if replacement.getStringlist()[len(replacement.getStringlist())-1] != '':
				string_list[a+1] = replacement.getStringlist()[len(replacement.getStringlist())-1] + string_list[a+1]
			helpStringList = helpStringList + string_list[a:a + 1] + replacement.getStringlist()[1:len(replacement.getStringlist())-1]
			helpAlternatives = helpAlternatives + replacement.getAlternatives()
			out[a].reset()
		helpStringList = helpStringList + [string_list[len(string_list)-1]]
		regex = Expression(helpStringList,helpAlternatives)
		subExpressionList = []
		for alter in helpAlternatives:
			subExpressionList += getAlternativeNew(alter.getString(),alter.getMatchinglist())
		stringListAlter = []
		for ele1 in string_list:
			for ele2 in ele1:
				addAlternative = Alternative(ele2,computeMatchList([ele2]))
				addAlternative.setLambdaType(lambda_r(addAlternative))
				stringListAlter.append(addAlternative)
		subExpressionList += stringListAlter
		regex.setSubExpressionList(subExpressionList)
		st = printRegex(regex)
		print 'label: ', printRegex(y_regex[x.getID()]), '\nprediction: ', st, '\nFehler: ', loss(y_regex[x.getID()],regex,sparm), '\n####################################'
		return regex
	# find most violated constrained
	if flagLoss == 4:
		startall = time.time()
		out = [Alternative('[DUMMY]*',matching_list_x[a]) for a in range(number)]
		ret = [Alternative('[DUMMY]*',matching_list_x[a]) for a in range(number)]
		helpStringList = []
		helpAlternatives = []
		for a in range(number):
			replacement = getMaxRegex([],out[:],ret,string_list,a,fmvc,0.0,y,x,sm,sparm)
			# add strings to the stringList if replacement is of the form: string_1[]sring_2[]string_3, where string_1 or string_3 != '', 
			# for example: [hH]ttp:// : we have to add ttp:// to the next Stringlist
			# in: xyz[hH]: we have to add xyz to the previous stringlist
			if replacement.getStringlist()[0] != '':
				helpStringList[len(helpStringList)-1] = helpStringList[len(helpStringList)-1] + replacement.getStringlist()[0]
			if replacement.getStringlist()[len(replacement.getStringlist())-1] != '':
				string_list[a+1] = replacement.getStringlist()[len(replacement.getStringlist())-1] + string_list[a+1]
			helpStringList = helpStringList + string_list[a:a + 1] + replacement.getStringlist()[1:len(replacement.getStringlist())-1]
			helpAlternatives = helpAlternatives + replacement.getAlternatives()
			out[a].reset()
		helpStringList = helpStringList + [string_list[len(string_list)-1]]
		regex = Expression(helpStringList,helpAlternatives)
	subExpressionList = []
	for alter in helpAlternatives:
		subExpressionList += getAlternativeNew(alter.getString(),alter.getMatchinglist())
	stringListAlter = []
	for ele1 in string_list:
		for ele2 in ele1:
			addAlternative = Alternative(ele2,computeMatchList([ele2]))
			addAlternative.setLambdaType(lambda_r(addAlternative))
			stringListAlter.append(addAlternative)
	subExpressionList += stringListAlter
	regex.setSubExpressionList(subExpressionList)
	return regex
	

def psi(x, y, sm, sparm):
	values = calc_psi(y)
	svector = svmlight.create_svector(values)
	return svector

	
def print_struct_learning_stats(sample, sm, cset, alpha, sparm):
	predictions = [classify_struct_example(x,sm,sparm) for x,y in sample]
	losses = [loss(y,ybar,sparm) for (x,y),ybar in zip(sample,predictions)]
	print 'Average loss:',float(sum(losses))/len(losses)
#	print 'Model: ' , sm.w

def print_struct_testing_stats(sample, sm, sparm, teststats):
	print 'average loss: ', sum(teststats) / len(teststats)
#	saveModel(sm,'stratoPegasos')
#	print 'MODEL: ', sm.w

############################# Help Functions #################################################
'''
require:	a tuple of a list, wich determines what '(' groups a alternativ with depth one
			and the grouped regex 'regex_tuple'
			the MatchingList, for the alternatives of depth one 'matching_list'
ensure:		returns a list that contains the values of Psi(batch,regex)
'''
def calculate_attr_vec(y):
	global unitVector
	L_y = getListOfAllSingleAlternatives(y.getAlternatives())
	# initialize all values with zero:
	numberGetPossibilities = len(get_possiblilities())
	if unitVector:
		y_out = [0] * ((number_features * (number_types * len(get_possiblilities()))) + 10)
	else:
		y_out = [0] * ((number_features * number_types) + (number_features * number_specials) + 1)
	for a in range(len(L_y)):
		featureVector = []
		# skip dummy entries
		if (L_y[a].getString() == '[DUMMY]*') or (y.getTrain() == False and L_y[a].getNoLoss() == False and False) or L_y[a].getString() == '(.*)':
			continue
		type = L_y[a].getType()
		shortCutType = getShortcutType(L_y[a].getShortcut())
		score = 1.0
		start1 = time.time()
		maximum, minimum, dis, distinct, one = L_y[a].getMatchinglist().getMaxMinDistinctLength()
		
		# calculate the values for features
		#F_1:
		if minimum == 0:
			featureVector.append(1.0)
		else:
			featureVector.append(0.0)
		
		#NEW!!!!!!!!!!!!!!!!!
		featureVector.append(0.0)
			
		#F_3:
		if minimum <= 1 and maximum <= 1:
			featureVector.append(1.0)
		else:
			featureVector.append(0.0)
			
		#F_4:
		featureVector.append(dis)
		
		#F_5 and F_6:
		if type >= 6:
			liste = L_y[a].getAlterlist()
			dis = float(len(liste))
			len_match = float(len(L_y[a].getMatchinglist().getList()))
			if len_match != 0:
				add = 1.0 - (dis / len_match)
			else:
				add = 0.0
			featureVector.append(add)
			featureVector.append(one)
		else:
			featureVector.append(0.0)
			featureVector.append(0.0)
		specialList = []
		gAtoZ, sAtoZ, d0to9, gAtoF, sAtoF = L_y[a].getMatchinglist().getContainSpecials()
		
		#F_7:
		featureVector.append(gAtoZ / 26.0)	
		
		#F_8
		featureVector.append(sAtoZ / 26.0)
		
		#F_9
		featureVector.append(d0to9 / 10.0)
		
		#F_10:
		featureVector.append(gAtoF / 6.0)
		
		#F_11:
		featureVector.append((gAtoZ - gAtoF) / 20.0)

		#F_12:
		featureVector.append(sAtoF / 6.0)
		
		#F_13:
		featureVector.append((sAtoZ - sAtoF) / 20.0)
		
		#F_14:
		if gAtoZ == 0:
			featureVector.append(1.0)
		else:
			featureVector.append(0.0)
			
		#F_15:
		if sAtoZ == 0:
			featureVector.append(1.0)
		else:
			featureVector.append(0.0)
		
		#F_16:
		if gAtoF == 0:
			featureVector.append(1.0)
		else:
			featureVector.append(0.0)
			
		#F_17:
		if sAtoF == 0:
			featureVector.append(1.0)
		else:
			featureVector.append(0.0)
			
		#F_18:
		if d0to9 == 0:
			featureVector.append(1.0)
		else:
			featureVector.append(0.0)
		
		if unitVector:
			if type <= 5:
				for b in range(number_features):
					y_out[((((type - 1) * numberGetPossibilities) + shortCutType) * number_features) + b] += featureVector[b]
			else:
				for b in range(number_features):
					y_out[(5 * numberGetPossibilities * number_features) + ((type - 6) * number_features) + b] += featureVector[b]
		else:
			for b in range (number_features):
				y_out[((type - 1) * number_features) + b] += featureVector[b]
			for c in range(len(L_y[a].getShortcut())):
				if L_y[a].getShortcut()[c] == 1:
					for b in range(number_features):
						y_out[((number_types + c) * number_features) + b] += featureVector[b]	
	return y_out
		
'''
create list of possible replacemente for the (.*) in the regex 
'''
def createClassList(x):
	matching_list_x = x.getMatchinglist()
	number = x.getNumber()
	string_list = x.getStringlist()
#	out = [Alternative('[DUMMY]*',matching_list_x[a]) for a in range(number)]
	ret = [Alternative('[DUMMY]*',matching_list_x[a]) for a in range(number)]
	reList = []
	# computes a list wich contains for everey position a list of possible replacements for the .* of the alignment
	for position in range(number):
		start1 = time.time()
		classes_test = []
		distinct_list = matching_list_x[position].getAttrAlternatives()
		ccc = get_alternativ_string(distinct_list)
		start1 = time.time()
		
		# add regular expression in the form [aA][bB]c[dD]... if it is possible
		equalCaseInsensitive = checkCaseInsensitiveEqual(matching_list_x[position].getList())
#		print 'EQUAL: ', equalCaseInsensitive
		if equalCaseInsensitive:
			(listSensitive,brackNumber) = getEqualCaseInsensitiveRegex(matching_list_x[position].getList())
#			print 'list: ' + listSensitive
			reg = listSensitive
			#helpStringList = ['' for duu in range(brackNumber)]
			# check if the regExp reg matches the complete matchinglist
			if matchList(matching_list_x[position], reg) == True:
#				print 'reg: ', reg
				list,regex,stringlist, listMacro, regexMacro = match_regex.calculate_match_regex(reg)
#				print 'stringList: ', stringlist
				c = re.compile(regex,re.DOTALL)
#				print listMacro
#				print regexMacro
				match_list = []
				for a in range(len(list)):
					match_list.append([])
				for a in range(len(matching_list_x[position].getList())):
					for b in range(len(list)):
						m = c.match(matching_list_x[position].getList()[a])
						match_list[b].append(m.group(list[b]))
				match_List = []
				for a in range(len(match_list)):
					match_List.append(computeMatchList(match_list[a]))
				alternatives = getListOfAlternatives(listMacro, regexMacro, match_List)
				for a in range(len(alternatives)):
					if a == 0:
						alternatives[a].setBeginning(1)
					else:
						alternatives[a].setBeginning(0)
					alternatives[a].setNoLoss(x.getListNoLoss()[position])
					alternatives[a].setLambdaType(lambda_r(alternatives[a]))
				cl_test = Expression(stringlist,alternatives)
				subExpressionList = []
				for a in range(len(alternatives)):
					subExpressionList += getAlternativeNew(alternatives[a].getString(),alternatives[a].getMatchinglist())
				cl_test.setSubExpressionList(subExpressionList)
			#	print 'adde in createClassList: ', printRegex(cl_test)
				classes_test.append(cl_test)
		
		for b in range(7):
			help_type = b + 1
			if help_type < 6:
				listShortcut = get_possiblilities()
				for a in range(len(listShortcut)):
					in_brackets_string , altlist= get_strg_for_bracket(listShortcut[a],matching_list_x[position])
					regex = get_complete_test_regex_class([help_type],[in_brackets_string],[matching_list_x[position]],['',''], False)
					'''[\d] = \d and [\e] = \e'''
					if regex.count('\\d') == 1 or regex.count('\\e') == 1 or regex.count('[\\S]') == 1:
						regex = regex.replace('[','').replace(']','')
					alternative = Alternative(regex,matching_list_x[position],help_type, listShortcut[a],[],altlist)
					alternative.setNoLoss(x.getListNoLoss()[position])
					alternative.setBeginning(1)
					alternative.setLambdaType(lambda_r(alternative))								
					if matchList(matching_list_x[position], regex) == True:
						cl_test = Expression(['',''],[alternative])
						subExpressionList = getAlternativeNew(alternative.getString(),matching_list_x[position])		
						cl_test.setSubExpressionList(subExpressionList)
						#	print 'adde in createClassList: ', printRegex(cl_test)
						classes_test.append(cl_test)
			if help_type == 6:
				reg = ccc
				in_brackets_string = reg
				regex =  get_complete_test_regex_class([help_type],[in_brackets_string],[matching_list_x[position]],['',''], False)
				altlist = []
				for co in range(len(distinct_list)): altlist.append(saveSpecials(distinct_list[co]))
				alternative = Alternative(regex,matching_list_x[position],9, [ 0 for ttt in range(number_specials)],[],altlist)
				alternative.setNoLoss(x.getListNoLoss()[position])
				alternative.setBeginning(1)
				alternative.setLambdaType(lambda_r(alternative))
				# check if reg is two long
				if True and len(reg) < 1000 and len(distinct_list) < 16:
					cl_test = Expression(['',''],[alternative])
					subExpressionList = getAlternativeNew(alternative.getString(),alternative.getMatchinglist())
					cl_test.setSubExpressionList(subExpressionList)
				#	print 'adde in createClassList: ', printRegex(cl_test)
					classes_test.append(cl_test)
			# \S+( \S+){x,y}
			if help_type == 7:
				minWhite,maxWhite = get_number_of_whitespaces(matching_list_x[position].getList())
				# only \S+ is in help_type <= 5
				if minWhite == 0 and maxWhite == 0:
					continue
				# \S+( \S+){x} and \S+ \S+ respectively
				elif minWhite == maxWhite:
					if minWhite != 1:
						reg = '\S+( \S+){' + str(minWhite) + '}'
						helpStringList = ['','','']
					else:
						reg = '\S+ \S+'
						helpStringList = ['',' ','']
				# \S+( \S+)?
				elif minWhite == 0 and maxWhite == 1:
					reg = '\S+( \S+)?'
					helpStringList = ['','','']
				# \S+( \S+){x,y}
				else:
					reg = '\S+( \S+){' + str(minWhite) + ',' + str(maxWhite) + '}'
					helpStringList = ['','','']
				# check if the regExp reg matches the complete matchinglist
				if matchList(matching_list_x[position], reg) == True:
#					print 'reg: ', reg
					list,regex,stringlist, listMacro, regexMacro = match_regex.calculate_match_regex(reg)
					c = re.compile(regex,re.DOTALL)
#					print listMacro
#					print regexMacro
					match_list = []
					for a in range(len(list)):
						match_list.append([])
					for a in range(len(matching_list_x[position].getList())):
						for b in range(len(list)):
							m = c.match(matching_list_x[position].getList()[a])
							match_list[b].append(m.group(list[b]))
					match_List = []
					for a in range(len(match_list)):
						match_List.append(computeMatchList(match_list[a]))
					alternatives = getListOfAlternatives(listMacro, regexMacro, match_List)
					for a in range(len(alternatives)):
						if a == 0:
							alternatives[a].setBeginning(1)
						else:
							alternatives[a].setBeginning(0)
						alternatives[a].setNoLoss(x.getListNoLoss()[position])
						alternatives[a].setLambdaType(lambda_r(alternatives[a]))
				else:
					continue
				cl_test = Expression(helpStringList,alternatives)
				subExpressionList = []
				for a in range(len(alternatives)):
					subExpressionList += getAlternativeNew(alternatives[a].getString(),alternatives[a].getMatchinglist())
				cl_test.setSubExpressionList(subExpressionList)
			#	print 'adde in createClassList: ', printRegex(cl_test)
				classes_test.append(cl_test)
		reList.append(classes_test[:])
	return reList

'''
create list of losses for possible replacemente for the (.*) in the regex 
'''
def createLossList(x,y,classList,sparm):
	copyClassList = classList[:]
	number = x.getNumber()
	matching_list_x = x.getMatchinglist()
	string_list = x.getStringlist()
	reList = []
#	print 'real: ', printRegex(y)
	for position in range(number):
		list = copyClassList[x.getID()][position][:]
		alt = [Alternative('[DUMMY]*',matching_list_x[a]) for a in range(number)]
		errorList = []
		liste = []
		for ddcount in range(len(list)):			
			altList = list[ddcount].getAlternatives()
			# for example \S+( \S+)+, \S+( \S+)*, ...
			if len(altList) == 2:
				alt[position] = altList[0]
				alt = alt[:position + 1] + [altList[1]] + alt[position + 1:]
				copyStringList = string_list[:]
				# case: \S+ \S+
				if altList[0].getString() == '\\S+' and altList[1].getString() == '\\S+':
				#	print 'bin hier'
					copyStringList = copyStringList[:position + 1] + [' '] + copyStringList[position + 1:]
				else:
					copyStringList = copyStringList[:position + 1] + [''] + copyStringList[position + 1:]
				ybar_reg = Expression(copyStringList,alt[:])
				ybar_reg.setDummy(position)
			else:
			#	for ttcount in range(len(list)):
			#		print 'alternatives: ', list[ttcount].getAlternatives()
			#	print 'parameter; position: ', position, ' ddcount: ', ddcount, ' len(list): ', len(list), ' num. alternatives: ', len(list[ddcount].getAlternatives()) 
				alt[position] = list[ddcount].getAlternatives()[0]
				ybar_reg = Expression(string_list,alt[:])
				ybar_reg.setDummy(position)
		#	print 'here we are: ', alt[position].getString(), 'len: ', len(list[ddcount].getAlternatives()), 'stringList: ', string_list
			error = loss(y, ybar_reg,sparm,position)
		#	print 'regex: ', printRegex(ybar_reg), 'loss: ', error
			liste.append(error)						
		errorList.append(liste)
		newLoss = Loss(errorList)
		reList.append(newLoss)
	return reList

'''
require:	regular expression 'string'
ensure:		returns the number of alternatives in the regular expression
'''	
def get_insert_regex(strg):
	#print 'regex: ', strg
	count1 = strg.count('(')
	count2 = strg.count('\(')
	count3 = strg.count('[')
	count4 = strg.count('\[')
	re = (count1 - count2) + (count3 - count4)	
	#print re
	return re - 1
	
	
# returns a number wich represents the type of the regex, and an number wich represents, 
#how many strings from the matching list is matched and other values 
#(see phi_vector.txt for details)
# 1 = []*, 2 = []+, 3 = []?, 4 = []{}, 5 = []{,}
# 6 = (|) , 7 = (|)reg 8 = (|)*, 9 = (|)+, 10 = (|)?, 11 = (|){}, 12 = (|){,}
# 12 = ()*, 13 = ()+, 14 = ()?, 15 = (){}, 16 = (){,}

'''
require:	a regular expression 'regex'
			the MatchingList for the regex 'matching_list'
ensure:		returns a tuple consists of the type of the 'regex' and
			the percentage, how many strings of 'maching_list'
			are matched
'''
def get_type_and_score(regex, matching_list):
#	print 'regex 1131: ',  regex
	#print 'matching_list: ', matching_list
	#print allo
	matching_list = matching_list[:len(matching_list) - extra_parameters]
	c1 = re.compile('\[.+\]',re.DOTALL)
	#c8 = re.compile('\([.^|]+\)',re.DOTALL)
	c9 = re.compile('\(.+|.+\)',re.DOTALL)
#	print 're: ', regex
#	print 'matchList: ', matching_list
	c7 = re.compile(replaceSpecials(regex))
	count = 0
	for a in range(len(matching_list)):
		if c7.match(matching_list[a]):
			count = count + 1
	try:
		per = float(count / len(matching_list))
	except:
		per = 0
	if c1.match(regex) is not None:
		type5 = re.compile('\[.+\]\{\d+,\d+\}', re.DOTALL)
		type4 = re.compile('\[.+\]\{\d+\}', re.DOTALL)
		type2 = re.compile('\[.+\]\+', re.DOTALL)
		type3 = re.compile('\[.+\]\?', re.DOTALL)
		type1 = re.compile('\[.+\]\*', re.DOTALL)
		typedummy = re.compile('\[DUMMY\]\*', re.DOTALL)
		# type 0
		if typedummy.match(regex) is not None:			
			return 0, 0
		# type 3
		if type5.match(regex) is not None:			
			return 5, per
		# type 4
		elif type4.match(regex) is not None:
			return 4, per
		# type 2
		elif type2.match(regex) is not None:
			return 2, per
		#type 3
		elif type3.match(regex) is not None:
			return 3, per
		#type 1
		elif type1.match(regex) is not None:
			return 1, per
		else:
			return 4, per			
	elif c9.match(regex) is not None:
		c2 = re.compile('\(.+\|.+\)(\{\d+,\d+\})', re.DOTALL)
		c3 = re.compile('\(.+\|.+\)\{\d+\}', re.DOTALL)
		c4 = re.compile('\(.+\|.+\)\+', re.DOTALL)
		c5 = re.compile('\(.+\|.+\)\?', re.DOTALL)
		c6 = re.compile('\(.+\|.+\)\*', re.DOTALL)
		# type 10
		if c2.match(regex) is not None:
			return 10, per
		# type 9
		elif c3.match(regex) is not None:
			return 9, per
		# type 7
		elif c4.match(regex) is not None:
			return 7, per
		#type 8
		elif c5.match(regex) is not None:
			return 8, per
		#type 6
		elif c6.match(regex) is not None:
			return 6, per
		else:
			return 9, per
	# macroType
	elif regex[0] == '$':
		return 11, 1.0
	elif regex[0] == '\\':
		#special character
		'''\\l = \r?'''
		if regex == '\\l':
			return 3, per
		append = parse_regex.find_append(1,regex)
#		print 'ausdruck: ', regex, 'appedn: ', append
		if append == '':
			return 4, per
		elif append == '+':
			return 2, per
		elif append == '*':
			return 1, per
		elif append == '?':
			return 3, per
		elif append.count('{'):
			if append.count(','):
				return 5, per
			else:
				return 4, per
	return 0,0
'''
require:	a MatchingList for one alternative 'matching_list'
ensure:		returns a tuple, wich consits of 5 components:
				max: length of the longest string in 'matching_list'
				min: length of the shortest string in 'mtaching_list'
				dis: 1 iff all strings in 'matching_list' have same length, otherwise 0
				len(distinct): counts the distinct length of the strings in 'matching_list'
				one: 1 iff 'matching_list' includes only strings with length 1
'''
def get_max_min_distinct_length(matching_list):
	b = 0
	for a in range(len(matching_list)):
		if type(matching_list[len(matching_list) - (a +1)]) == list:
			b += 1
		else:
			break
	matching_list = matching_list[:len(matching_list) - b]
#	print matching_list
	max = -1
	min = 1000000
	distinct = set()
	one = 1.0
	for a in range(len(matching_list)):		
		length = len(matching_list[a])
		start1 = time.time()
		distinct.add(length)
		if length > max:
			max = length
		if length < min:
			min = length
		if length != 1:
			one = 0.0
	if len(distinct) == 1:
		dis = 1
	else:
		dis = 0
	return float(max), float(min), float(dis), float(len(distinct)), float(one)


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
		list.append(regex[begin:begin + idx].replace('\\\\','\\'))
		idx2 = regex[begin:].find('})')#parse_regex.get_index_close(0,regex[begin:])
		begin = begin + idx2 + 2
	list.append(regex[begin:].replace('\\\\','\\'))
	return list
	
	
'''
require:	list of distinct strings 'distinct_list'
ensure:		returns the alternativ with all the strings of 'distinct_list'
'''	
def get_alternativ_string(distinct_list):
#	print 'distinct_list: ', distinct_list
	"""
	# wird denke ich nicht mehr gebraucht
	list_histo = []
	list_regex = []
	match = []
	for a in range(len(distinct_list)): list_histo.append(0)
	for a in range(len(matching_list)):
		try:
			idx = distinct_list.index(matching_list[a])
			list_histo[idx] += 1
		except:
			print 'error in get_alternativ_string'
			print 'bei : ', matching_list[a]
	for a in range(len(list_histo)):
		if list_histo[a] > 1 and len(distinct_list[a]) > 1: 
			list_regex.append((distinct_list[a], []))
		else:
			match.append(distinct_list[a])
	regex = '(.*)'
	match.append(get_distinct_character_set(match))
	match.append(get_attr_alternatives(match))
	x = (regex,match)
	if len(match) > 2:
		list_regex.append(x)
	"""
	re = ''
	if len(distinct_list) != 0:
		for a in range(len(distinct_list) - 1):	re = re + str(distinct_list[a]) + '|'
		re = re + str(distinct_list[len(distinct_list) - 1])
	# replace special characters
	re = re.replace('(','\(')
	re = re.replace(')','\)')
	re = re.replace('[','\[')
	re = re.replace(']','\]')
	re = re.replace('$','\$')
	re = re.replace('.','\.')
	re = re.replace('?','\?')
	re = re.replace('@','\@')
	re = re.replace('+','\+')
	re = re.replace('^','\\^')
	re = '(' + re + ')'
	return re
	

	
'''
require:	a list wich determines wich types the regex contain 'type_list'
			a list wich determines what string is in the regex of 'typelist' 'in_brackets_list'
			the matchinglist for all alternatives of depth 1 'matching_list'
			a flag wich determines whether the whole regex or only the alternativ is returned
			a flag wich determines whether 'type_list' is a StringList or a list of numbers
ensure:		returns the regex wicht the types determed by 'type_list'
'''	
def get_complete_test_regex_class(type_list,in_brackets_list,matching_list,string_list, onlyOne = True, allStrings = False):
	if not allStrings:
		re = string_list[0]
		for a in range(len(type_list)):
			if type_list[a] == 1:
				re = re + '['+in_brackets_list[a]+']*'
				if onlyOne == False:
					return '['+in_brackets_list[a]+']*'
			elif type_list[a] == 2:
				re = re + '['+in_brackets_list[a]+']+'
				if onlyOne == False:
					return '['+in_brackets_list[a]+']+'
			elif type_list[a] == 3:
				re = re + '['+in_brackets_list[a]+']?'
				if onlyOne == False:
					return '['+in_brackets_list[a]+']?'
			elif type_list[a] == 4:
				c = len(matching_list[a].getList()[0])
				if c == 1:
					re = re + '['+in_brackets_list[a]+']'
					if onlyOne == False:
						return '['+in_brackets_list[a]+']'
				else:
					re = re + '['+in_brackets_list[a]+']{'+ str(c) +'}'
					if onlyOne == False:
						return '['+in_brackets_list[a]+']{'+ str(c) +'}'
			elif type_list[a] == 5:
				max, min, dis, dist, one = get_max_min_distinct_length(matching_list[a].getList())
				max = int(max)
				min = int(min)
				re = re + '['+ in_brackets_list[a] +']{' + str(min) + ',' + str(max) +'}'
				if onlyOne == False:
						return '['+ in_brackets_list[a] +']{' + str(min) + ',' + str(max) +'}'
			elif type_list[a] == 6 or type_list[a] == 7:
				re = re + in_brackets_list[a]
				if onlyOne == False:
						return in_brackets_list[a]
			elif type_list[a] == 0:
				re = re + '[DUMMY]*'
			re = re + string_list[a + 1]
	else:
		re = string_list[0]
		for a in range(len(type_list)):
			re = re + type_list[a].getString()
			re = re + string_list[a + 1]
	return re



	
'''
require:	matching_list is a list of strings
ensure:		list of distinct strings of matching_list
'''			
def get_distinct_character_set(matching_list):
	distinct_character = set()
	dis = []
	for a in range(len(matching_list)):
		for b in range(len(matching_list[a])):
			distinct_character.add(matching_list[a][b])
	for a in range(len(distinct_character)):
		dis.append(distinct_character.pop())
	return dis
	
'''
require:	distinct is a list of distinct characters
ensure:		tuple (A-Z,a-z,0-9,A-F,a-f) wich specifies how many
			characters of the form A-Z etc.
'''
def get_number_character_class(distinct):
	gAtoZ = 0
	sAtoZ = 0
	d0to9 = 0
	gAtoF = 0
	sAtoF = 0
	for a in range(len(distinct)):
		strg = distinct[a]
		if string.uppercase.count(strg) > 0:
			gAtoZ += 1
			if string.uppercase[:6].count(strg) > 0:
				gAtoF += 1
		elif string.lowercase.count(strg) > 0:
			sAtoZ += 1
			if string.lowercase[:6].count(strg) > 0:
				sAtoF += 1
		elif string.digits.count(strg) > 0:
			d0to9 += 1
	return float(gAtoZ), float(sAtoZ), float(d0to9), float(gAtoF), float(sAtoF)
	
'''
require:	string str
ensure:		string with the saved specials: \@ ....
'''
def saveSpecials(str):
	return str.replace('(','\(').replace(')','\)').replace('[','\[').replace(']','\]').replace('$','\$').replace('.','\.').replace('?','\?').replace('@','\@').replace('-','\-').replace('+','\+')
	
'''
require:	number_list wich specifies wich specials we have to add
				[0,1,2,3,4]
				0: A-Z
				1: a-z
				2: 0-9
				3: A-F
				4: a-f
			distinct is a list of distinct strings we have to add
ensure:		string wich contains the specials from number_list and the
			characters of distinct, iff they can not constructed from 
			the specials of number_list
'''	
def get_strg_for_bracket(number_list,distinct):
#	out_set = set(distinct)
	distinct = distinct.getDistinctCharacterSet()
#	print 'DISTINCT: ', distinct
	out_set = set()
	re = ''
	for a in range(len(distinct)):
		if distinct[a] == '\\':
			re = re + '\\\\'
		else:
			re = re + str(distinct[a])
		out_set.add(str(distinct[a]).replace('(','\(').replace(')','\)').replace('[','\[').replace(']','\]').replace('$','\$').replace('.','\.').replace('?','\?').replace('@','\@').replace('-','\-').replace('+','\+').replace('^','\^'))
	re = re.replace('(','\(')
	re = re.replace(')','\)')
	re = re.replace('[','\[')
	re = re.replace(']','\]')
	re = re.replace('$','\$')
	re = re.replace('.','\.')
	re = re.replace('?','\?')
	re = re.replace('@','\@')
	re = re.replace('-','\-')
	re = re.replace('+','\+')
	re = re.replace('^','\^')
	if number_list[0] == 1:
		strg = string.uppercase
		for b in range(len(strg)):
			re = re.replace(strg[b],'')
		re = re + 'A-Z'
		out_set = out_set.difference(set(string.uppercase))
		out_set.add('[A-Z]')
	if number_list[1] == 1:
		strg = string.lowercase
		for b in range(len(strg)):
			re =re.replace(strg[b],'')
		re = re + 'a-z'
		out_set = out_set.difference(set(string.lowercase))
		out_set.add('[a-z]')
	if number_list[2] == 1:
		strg = string.digits
		for b in range(len(strg)):
			re =re.replace(strg[b],'')
		re = re + '0-9'	
		out_set = out_set.difference(set(string.digits))
		out_set.add('[0-9]')
	if number_list[3] == 1:
		strg = string.uppercase[:6]
		if re.count('A-Z') > 0:
			strg = string.uppercase[1:6]
		for b in range(len(strg)):
			re =re.replace(strg[b],'')
		re = re + 'A-F'
		out_set = out_set.difference(set(string.uppercase[1:6]))
		out_set.add('[A-F]')
	if number_list[4] == 1:
		strg = string.lowercase[:6]
		if re.count('a-z') > 0:
			strg = string.lowercase[1:6]
		for b in range(len(strg)):
			re =re.replace(strg[b],'')
		re = re + 'a-f'
		out_set = out_set.difference(set(string.lowercase[1:6]))
		out_set.add('[a-f]')
	if number_list[5] == 1:
		re = '\\e'
		out_set = set('\\e')
	if number_list[6] == 1:
		re = '\\S'
		out_set = out_set.intersection(set([' ','\t','\n','\r','\f','\v']))
		helpList = list(out_set)
		out_set.add('\\S')
		for b in range(len(helpList)):
			re = re + helpList[b]
	if re == '0-9':
		re = '\\d'
	return re, list(out_set)
	
'''
require:	matching_list is a list of strings
ensure:		list of distinct strings of matching_list
'''
def get_attr_alternatives(matching_list):
	b = 0
	for a in range(len(matching_list)):
		if type(matching_list[len(matching_list) - (a +1)]) == list:
			b += 1
		else:
			break
	matching_list = matching_list[:len(matching_list) - b]
	dis_set = []
	for a in range(len(matching_list)):
		if dis_set.count(matching_list[a]) == 0:
			dis_set.append(matching_list[a])
	return dis_set
	
'''
require:	dis_set is a set of strings
ensure:		number of strings in dis_set with lenth zero
'''
def get_number_length_one(dis_set):
	count = 0
	for a in range(len(dis_set)):
		if len(dis_set[a]) == 1:
			count += 1
	return count


'''
ensures: list with all combinations of the special types
			[a,b,c,d,e]
				a: A-Z
				b: a-z
				c: 0-9
				d: A-F
				e: a-f
'''
def get_possiblilities():
	list = []
	for a in range(2):
		for b in range(2):
			for c in range(2):
				for d in range(2):
					for e in range(2):						
						#postprocessing: delete nonrelevant combinations
						if not ((a == 1 and d == 1) or (b == 1 and e == 1)):
				#			# a-f or A-F only in combination with 0-9
							if not ((d == 1 or e == 1) and c == 0):
				#				print 'JA: ', string
								list.append([a,b,c,d,e,0,0])
						

	list.append([0,0,0,0,0,1,0])
	list.append([0,0,0,0,0,0,1])
	return list
	
'''
require:	brack_list is a list wich specifies wich brackets ( are grouping ones
			regex is a regex with grouping brackets (example ab([Ii])cd)
			fr specifies at wich grouping bracket we have to start
			to specifies at wich grouping bracket we have to stop
ensures:	part of regex from grouped bracket fr til grouped bracket to
'''
def getRegex(brack_list,regex,fr,to):
	if fr == 0:
		begin = 0
		if to == len(brack_list): return regex
		for a in range(brack_list[to]):
			idx = parse_regex.get_index_open(0,regex[begin:])
			begin = begin + idx + 1			
		return regex[:begin - 1]
	else:
		begin = 0
		for a in range(brack_list[fr - 1]):
			idx = parse_regex.get_index_open(0,regex[begin:])
			begin = begin + idx + 1
		brack = 0
		for ca in range(len(regex[begin:])):
			if regex[begin:][ca] == ')':
				if ca > 0:
					if regex[begin:][ca-1] != '\\':
						if brack == 0: break
						else: brack -= 1
				else:
					brack -= 1				
			if regex[begin:][ca] == '(': 
				if ca > 0:
					if regex[begin:][ca-1] != '\\':
						brack +=1
				else:
					brack += 1
		ca = ca + parse_regex.get_index_open(0,regex[begin + ca + 1:])
		begin3 = 0
		if to == len(brack_list):
			return regex[begin + ca + 1:]			
		for a in range(brack_list[to]):
			idx = parse_regex.get_index_open(0,regex[begin3:])
			begin3 = begin3 + idx + 1
		return regex[begin + ca +1:begin3 - 1]
			
'''
require:	regex with grouping brackets (example ab([Ii])cd)
ensure:		regex without grouping brackets
'''			
def removeGroupingBrackets(regex):
	while True:
		ret = 0
		brack = 0
		for a in range(len(regex)):
			if regex[a] == '(':
				if a > 0:
					if regex[a-1] != '\\':
						brack += 1
				else:
					brack += 1
				if a+2 < len(regex) and brack > 0:
					if regex[a + 1] == '(' or regex[a + 1] == '[':
						idx1 = a
						ret = 1		
					elif regex[a + 1] == '\\':
						if regex[a + 2] == 'W' or regex[a + 2] == 'w' or regex[a + 2] == 's' or regex[a + 2] == 'S' or regex[a + 2] == 'D' or regex[a + 2] == 'd':
							idx1 = a
							ret = 1
			elif regex[a] == ')':			
				if a - 1 >= 0:
					if regex[a - 1] != '\\':
						brack -= 1
						if brack == 0 and ret == 1:
							idx2 = a
							break
		if ret == 1: regex = regex[:idx1]+regex[idx1 +1:idx2]+regex[idx2+ 1:]
		else: break
	return regex
	
	
'''
require:	regex y and ybar we have to compare
ensure:		HammingLoss
http://www.cs.rochester.edu/~zhangchl/publications/ictai06.pdf
'''
def lossRegex(y,ybar):
#	print 'lossRegex'
#	if printRegex(ybar).count('DUMMY') == 0:		
#		print 'vergleiche: ', printRegex(y), 'mit: ', printRegex(ybar)
#		if y.getID() == 10:
#			print allo
#	print 'y: ', printRegex(y)
#	print 'erster Typ: ', y.getAlternatives()[0].getType(),'zweiter Typ: ', ybar.getAlternatives()[0].getType()
	L_y = getListOfAllSingleAlternatives(y.getAlternatives())
	L_ybar = getListOfAllSingleAlternatives(ybar.getAlternatives())
	numberMatchAll = 0
#	for a in range(len(L_y)):
#		print L_y[a].getString()
#	for a in range(len(L_ybar)):
#		print L_ybar[a].getString()
	ylist_type = []
	ybarlist_type = []
	for b in range(number_types):
		ylist_type.append(0)
		ybarlist_type.append(0)
	y_special = [0 for a in range(number_specials)]
	ybar_special = [0 for a in range(number_specials)]
#	print '###############################################'
	for a in range(len(L_y)):
		if L_y[a].getString() == '(.*)':
			numberMatchAll += 1
#		else:
#			if printRegex(ybar).count('DUMMY') == 0:
#				print '\n\n betrachte: ', L_y[a].getString(), 'mit Typ: ', L_y[a].getType()
		#(one,two) = getTypeAppend(L_y[a].getString())
		#one = 
		
		#print 'one: ', one, 'two: ', two
		#print 'type: ', L_y[a].getType()
#		print 'y ', L_y[a].getString() , 'mit Type: ', L_y[a].getType()
		if L_y[a].getString() != '(.*)':
			ylist_type[L_y[a].getType() - 1] += 1
		for b in range(number_specials):
			y_special[b] += L_y[a].getShortcut()[b]
	if ylist_type[8] == numberMatchAll and numberMatchAll > 2:
		return 0.0
#	ylist_type[8] -= numberMatchAll	
#	if sum(ylist_type) > 0:
#		print printRegex(y)
#		print 'Liste: ', ylist_type
#		print 'shortcutList: ', y_special
#		print allo
#	print '########################################################'
#	print ybarlist_type
	for a in range(len(L_ybar)):
		if L_ybar[a].getNoLoss() == False:
#			if printRegex(ybar).count('DUMMY') == 0:
#				print 'skippe ybar ', L_ybar[a].getString() , 'mit Type: ', L_ybar[a].getType()
			continue
		#(one,two) = getTypeAppend(L_ybar[a].getString())
#		print 'ybar ', L_ybar[a].getString() , 'mit Type: ', L_ybar[a].getType()
		ybarlist_type[L_ybar[a].getType() - 1] += 1
		for b in range(number_specials):
			ybar_special[b] += L_ybar[a].getShortcut()[b]
#	print '###############################'
#	print 'y: ', ylist_type
#	print 'ybar: ', ybarlist_type
#	print 'special y: ', y_special
#	print 'special ybar: ', ybar_special
	error = 0.0
	y_labels =  sum(ylist_type) + sum(y_special)
	ybar_labels = sum(ybarlist_type) + sum(ybar_special)
	#classnumber = y_labels + ybar_labels
	#classnumber = (len(ylist_type)) + number_specials
	classnumber = 0
	for b in range(len(ylist_type)):
		error += abs(ylist_type[b] - ybarlist_type[b])
		classnumber += max(ylist_type[b],ybarlist_type[b])
	for b in range(number_specials):
		error += abs(ybar_special[b] - y_special[b])
		classnumber += max(ybar_special[b],y_special[b])
	if classnumber != 0:
		error = float(error / float(classnumber))
	else:
		error = 0.0
#	print L_y[0].getString(), 'mit: ', y_special
#	print L_ybar[0].getString(), 'mit: ', ybar_special
#	print 'ausgabe: ', error, 'fuer: ', printRegex(y), 'und: ', printRegex(ybar)
	return error
	
'''	
require:	regex wich is a alternaiv (example [Ii])	
ensures:	a tuple one, two where:
			one: specifies the type of alternative:
				1: [
				2: (
				3: \
			two: specifies the type of quantor:
				1: *
				2: +
				3: ?
				4: {x}
				5: {x,y}
				6: none
'''
def getTypeAppend(regex):
	one = -1
	two = -1
	if regex[0] == '[':
		one = 1
		idx = regex.rfind(']')		
	elif regex[0] == '(':
		one = 2
		idx = regex.rfind(')')
	elif regex[0] == '\\':
		one = 3
		idx = 2
	append = parse_regex.find_append(idx, regex)
	if   append == '*' : two = 1
	elif append == '+' : two = 2
	elif append == '?' : two = 3
	elif append.count('{') > 0 and append.count(',') == 0: two = 4
	elif append.count('{') > 0 and append.count(',') == 1: two = 5
	else: two = 4
	return one,two

'''
require:	regex of the alignment
			matchList for the alignment-regex
			fr specifies at wich (.*) of regex we start to create the string
 			to specifies at wich (.*) of regex we end to create the string
			number specifies wich string of the batch we create (x^number)
ensure:		string of the text x^number from fr to to where the (.*) are replaced with
			the strings of the matchingList
'''
def getMatchString(regex,matchList,fr,to,number):
	begin = 0
	idx1 = 0
	for a in range(fr):
		idx1 = regex[begin:].find('(.*)')
		begin = begin + idx1 + 1
	idx1 = begin
	if fr == 1: idx1 = 1
	begin = 0
	for a in range(to):
		idx2 = regex[begin:].find('(.*)')
		begin = begin + idx2 + 1
	idx2 = begin
	if (to - 1)  == regex.count('(.*)'):
		reg = regex[idx1- 1:]
	else:
		reg =  regex[idx1 - 1: + idx2-1]
	for a in range((to - fr)):
		idx = reg.find('(.*)')
		reg = reg[:idx] + matchList[(fr-1) + a][number] + reg[idx + 4:]
	return reg
'''	
 returns true iff regex matches all strings in the list MatchList
 require: Matchinglist MatchList, regular expression regex
 ensure: returns true if regex matches the MatchList, ohterwise false
'''
def matchList(MatchList,regex):
	ret = True
	list = MatchList.getList()
#	print 'regex: ', regex, 'Liste: ', list
	try:
		c = re.compile(replaceSpecials(regex),re.DOTALL)
	except:
		print 'regex: ', regex, 'Liste: ', list
		c = re.compile('.*',re.DOTALL)
		print allo
	for a in range(len(list)):
		m = c.match(list[a])
		if m is None:
			ret = False
#			print 'Matcht nicht: ', list[a]
			break
		else:
			if m.group(0) != list[a]:
#				print 'matcht nicht: ', list[a], 'gegen: ', m.group(0)
				ret = False
				break
	return ret
'''
 require: 	list wich opening bracket ( is the start of a new alternvative with depth 1
			grouped regular expression regex (the alternatives with depth 1 are in brackets)
 ensure: 	returns a list L_regex wich contains all the alternatives of the regular expression
'''
def getListOfAlternatives(list,regex, matchingList):
#	print 'match: ', matchingList[0].getList()
#	print 'list: ', list
#	print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
#	print 'regex: ', regex
	retList = []
	matchList = []
	# for all alternatives with depth 0 add this and the containing alternatives to the list
	for a in range(len(list)):
		begin = 0
		# dont consider the \(
		helpRegex = regex.replace('\\(','AA')
		#helpRegex = regex.replace('\\)','AA')
		for b in range(list[a]):
			idx = helpRegex[begin:].find('(')
			begin = begin + idx + 1
		idx = begin - 1		
		innerRegex = parse_regex.find_in_brackets(0,idx,regex)
		innerRegex =  innerRegex[1:len(innerRegex)-1]
	#	print 'INNER REGEX: ', innerRegex
	#	if len(matchingList) == 2:
#		print 'innerRegex: ', innerRegex, matchingList[a].getList()		
		alt = getAlternative(innerRegex,matchingList[a])
		retList.append(alt)
	return retList
	

'''
require:	alternative-string 'regex' and the Matching-List 'matchingList' for this alternativ
ensure:		creates an object from type 'Alternative', with all containing alternatives
'''	
def getAlternative(regex, matchingList):
	list = matchingList.getList()
	type, dummy = get_type_and_score(regex,[])
#	print 'Type: ', type, 'for: ', regex
	str = regex
	shortcut = [0 for a in range(len(shortCutList))]
	alterlist = None
	if type >= 1 and type <= 5:
		for a in range(len(shortCutList)):
			if regex.count(shortCutList[a]) > 0:
				shortcut[a] = 1
		if regex.count('\\d') > 0:
			shortcut[2] = 1
		if regex.count('\\S') > 0:
			shortcut[6] = 1
		if regex.count('\\e') > 0:
			shortcut[5] = 1
		all = getAlternativesEasyType(regex[1:regex.rfind(']')])
	else:
		all, alterlist = getListSubalternatives(str[str.find('(') + 1:str.rfind(')')])
	alt = Alternative(str,matchingList,type,shortcut,[],all)
	if type >= 6 and type <= 10:
#		print 'AlterList: ', alterlist
		regNeu = parse_regex.get_in_brackets(0,regex)
		append = parse_regex.find_append(len(regNeu),regex)
		regNeu = regNeu[1:]
		li, reg, dummy, listeMacro, regexMacro = match_regex.calculate_match_regex(regNeu)
		c1 = re.compile('(' + replaceSpecials(reg) + ')' + append,re.DOTALL)
		newList = []
		for d in range(len(li)):
			newList.append([])
		for d in range(len(list)):
			m1 = c1.match(list[d])
			if m1 is not None:# and m1.group(0) == list[d]:
				for b in range(len(li)):
					if m1.group(li[b] + 1) is not None:
						newList[b].append(m1.group(li[b] + 1))
			else:
				print 'matchte: ', replaceSpecials(reg),  'Ausgabe: ', list[d]
				print allo
		listNew = []
		for c in range(len(newList)):
			help = MatchingList(newList[c])
			help.setDistinctCharacterSet(get_distinct_character_set(newList[c]))
			help.setAttrAlternatives(get_attr_alternatives(newList[c]))
			help.setMaxMinDistinctLength(get_max_min_distinct_length(newList[c]))
			gAtoZ, sAtoZ, d0to9, gAtoF, sAtoF = get_number_character_class(help.getDistinctCharacterSet())
			help.setContainSpecials((gAtoZ, sAtoZ, d0to9, gAtoF, sAtoF))
			listNew.append(help)
#		print li, reg, listNew
		if len(li) > 0:
#			print 'naechster Schritt: ', listeMacro, regexMacro
			alter = getListOfAlternatives(listeMacro,regexMacro,listNew)
			for a in range(len(alter)):
#				print 'fuege hinzu: ', alter[a].getString()
				alt.addAlternative(alter[a])
	return alt
	
	
'''
require:	a list of alternatives
ensure:		returns a list wich contains all alternatives and their containing alternatives
'''
def getListOfAllSingleAlternatives(AlternativeList):
	retList = []
	for a in range(len(AlternativeList)):
		retList.append(AlternativeList[a])
		if AlternativeList[a].getContain() != []:
			retList = retList + getListOfAllSingleAlternatives(AlternativeList[a].getContain())
	return retList
				
				
'''	
 require:	regex like: a|b|c|d|e
 ensure:	returns list of subalternatives: all_list: [a,b,c,d,e], and the list of subalternatives who contain a alternativ
'''
def getListSubalternatives(regex):
	number , modified_regex = parse_tree.countAlternatives(regex)
	reg_list = []
	all_list = []
	begin = 0
	for i in range(number):
		idx = modified_regex[begin:].find('|')
		str = regex[begin:begin + idx]
		str = str.replace('\\(','').replace('\\)','').replace('\\[','').replace('\\]','').replace('\\$','')
		# check if there is a sub_alternative
		if not( str.count('[') == 0 and str.count('(') == 0 and str.count('$') == 0):
			reg_list.append(regex[begin:begin + idx])
		all_list.append(regex[begin:begin + idx])
		begin = begin + idx + 1
	str = regex[begin:]
	str = str.replace('\\(','').replace('\\)','').replace('\\[','').replace('\\]','').replace('\\$','')
	if not( str.count('[') == 0 and str.count('(') == 0 and str.count('$') == 0):
			reg_list.append(regex[begin:])	
	all_list.append(regex[begin:])
	return all_list,reg_list

'''
require:	position of .* where we have to choose the SpecialList
			alt: list of alternatives
			fmv: true if we have to find the find most violated constrained, false otherwise
			value: the score of the other alternatives, except the alternative with position 'position'
			y: real regex
			x: train data : class Batch
			sm, sparm: parameters for the current weightvector
ensure:	list of specials wich have the highest score
'''
def getMaxSpecialList(position,alt,fmvc,value,y,x,sm,sparm):
	start = time.time()
	number = x.getNumber()
	number_specials = 5
	list_poss = get_possiblilities()
	help_list = [0 for a in range(number_specials)]
	string_list = x.getStringlist()
	matching_list_x = x.getMatchinglist()
	score_list = []
	help_classes = []
	help_test = []
	start = time.time()
	test = []
	for count in range(len(list_poss)):
		in_brackets_string, altlist = get_strg_for_bracket(list_poss[count],matching_list_x[position])
		# control if \e matches all the strings in the matchList
		if list_poss[count] == [0,0,0,0,0,1,0]:
			# set dummy if it does not match the whole matchingList
			if not matching_list_x[position].getMatchesEPlus():
				in_brackets_string, altlist = get_strg_for_bracket(list_poss[0],matching_list_x[position])
				list_poss[count] = list_poss[0]
		''' [0-9]* = \d* '''
		if in_brackets_string == '\\d' or in_brackets_string == '\\e' or in_brackets_string == '\\S':
			st = in_brackets_string + '*'
		else:
			st = '[' + in_brackets_string + ']*'
		alt[position] = Alternative(st,matching_list_x[position], 1, list_poss[count],[],altlist)
		if fmvc:
			alt[position].setNoLoss(x.getListNoLoss()[position])	
		cl = Expression(string_list,alt[:])
		cl.setDummy(position)
		help_classes.append(cl)
		cl_test = Expression('dummy',[alt[position]])
		help_test.append(cl_test)
	help_v = [(psi(x,c,sm,sparm),c) for c in help_test]
	help_predictions = [(svmlight.classify_example(sm, p),c) for p,c in help_v]
	if fmvc == True	:
		for aaa in range(len(y_regex)):
			if y == y_regex[aaa]: break
		flagError = False
		errorList = []
		for bbb in range(len(list_loss[aaa][position])):
			errorList = list_loss[aaa][position][bbb].getErrorList()
			if len(errorList) > 0:
				flagError = True
			break
		if not flagError:
			list = []
			for ddcount in range(len(help_predictions)):
				score, reg = help_predictions[ddcount]					
				ybar_reg = help_classes[ddcount]
				error = loss(y, ybar_reg,sparm,position)
				list.append(error)						
				score = score + error
				help_predictions[ddcount] = (score, reg)
			errorList.append(list)
			newLoss = Loss(errorList)
			list_loss[aaa][position].append(newLoss)
		else:
			for ddcount in range(len(help_predictions)):
				score, reg = help_predictions[ddcount]	
				score = score + errorList[0][ddcount]
				help_predictions[ddcount] = (score, reg)		
	help = help_test.index(max(help_predictions)[1])
	help_list = list_poss[help]
	return help_list


'''
require: 	special_list of specials with the highest score
			position of .* where we have to choose the SpecialList
			alt: list of alternatives
			curReg: current List of Alternatives
			stringList: current StringList for the regex
			fmv: true if we have to find the find most violated constrained, false otherwise
			value: the score of the other alternatives, except the alternative with position 'position'
			y: real regex
			x: train data : (regex of alignment, MatchingList)
			sm, sparm: parameters for the current weightvector
ensure:	regex with highest score for the position positon
'''


'''
computes the number of minimal and maximal number of whitespaces
'''
def get_number_of_whitespaces(matching_list):
	whiteList = [a.count(' ') for a in matching_list]
	return min(whiteList), max(whiteList)



def getMaxRegex(special_list,alt,curReg,stringList,position,fmvc,value,y,x,sm,sparm):
	classes_test = list_class[x.getID()][position]
	score = 0.0
	current = classes_test[0]
	index = 0
	scoreClassList = []
	for c in classes_test:
		actScore = svmlight.classify_example(sm,svmlight.create_svector(calc_psi(c)))
		subExpressionList = c.getSubExpressionList()
		for subExpression in subExpressionList:
			actType = subExpression.getLambdaType()						
			subVec = svector = svmlight.create_svector(tensor(phi_matchingSet(subExpression.getMatchinglist()),actType))
			subScore = svmlight.classify_example(sm,subVec)
			if not fmvc and False:
				if subExpression.getString() == '0-9':
					print '####################\n'
					vec = phi_matchingSet(subExpression.getMatchinglist())
					lenVec = len(vec)
					vecNew = [0.0 for a in range(lenVec)]
					for i in range(lenVec):
						vecNew[i] = 1.0
						aVec = svmlight.create_svector(tensor(vecNew,actType))
						aScore = svmlight.classify_example(sm,aVec)
						print 'score: ', i, ' is: ', aScore
						vecNew[i] = 0.0
					print '####################\n'
		if fmvc:
			actScore += list_loss[x.getID()][position].getErrorList()[0][index]
		scoreClassList.append((actScore,classes_test[index]))
		index += 1
	current = max(scoreClassList)[1]
	curReg[position] = current.getAlternatives()[0]
	return current	
	
	
'''
require:		string for example: Ii0-9
ensure: 		returns a list of all alternatives in string for example [I,i,0-9]
'''
def getAlternativesEasyType(str):
	reg_list = []
	offset = 0
	list_special = ['A-Z','a-z','0-9','A-F','a-f']
	for a in range(len(list_special)):
		if str.count(list_special[a]) > 0:
			reg_list.append('[' + list_special[a] + ']')
			str = str.replace(list_special[a],'')		
	for i in range(len(str)):
		if offset > 0:
			offset -= 1
			continue
		if str[i + offset] == '\\':
			reg_list.append(str[i] + str[i+1])
			offset += 1
		else:
			reg_list.append(str[i])
	return reg_list	

'''
require:	MacroID wich determines wich Macro, ex: DATE,
			text determines in wich we search for the macro
ensure:		list wich contains tuples (start,end,macroText) wich determines
			the start, the end and the Text for the Macro
'''
def computeMacroInsert(MacroID,text):
	list = []
	regex = possMacroList[MacroID][1]
	for m in re.finditer(regex, text):
		list.append((MacroID, m.start(),m.end(),m.group(0)))
	return list
	
'''
require: 	start, end wich determines the Postion for the start and the end
			the batch, wich contains the whole strings
ensure: 	
'''
def betweenString(start,end,batch):
	flagBegin = False
	flagEnd = False
	startString = 0
	endString = len(batch.getStringlist()) - 1
	num = len(batch.getStringlist()[0])
	for a in range(len(batch.getStringlist()) - 1):	
		num += len(batch.getMatchinglist()[a].getList()[0]) + len(batch.getStringlist()[a + 1])	
		if num > start and not flagBegin:
			startString = a
			flagBegin = True
		if num > end and not flagEnd:
			endString = a + 1
			flagEnd = True
			break		
	return startString, endString
	
'''
require: 	
ensure: 	
'''	
def containMacro(MacroID,start,end,batch):
	regex = possMacroList[MacroID][1]
	stringList = ['','']
	flagMatch = True
	matchList = []
	preSet = set()		# stores the different strings befor the macro
	postSet = set()	# stores the different strings after the macro
	preList = []
	postList = []
	# compute the MatchingLists
	for a in range(len(batch.getMatchinglist()[0].getList())):
		strg = computeStringFromTo(batch,start,end,a)
		m = re.search(regex,strg)
		if m is None:
			flagMatch = False
			break
		else:
			preSet.add(strg[0:m.start()])
			postSet.add(strg[m.end():])
			preList.append(strg[0:m.start()])
			postList.append(strg[m.end():])
			matchList.append(m.group(0))
	listMatchObjects = computeMatchList(matchList)
	# compute the alternatives for the matchingListObjects
	alternativeList = [Alternative(possMacroList[MacroID][0],listMatchObjects, 11, [0,0,0,0,0], [], [possMacroList[MacroID][0]])]
	# if the pre or postlist has more than one element, insert a dummy:
	# so it looks like: (.*)Macro(.*)
	if len(preSet) == 1:
		stringList[0] = preSet.pop()
	else:
		stringList = [''] + stringList
		alternativeList = [Alternative('[DUMMY]*',computeMatchList(preList))] + alternativeList
	if len(postSet) == 1:
		stringList[len(stringList) - 1] = postSet.pop()
	else:
		stringList = stringList + ['']
		alternativeList = alternativeList + [Alternative('[DUMMY]*',computeMatchList(postList))]
	macro = Macro(alternativeList,stringList,[],start,end,0)			
	return flagMatch, macro
		
'''
require:	a batch with a startPosition for the stringlist and a endposition for the stringlist
			finally the Position wich x^j in the batch x is computed
ensure:		the string from stringlist start to stringlist end of the batch
'''	
def computeStringFromTo(batch,start,end,Position):
	string = batch.getStringlist()[start]
	if end == -1:
		string = string + batch.getMatchinglist()[len(batch.getMatchinglist()) - 1].getList()[Position]
	else:
		for a in range(end)[start:]:
			string = string + batch.getMatchinglist()[a].getList()[Position] + batch.getStringlist()[a + 1]
	return string
	
'''
require:	stringList wich contains a list of strings
ensure: 	creates a MatchingList Object for that stringList
'''	
def computeMatchList(stringList): 
	help = MatchingList(stringList)
	help.setDistinctCharacterSet(get_distinct_character_set(stringList))
	help.setAttrAlternatives(get_attr_alternatives(stringList))
	help.setMaxMinDistinctLength(get_max_min_distinct_length(stringList))
	gAtoZ, sAtoZ, d0to9, gAtoF, sAtoF = get_number_character_class(help.getDistinctCharacterSet())
	help.setContainSpecials((gAtoZ, sAtoZ, d0to9, gAtoF, sAtoF))
	help.setMatchesEPlus(checkAllMatchEPlus(stringList))
	help.setFeatureVector(phi_matchingSet(help))
	return help
	
def checkAllMatchEPlus(matchList):
	c = re.compile("[\w._\-'#+]+",re.DOTALL)
	bool = True
	for a in range(len(matchList)):
		m = c.match(matchList[a])
		if m is None:
			bool = False
			break
		else:
			if len(m.group(0)) != len(matchList[a]):
				bool = False
				break
	return bool
	
'''
transforms a set to a list
'''
def setToList(set1):
	l = len(set1)
	list = []
	for a in range(l):
		list.append(l.pop())
	return list
'''
'''
def computeCompleteMacro(macro,sm,sparm):
	alternativeList = macro.getAlternativelist()[:]
	for a in range(len(alternativeList)):
		if alternativeList[a].getType() == -1:
			ret = [alternativeList[a]][:]
			y = ''
			string_list = ''
			x = Batch(string_list,1,[alternativeList[a].getMatchinglist()])
			help_list = getMaxSpecialList(0,ret,False,0.0,y,x,sm,sparm)
			getMaxRegex(help_list,ret[:],ret,string_list,0,False,0.0,y,x,sm,sparm)
			alternativeList[a] = ret[0]
	return alternativeList
	
'''
returns a string wich represents the expression
'''	
def printRegex(expression):
	string = ''
	for a in range(len(expression.getAlternatives())):
		string = string + expression.getStringlist()[a] + expression.getAlternatives()[a].getString()
	string = string + expression.getStringlist()[len(expression.getStringlist()) - 1]
	return string
	
	
'''
returns a string wich represents the b's batch
'''
def printBatch(expression,b):
	string = ''
	for a in range(len(expression.getAlternatives())):
		string = string + expression.getStringlist()[a] + expression.getAlternatives()[a].getMatchinglist().getList()[b]
	string = string + expression.getStringlist()[len(expression.getStringlist()) - 1]
	return string

def includeMaxMacros(x,y,regex,fmvc,sm,sparm):
	refScore = svmlight.classify_example(sm,psi(x,regex,sm,sparm))
	if fmvc:
		refScore += loss(y,regex,sparm,sm)
	offset = 0
	for a in range(len(macroList)):
		alternativeList = computeCompleteMacro(macroList[a],sm,sparm)
		diff = 1
		newStringList = regex.getStringlist()[0:macroList[a].getStartStringList() + offset] + macroList[a].getStringlist() + regex.getStringlist()[macroList[a].getEndStringList() + diff + offset:]
		newAlternativeList = regex.getAlternatives()[0:macroList[a].getStartStringList() + offset] + alternativeList + regex.getAlternatives()[macroList[a].getEndStringList() + offset + diff - 1:]
		newRegex = Expression(newStringList,newAlternativeList)
		newRefScore = svmlight.classify_example(sm,psi(x,newRegex,sm,sparm))
		if fmvc:
			newRefScore += loss(y,newRegex,sparm,sm)
		if newRefScore > refScore:
			regex = newRegex
			offset += len(alternativeList) - 1
	return regex
	
'''
replace the specials, so that the re.compile(regex) works
'''
def replaceSpecials(regex):
	neu = regex.replace('\\e','[\w._\-\'#+]')
	neu = neu.replace('\\u','[\w_\.\-]')
	neu = neu.replace('\\l*','[\r\n]*')
	neu = neu.replace('\\l','[\r\n]*')
	neu = neu.replace('\\o','[ \t]')
	neu = neu.replace('${NL}','[^\n]*\n')
	neu = neu.replace('${AVAST}','[\(\X\-Antivirus\: avast!Clean\|StatusNotTested\r\n\)]*')
	neu = neu.replace('${IP}','\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
	neu = neu.replace('${WND_SP}','[A-Za-z0-9\-\!\'\"\&\.\?_,]+')
	return neu
	
'''
replace all \r?
'''
def replaceNewLineAppend(regex):
	neu = regex.replace('(\\r?\n)','[\n]')
	neu = neu.replace('\\r?','')	
	return neu
'''
returns the index of shortCutList in the list of possible shortcuts
'''	
def getShortcutType(shortCutList):
	list = get_possiblilities()
	for a in range(len(list)):
		if shortCutList == list[a]:
			return a
			
			
def checkCaseInsensitiveEqual(list):
	disSet = set()
	allSet = set(list)
	if len(allSet) <= 1:
		return False
	for a in list:
		disSet.add(a.lower())
		if len(disSet) > 1:
			return False
	return True
	
def getEqualCaseInsensitiveRegex(list):
	re = ''
	listChar = []
	count = 0
	for i in range(len(list[0])):
		for j in list:
			if listChar.count(j[i]) == 0:
				listChar.append(j[i])
			if len(listChar) == 2:
				break
		if len(listChar) == 2:
			re = re + '[' + listChar[0] + listChar[1] + ']'
			count = count + 1
		else:
			re = re + listChar[0]
		listChar = []
	return (re,count)
	
	
#####################################################################
# find the longest commen subsequence of two strings
# source : http://wordaligned.org/articles/longest-common-subsequence
def memoize(fn):
    '''Return a memoized version of the input function.
    
    The returned function caches the results of previous calls.
    Useful if a function call is expensive, and the function 
    is called repeatedly with the same arguments.
    '''
    cache = dict()
    def wrapped(*v):
        key = tuple(v) # tuples are hashable, and can be used as dict keys
        if key not in cache:
            cache[key] = fn(*v)
        return cache[key]
    return wrapped

def lcs(xs, ys):
    '''Return the longest subsequence common to xs and ys.
    
    Example
    >>> lcs("HUMAN", "CHIMPANZEE")
    ['H', 'M', 'A', 'N']
    '''
    @memoize
    def lcs_(i, j):
        if i and j:
            xe, ye = xs[i-1], ys[j-1]
            if xe == ye:
                return lcs_(i-1, j-1) + [xe]
            else:
                return max(lcs_(i, j-1), lcs_(i-1, j), key=len)
        else:
            return []
    return lcs_(len(xs), len(ys))
    
def saveModel(sm,dst):
	string = '# Model for Pegasos \n# <dimension> <id>:<value> <id:value> ... \n'
	string = string + str(len(sm.w)) + ' '
	for i in range(len(sm.w)):
		string = string + str(i) + ':' + str(sm.w[i]) + ' '
	fobj = open(dst,'w')
	fobj.write(string)
	fobj.close()
	
def printModel(sm,nrFeature):
	string = '# Model for Pegasos \n# <dimension> <id>:<value> <id:value> ... \n'
	string = string + str(len(sm.w)) + ' '
	counter = 0
	for i in range(len(sm.w)):
		counter += 1
		string = string + str(i) + ':' + str(sm.w[i]) + ' '
		if counter == nrFeature:
			string = string + '\n'
			counter = 1		
	print string
#######################################################################


def calc_psi(y):
	subExpressionList = y.getSubExpressionList()
	reVec = []
	matchVec = []
	for subExpression in subExpressionList:
		if subExpression.getString().startswith('(.*)'):
			continue
		actType = subExpression.getLambdaType()
		if matchVec == []:
			matchVec = tensor(phi_matchingSet(subExpression.getMatchinglist()),actType)
		else:
			matchVec = vec_add(matchVec,tensor(phi_matchingSet(subExpression.getMatchinglist()),actType))
		
		for lambdaType in subExpression.getTopLevelAlternativeTypes():
			if reVec == []:
				reVec = tensor(actType,lambdaType)
			else:
				reVec = vec_add(reVec,tensor(actType,lambdaType))
	reVec = reVec + matchVec
	return reVec

	
	
	
# 10 normal types + 8 possible ranges (0-9,a-z,A-Z,a-f,A-F,\S,\e,\d)
def lambda_r(alternative):
#	print 'alt: ', alternative.getString()
	altString = alternative.getString()
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
	return reVec

	
def get_top_level_alternatives(alternative):
	altString = alternative.getString()
	c1 = re.compile('([\w\W]+)\{(\d+|\d+,\d+)\}')
	# if alternative has a quantor
	if altString.endswith('*') or altString.endswith('+') or altString.endswith('?') or (c1.match(altString) is not None):
		if altString.startswith('['):
			withoutQuantor = ''
			if altString.endswith('*') or altString.endswith('+') or altString.endswith('?'):
				withoutQuantor = altString[:len(altString)-1]
			else:
				c1 = re.compile('([\w\W]+)\{(\d+|\d+,\d+)\}')
				withoutQuantor = c1.match(altString).group(1)
			matchingList = get_set_of_characters(alternative.getMatchinglist())
			alternative1 = getAlternative(withoutQuantor,matchingList)
			return [alternative1]
		elif altString.startswith('('):
			withoutQuantor = ''
			if altString.endswith('*') or altString.endswith('+') or altString.endswith('?'):
				withoutQuantor = altString[:len(altString)-1]
			else:
				c1 = re.compile('([\w\W]+)\{(\d+|\d+,\d+)\}')
				withoutQuantor = c1.match(altString).group(1)
				matchingList = get_matching_list_for_alternative(withoutQuantor, alternative.getMatchinglist())
				alternative1 = getAlternative(withoutQuantor,matchingList)
				return [alternative1]
		else:
			withoutQuantor = ''
			if altString.endswith('*') or altString.endswith('+') or altString.endswith('?'):
				withoutQuantor = altString[:len(altString)-1]
			else:
				c1 = re.compile('([\w\W]+)\{(\d+|\d+,\d+)\}')
				withoutQuantor = c1.match(altString).group(1)
			matchingList = get_set_of_characters(alternative.getMatchinglist())
			alternative1 = getAlternative(withoutQuantor,matchingList)
			return [alternative]
	# if alternative is [] or \
	elif (altString.startswith('[') and altString.endswith(']')) or altString.startswith('\\'):
		if altString.startswith('\\'):
			return [alternative]
		else:
			altString = altString[1:len(altString) -1]
			reList = []
			rangeList = get_list_of_ranges(altString)
			withoutRanges = altString
			for ele in rangeList:
				matchingList = get_matching_list_for_range(ele,alternative.getMatchinglist())
				alternative1 = getAlternative(ele,matchingList)
				reList.append(alternative1)
				withoutRanges = withoutRanges.replace(ele,'')
			for ele in withoutRanges:
				matchList = computeMatchList([ele])
				alternative1 = getAlternative(ele,matchList)
				reList.append(alternative1)
		return reList
	elif altString.startswith('(') and altString.endswith(')'):
		print 'todo'
		exit()
	return []
			

def get_matching_list_for_range(range,matchingList):
	matchList = matchingList.getList()
	characterSet = set()
	c1 = re.compile('[' + range  + ']', re.DOTALL)
	for ele1 in matchList:
		for ele2 in ele1:
			if c1.match(ele2) is not None:
				characterSet.add(ele2)
	reMatchingList = computeMatchList(list(characterSet))
	return reMatchingList
			

def get_list_of_ranges(regexString):
	reList = []
	if regexString.count('0-9'):
		reList.append('0-9')
	if regexString.count('a-z'):
		reList.append('a-z')
	if regexString.count('A-Z'):
		reList.append('A-Z')
	if regexString.count('a-f'):
		reList.append('a-f')
	if regexString.count('A-F'):
		reList.append('A-F')
	if regexString.count('\\S'):
		reList.append('\\S')
	if regexString.count('\\S'):
		reList.append('\\S')
	if regexString.count('\\w'):
		reList.append('\\w')
	if regexString.count('\\W'):
		reList.append('\\W')
	return reList
	
	
# alternatives of the form [...]			
def get_set_of_characters(matchingList):
	stringList = matchingList.getList()
	characterSet = set()
	for ele in stringList:
		for ele1 in ele:
			characterSet.add(ele1)
	characterList = list(characterSet)
	reMatchingList = computeMatchList(characterList)
	return reMatchingList


# alternatives of the form (||||)
def get_matching_list_for_alternative(regexString,matchingList):
	stringList = matchingList.getList()
	matchSet = set()
	c = re.compile(regexString, re.DOTALL)
	for ele in stringList:
		for a in range(len(ele)):
			ma = c.search(ele).group(0)
			matchSet.add(ma)
			ele = ele[ele.index(ma) + len(ma):]
			if ele == '':
				break
	reMatchingList = computeMatchList(list(matchSet))
	return reMatchingList
	
	
def tensor(vec1,vec2):
	reVec = []
	for ele1 in vec2:
		for ele2 in vec1:
			reVec.append(ele1 * ele2)
	return reVec
	
def vec_add(vec1,vec2):
	if len(vec1) != len(vec2):
		print 'error, because the vectors for the add operation have not the equal length'
		exit()
	reVec = []
	for idx in range(len(vec1)):
		reVec.append(vec1[idx] + vec2[idx])
	return reVec
	
	
def getListOfAlternativesNew(list,regex, matchingList,stringList,wholeMatchingList, regexPlane):
	retList = []
	typeList = []	
	# add all characters from the stringList
	for ele1 in stringList:
		for ele2 in ele1:
			addAlternative = Alternative(ele2,computeMatchList([ele2]))
			addAlternative.setLambdaType(lambda_r(addAlternative))
			retList.append(addAlternative)
			typeList.append(lambda_r(addAlternative))
	matchList = []
	# for all alternatives with depth 0 add this and the containing alternatives to the list
	for a in range(len(list)):
		begin = 0
		# dont consider the \(
		helpRegex = regex.replace('\\(','AA')
		#helpRegex = regex.replace('\\)','AA')
		for b in range(list[a]):
			idx = helpRegex[begin:].find('(')
			begin = begin + idx + 1
		idx = begin - 1		
		innerRegex = parse_regex.find_in_brackets(0,idx,regex)
		innerRegex =  innerRegex[1:len(innerRegex)-1]
		alt = getAlternativeNew(innerRegex,matchingList[a])
		
		
		retList += alt
		# add first alternative which is the alternative itself:
		if len(alt) >= 1:
			typeList.append(lambda_r(alt[0]))
			
	# add whole regex if not stringList = ['','']
	if stringList != ['','']: #and not (regexPlane.startswith('[') or regexPlane.startswith('(')):
		addingAlternative = Alternative(regexPlane,computeMatchList(wholeMatchingList))
		# add type for a \in \Sigma		
		retList.append(addingAlternative)
		addingAlternative.setLambdaType(lambda_r(addingAlternative))
		addingAlternative.setTopLevelAlternativeTypes(typeList)
	return retList
	

'''
require:	alternative-string 'regex' and the Matching-List 'matchingList' for this alternativ
ensure:		creates an object from type 'Alternative', with all containing alternatives
'''	
def getAlternativeNew(regex, matchingList):
	list = matchingList.getList()
	type, dummy = get_type_and_score(regex,[])
	str = regex
	shortcut = [0 for a in range(len(shortCutList))]
	alterlist = None
	alt = ''
	if type >= 1 and type <= 5:
		all = getAlternativesEasyType(regex[1:regex.rfind(']')])
		c1 = re.compile('([\w\W]+)\{(\d+|\d+,\d+)\}')
		altString = str
		alt = []
		if altString.endswith('*') or altString.endswith('+') or altString.endswith('?') or (c1.match(altString) is not None):
			alt1 = Alternative(str,matchingList,type,shortcut,[],[])
			if altString.startswith('['):
				withoutQuantor = ''
				if altString.endswith('*') or altString.endswith('+') or altString.endswith('?'):
					withoutQuantor = altString[:len(altString)-1]
				else:
					c1 = re.compile('([\w\W]+)\{(\d+|\d+,\d+)\}')
					withoutQuantor = c1.match(altString).group(1)
				alt1.setLambdaType(lambda_r(alt1))
				matchingListNew = get_set_of_characters(matchingList)
				alternativeList1 = getAlternativeNew(withoutQuantor,matchingListNew)
				alternative2 = alternativeList1[0]
				alternative1 = alternativeList1[len(alternativeList1)-1]
				alt1.setTopLevelAlternativeTypes([lambda_r(alternative1)])
				altString = withoutQuantor
				altString = altString[1:len(altString) -1]
				reList = []
				typeList = []
				rangeList = get_list_of_ranges(altString)
				withoutRanges = altString
				for ele in rangeList:
					matchingListNew = get_matching_list_for_range(ele,matchingList)
					alternative2 = Alternative(ele,matchingListNew,-1,shortcut,[],[])
					alternative2.setLambdaType(lambda_r(alternative2))
					typeList.append(lambda_r(alternative2))
					reList.append(alternative2)
					withoutRanges = withoutRanges.replace(ele,'')
				if withoutRanges.count('\\\\') > 0:
					matchList = computeMatchList(['\\'])
					alternative2 = Alternative('\\',matchList,-1,shortcut,[],[])
					alternative2.setLambdaType(lambda_r(alternative2))
					typeList.append(lambda_r(alternative2))
					reList.append(alternative2)
				withoutRanges = withoutRanges.replace('\\','')
				for ele in withoutRanges:
					matchList = computeMatchList([ele])
					alternative2 = Alternative(ele,matchList,-1,shortcut,[],[])
					alternative2.setLambdaType(lambda_r(alternative2))
					typeList.append(lambda_r(alternative2))
					reList.append(alternative2)
				alt = reList
				alt += [alternative1,alt1]
			elif altString.startswith('\\'):				
				withoutQuantor = ''
				if altString.endswith('*') or altString.endswith('+') or altString.endswith('?'):
					withoutQuantor = altString[:len(altString)-1]
				else:
					c1 = re.compile('([\w\W]+)\{(\d+|\d+,\d+)\}')
					withoutQuantor = c1.match(altString).group(1)
				matchingListNew = get_set_of_characters(matchingList)
				alt2 = getAlternativeNew(withoutQuantor,matchingListNew)[0]
				alt1.setLambdaType(lambda_r(alt1))
				alt1.setTopLevelAlternativeTypes([lambda_r(alt2)])
				alt = [alt1,alt2]
			else:
				alt = [Alternative(withoutQuantor,computeMatchinglist(withoutQuantor),-1,shortcut,[],[])]
		else:
			if altString.startswith('\\'):
				addAlternative = Alternative(str,matchingList,type,shortcut,[],[])
				addAlternative.setLambdaType(lambda_r(addAlternative))
				addAlternative.setTopLevelAlternativeTypes([lambda_r(addAlternative)])
				alt = [addAlternative]
			else:
				altString = altString[1:len(altString) -1]
				reList = []
				typeList = []
				addAlternative = Alternative(str,matchingList,type,shortcut,[],[])
				addAlternative.setLambdaType(lambda_r(addAlternative))				
				rangeList = get_list_of_ranges(altString)
				withoutRanges = altString
				for ele in rangeList:
					matchingListNew = get_matching_list_for_range(ele,matchingList)
					alternative1 = Alternative(ele,matchingListNew,-1,shortcut,[],[])
					alternative1.setLambdaType(lambda_r(alternative1))
					reList.append(alternative1)
					typeList.append(lambda_r(alternative1))
					withoutRanges = withoutRanges.replace(ele,'')
				if withoutRanges.count('\\\\') > 0:
					matchList = computeMatchList(['\\'])
					alternative1 = Alternative('\\',matchList,-1,shortcut,[],[])
					alternative1.setLambdaType(lambda_r(alternative1))
					typeList.append(lambda_r(alternative1))
					reList.append(alternative1)
				withoutRanges = withoutRanges.replace('\\','')
				for ele in withoutRanges:
					matchList = computeMatchList([ele])
					alternative1 = Alternative(ele,matchList,-1,shortcut,[],[])
					alternative1.setLambdaType(lambda_r(alternative1))
					typeList.append(lambda_r(alternative1))
					reList.append(alternative1)
				addAlternative.setTopLevelAlternativeTypes(typeList)
				reList.append(addAlternative)
				alt = reList
		return alt
	else:
		all, alterlist = getListSubalternatives(str[str.find('(') + 1:str.rfind(')')])
	if type >= 6 and type <= 10:
		wholeAlternative1 = Alternative(regex,matchingList,-1,shortcut,[],[])
		wholeAlternative1.setLambdaType(lambda_r(wholeAlternative1))
		regNeu = parse_regex.get_in_brackets(0,regex)
		append = parse_regex.find_append(len(regNeu),regex)
		regNeu = regNeu[1:]
		alt = []
		# compute matching for all all with (||||||)q
		if append != '':
			newMatchingList = get_matching_list_for_alternative(regNeu, matchingList)
			wholeAlternative1.setLambdaType(lambda_r(wholeAlternative1))
			wholeAlternative = Alternative('(' +  regNeu + ')',newMatchingList,-1,shortcut,[],[])
			wholeAlternative.setTopLevelAlternativeTypes(wholeAlternative)
			wholeAlternative.setLambdaType(lambda_r(wholeAlternative))
			matchingList = newMatchingList
			list = matchingList.getList()
			alt.append(wholeAlternative1)
		if regNeu == '.*':
			addAlternative = Alternative(str,matchingList,type,shortcut,[],[])
			addAlternative.setLambdaType(lambda_r(addAlternative))
			return [addAlternative]
		li, reg, stringList, listeMacro, regexMacro = match_regex.calculate_match_regex(regNeu)
		li, reg,alternativeList = match_regex.group_alternatives(regNeu)
		c1 = re.compile('foo(' + replaceSpecials(reg) + ')foo',re.DOTALL)
		newList = []
		wholeList = list[:]
		for d in range(len(li)):
			newList.append([])
		for d in range(len(list)):
			newStrg = 'foo' + list[d] + 'foo'
			m1 = c1.match(newStrg)
			if m1 is not None:
				for b in range(len(li)):
					if m1.group(li[b] + 1) is not None:
						newList[b].append(m1.group(li[b] + 1))
			else:
				print 'matchte:' + replaceSpecials(reg) +  ':Ausgabe: ' + newStrg
				print allo
		listNew = []
		for c in range(len(newList)):
			help = MatchingList(newList[c])
			help.setDistinctCharacterSet(get_distinct_character_set(newList[c]))
			help.setAttrAlternatives(get_attr_alternatives(newList[c]))
			help.setMaxMinDistinctLength(get_max_min_distinct_length(newList[c]))
			gAtoZ, sAtoZ, d0to9, gAtoF, sAtoF = get_number_character_class(help.getDistinctCharacterSet())
			help.setContainSpecials((gAtoZ, sAtoZ, d0to9, gAtoF, sAtoF))
			listNew.append(help)
		typeList = []
		for i in range(len(listNew)):
			li, reg, stringList, listeMacro, regexMacro = match_regex.calculate_match_regex(alternativeList[i])			
			newList = []
			c1 = re.compile(replaceSpecials(reg),re.DOTALL)
			for d in range(len(li)):
				newList.append([])
			list = listNew[i].getList()
			for d in range(len(list)):
				m1 = c1.match(list[d])
				if m1 is not None:
					for b in range(len(li)):
						if m1.group(li[b]) is not None:
							newList[b].append(m1.group(li[b]))
				else:
					print 'matchte: ', replaceSpecials(reg),  'Ausgabe: ', list[d]
					print allo
			listNew2 = []
			for c in range(len(newList)):
				help = MatchingList(newList[c])
				help.setDistinctCharacterSet(get_distinct_character_set(newList[c]))
				help.setAttrAlternatives(get_attr_alternatives(newList[c]))
				help.setMaxMinDistinctLength(get_max_min_distinct_length(newList[c]))
				gAtoZ, sAtoZ, d0to9, gAtoF, sAtoF = get_number_character_class(help.getDistinctCharacterSet())
				help.setContainSpecials((gAtoZ, sAtoZ, d0to9, gAtoF, sAtoF))
				listNew2.append(help)
			alter = getListOfAlternativesNew(listeMacro,regexMacro,listNew2,stringList,listNew[i].getList(),alternativeList[i])
			if len(alter) > 0:
				typeList.append(lambda_r(alter[len(alter)-1]))
			for j in range(len(alter)):				
				alt.append(alter[j])
		wholeAlternative1.setTopLevelAlternativeTypes(typeList)
		alt.append(wholeAlternative1)
	if alt == '':
		print 'error bei: ', regex
		exit()
	return alt


def phi_matchingSet(matchingSet):
	featureVector = []
	# transform the possible list in a set and then back to a list
	matchList = list(set(matchingSet.getList()))
	minimum = -1
	maximum = -1
	lengthSet = set()
	allOne = 1
	# set up the necessary parameters for the phi-vector
	for ele in matchList:
		if minimum == -1 or len(ele) < minimum:
			minimum = len(ele)
		if maximum == -1 or len(ele) > maximum:
			maximum = len(ele)
		lengthSet.add(len(ele))
		if len(ele) != 1:
			allOne = -1
	
	# get the parameters which define, how many characters of the ranges A-Z,a-z,0-9,A-F,a-f are in the matching set 
	gAtoZ, sAtoZ, d0to9, gAtoF, sAtoF = matchingSet.getContainSpecials()
	
	#F_1: indicator if the empty string is in the matchingSet:
	if minimum == 0:
		featureVector.append(1.0)
	else:
		featureVector.append(0.0)
	
	#F_2: all elements in the matchingSet have the length 1
	if minimum <= 1 and maximum <= 1:
		featureVector.append(1.0)
	else:
		featureVector.append(0.0)
		
		
	#F_3: indicates if all strings in the matchingSet have the same lenth
	if len(lengthSet) == 1:
		featureVector.append(1.0)
	else:
		featureVector.append(0.0)
	
	#F_4: indicates if all strings have the length one
	if allOne == 1:
		featureVector.append(1.0)
	else:
		featureVector.append(0.0)
		
	#F_5: portion of characters in A-Z in matching set:
	featureVector.append(gAtoZ / 26.0)
	
	#F_6: portion of characters in a-z in matching set:
	featureVector.append(sAtoZ / 26.0)
	
	#F_7: portion of characters in 0-9 in matching set:
	featureVector.append(d0to9 / 10.0)
	
	#F_8: portion of characters in A-F in matching set:
	featureVector.append(gAtoF / 6.0)

	#F_9: portion of characters in A-Z\A-F in matching set:
	featureVector.append((gAtoZ - gAtoF) / 20.0)
	
	#F_10: portion of characters in a-f in matching set:
	featureVector.append(sAtoF / 6.0)
	
	#F_11: portion of characters in a-z\a-f in matching set:
	featureVector.append((sAtoZ - sAtoF) / 20.0)
		
	#F_12: indicates, if no characters from A-Z are in matching set:
	if gAtoZ == 0:
		featureVector.append(1.0)
	else:
		featureVector.append(0.0)
	
	#F_13: indicates, if no characters from a-z are in matching set:
	if sAtoZ == 0:
		featureVector.append(1.0)
	else:
		featureVector.append(0.0)
	
	#F_14: indicates, if no characters from A-F are in matching set:
	if gAtoF == 0:
		featureVector.append(1.0)
	else:
		featureVector.append(0.0)
	
	#F_15: indicates, if no characters from a-f are in matching set:
	if sAtoF == 0:
		featureVector.append(1.0)
	else:
		featureVector.append(0.0)
	
	#F_16: indicates, if no characters from 0-9 are in matching set:
	if d0to9 == 0:
		featureVector.append(1.0)
	else:
		featureVector.append(0.0)
		
	lenDiff = maximum - minimum
	#F_17: maximum - mininimum is between 1 and 5:
	if lenDiff > 0 and lenDiff <= 5:
		featureVector.append(1.0)
	else:
		featureVector.append(0.0)
		
	#F_18: maximum - mininimum is between 6 and 10:
	if lenDiff > 5 and lenDiff <= 10:
		featureVector.append(1.0)
	else:
		featureVector.append(0.0)
		
	#F_19: maximum - mininimum is between 10 and 20:
	if lenDiff > 10 and lenDiff <= 20:
		featureVector.append(1.0)
	else:
		featureVector.append(0.0)
		
	#F_19: maximum - mininimum is higher than 20:
	if lenDiff >= 20:
		featureVector.append(1.0)
	else:
		featureVector.append(0.0)
		
	#F_20: matching set is empty:
	if matchList == []:
		featureVector.append(1.0)
	else:
		featureVector.append(0.0)	
	if len(matchList) == 1:
		return [0.0 for a in range(len(featureVector))]
	return featureVector