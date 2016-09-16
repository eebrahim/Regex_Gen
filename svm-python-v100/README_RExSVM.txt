REx-SVM
-------

This package is a Python implementation of the REx-SVM. REx-SVM is an algorithm to learn a model which can be used to predict regular expressions for a given batch.
The algorithm is described at:
	Paul Prasse, Christoph Sawade, Niels Landwehr, and Tobias Scheffer. 
	Learning to Identify Regular Expressions that Describe Email Campaigns.
	Proceedings of the 29th International Conference on Machine Learning 
	(ICML-2012), Edinburgh, Scotland, 2012.
	http://www.cs.uni-potsdam.de/ml/publications/icml2012-regular-expressions.pdf

The implementation supports the following regular expressions:
- alternatives of strings, e.g. (hi|hello),
- alternatives of single characters, e.g. [abc],
- the quantors +,?,{x},{x,y},* , where x and y are digits;
- the ranges 
	0-9, 
	a-z, 
	A-Z, 
	a-f, 
	A-F,
- the macros
	\d = [0-9],
	\e = [a-zA-Z0-9._-'#+],
	\S = everything except whitespace characters,
- concatenations of alternatives and regular strings.
	
Example: "(buy|get) cheap [Vv]ia[gG]ra for only \d+ $"


Installation
------------

You will need
	- svm-python framework used by SVM^struct by Thorsten Joachims (http://tfinley.net/software/svmpython1/svm-python-v100.tgz).
	- current version of the python interpreter (http://www.python.org/).
	- the open-source build system cmake (http://www.cmake.org/).


To install this package, run the following commands:
	% extract the REx-SVM package
	tar xvzf REx-SVM.tar.gz

	% download the svm-python framework, if not done earlier.
	wget http://tfinley.net/software/svmpython1/svm-python-v100.tgz

	% extract the svm-python framework
	tar xzf svm-python-v100.tgz

	% change directory to svm-python-v100 directory
	cd svn-python-v100

	% compile the svmstruct framework; if it does not work; try the c++ compiler by changing the line "LD =
	% gcc" to "LD = c++" in the Makefile
	make

	% compile the hirschberg-alignment algorithmus
	cd alignment_cpp
	cmake .
	make


The previous commands should yield the following file structure:
	svm-python-v100
	alignment_cpp
	example
	html-docs
	mulit-example
	svm_light
	svm_struct
	LICENCE_RExSVM.txt
	LICENSE.txt
	macro_definition.txt
	Makefile
	match_regex.py
	multiclass.py
	parse_regex.py
	preprocessing.py
	README.txt
	README_RExSVM.txt
	README_STRUCT.txt
	regex.py
	svmstruct.py
	svm_struct_api.c
	svm_struct_api.h
	svm_struct_api.o
	svm_struct_api_types.h
	

Usage
-----

Make sure that your PYTHONPATH environment includes ".". This can be done in a Linux/Unix environment by the following command:
	export PYTHONPATH=${PYTHONPATH}:.


You can start REx-SVM by using the following commands:
	
	% learn a model
	./svm_python_learn		--m regex [options] <train> <model>
	
	% classify given batches:
	./svm_python_classify	--m regex [options] <test> <output>

The predicted regular expressions are written to the file <output>.
Furthermore, all arguments of the original SVM^struct can be used. For example, the option "-c 100" adjusts the regularization parameter C to 100. 


The files <train>/<test> must contain the list of the directories that contain the batches (.in files), the
labels (label.txt), and the file lists (filelist.txt).

Example:
	train.txt:	dir1						% batch 1
				dir2						% batch 2
				dir3						% batch 3
	where dir1, dir2, and dir3 are folders including data of the corresponding batch data, e.g. 
	dir1:		0.in						% contains one text which belongs to the batch
				1.in
				2.in
				3.in
				label.txt					% contains the target regular expression
	filelist.txt:	dir1/0.in					% absolute path; or relative path from root of svm-python-v100
				dir1/1.in
				dir1/2.in
				dir1/3.in
								
A complete example can be found in the folder example.


Example
-------

This package includes an example to learn a model from 20 given input batches and to predict 
a regular expression for test batches. To execute it call the following commands:

	% set pythonpath:
	export PYTHONPATH=${PYTHONPATH}:. 

	% learn model:
	./svm_python_learn --m regex -p 1 -c 999999 example/trainDirList.txt themodel

	% classify with model:
	./svm_python_classify --m regex example/testDirList.txt themodel output
