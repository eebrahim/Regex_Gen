import os,sys


dirList = ['train/train1/','train/train2/','train/train3/','train/train4/','train/train5/','train/train6/','train/train7/','train/train8/','train/train9/','train/train10/','train/train11/','train/train12/','train/train13/','train/train14/','train/train15/','train/train16/','train/train17/','train/train18/','train/train19/','train/train20/','test/test1/','test/test2/','test/test3/','test/test4/','test/test5/'];


for dirName in dirList:
	fileList = os.listdir(dirName)
	if os.path.isfile(dirName + 'alignment.txt'):
		print 'remove: ' + dirName + 'alignment.txt'
		os.remove(dirName + 'alignment.txt')