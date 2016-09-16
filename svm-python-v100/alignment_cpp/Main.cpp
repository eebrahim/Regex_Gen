
/***********************************************************************/
/*                                                                     */
/*   Main.cpp                                                      */
/*                                                                     */
/*   Part of the hirschberg-align-algorithm to compute a alignment     */
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



#include <iostream>
#include <vector>
#include "Hirschberg.h"
#include "Util.h"
#include <sstream>
#include "SimilarityString.h"
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <iomanip>
#include <fstream>
#include <string.h>
#include <time.h>




using std::cout;
using std::endl;
using std::vector;
using std::string;
using namespace std;

void usage()
{
    cout << "usage: Align <options> <file-list>" << endl;
}


void help()
{
    using std::setw;
    using std::left;
    using std::right;
    size_t leftMarg = 30;

    usage();
    cout << endl;
    cout << "options:" << endl;
    cout << setw(leftMarg) << left << "-q" << "quiet mode, only show result" << endl;
    cout << setw(leftMarg) << left << "-k" << "don't strip differences from similarity string" << endl;
    cout << setw(leftMarg) << left << "-n" << "don't strip numbers" << endl;
    cout << setw(leftMarg) << left << "-a" << "show alignments" << endl;
    cout << setw(leftMarg) << left << "-g <gapPenalty>" << "adjust gap penalty (default: 0.8)" << endl;
    cout << setw(leftMarg) << left << "-i <isleSize>" << "adjust isle size (default: 3)" << endl;
    cout << setw(leftMarg) << left << "-r <replaceString>" << "set replace string (default: '(.{0,n})'), where 'n' will be replaced by the number of characters" << endl;
	cout << setw(leftMarg) << left << "-f" << "file wich contains the pahts of the strings wich should be aligned" << endl;
	cout << setw(leftMarg) << left << "-o <fileName>" << "name of file to store the alignment" << endl;
}


int main (int argc, char* argv[])
{
    // program options
    bool quiet = false;
    double gapPenalty = 0.8f;
    bool stripDiffs = true;
    size_t isleSize = 3;
    bool showAlignments = false;
    string replaceStr = "(.{0,n})";
    string output = "";
    string startAlignment = "";
    string outputAlignment = "";
    vector<string> files;
	vector<string> usedFiles;
    bool fromFile = false;
    bool stripNums = true;
    bool inboxMode = false;
    int c;
	
	//cout << "start mich" << endl;
	
	//"qfkng:i:r:o:s:t:ah"
    while ((c = getopt (argc, argv, "qfknbg:i:r:o:s:t:ah")) != -1){
        switch(c){
			case 'h':
                help();
                return 0;
                break;
            case 'q':
                quiet = true;
                break;
            case 'n':
				stripNums = false;
				break;
            case 'g':
                gapPenalty = strtof(optarg, &optarg);
                break;
            case 'k':
                stripDiffs = false;
                break;
            case 'i':
                isleSize = strtof(optarg, &optarg);
                break;
            case 'r':
                replaceStr = string(optarg);
                break;
            case 'a':
                showAlignments = true;
                break;
            case '?':
                usage();
                return 0;
                break;
			case 'f':				
				fromFile = true;
				break;
			case 'o':
                output = string(optarg);
                break;
            case 's':
                startAlignment = string(optarg);
                break;
            case 't':
                outputAlignment = string(optarg);
                break;
            case 'b':
				inboxMode = true;
				break;
        }
    }
	if(!quiet){
        cout << "<<< settings: >>>" << endl;
        cout << "quiet: " << quiet << endl;
        cout << "gapPenalty:  " << gapPenalty << endl;
        cout << "isleSize:  " << isleSize << endl;
        cout << "stripDiffs:  " << stripDiffs << endl;
        cout << "stripNums: " << stripNums << endl;
        cout << "replaceStr:  " << replaceStr << endl;
        cout << "showAlignments:  " << showAlignments << endl;
        cout << "output: " << output << endl;
        cout << "outputAlignment: " << outputAlignment << endl;    
        cout << "fromFile: " << fromFile << endl;
        cout << endl;
    }
    if (optind < argc) {
		if (fromFile) {
			std::ifstream inputFile (argv[optind++]);
			std::string line;
			if (inputFile){
				while(getline(inputFile,line)){
					if (inboxMode){
						if(line.find("_mcrack") != string::npos){
							files.push_back(line);
						}
					}
					else {
						if (line.length() != 0)
							files.push_back(line);
					}
				}
			}
			inputFile.close();
		}
		else {
			while (optind < argc){
				string filename = argv[optind++];
				if (inboxMode){
					if(filename.find("_mcrack") != string::npos){
						files.push_back(filename);
					}
				}
				else {
					files.push_back(filename);
				}
				if(optind >= 500)
					break;
			}
		}
    }
    else {
		cout << "Nothing to do" << endl;
	}
//    for(size_t i = 1; i < files.size(); i++){
//		cout << "file " << files[i] << " ..." << endl;
//	}
    if(files.size() < 2){
        cout << "Not enough files to compare!" << endl;
        usage();
        return 0;
    }


    // init similarity string
    string fs;
    for(size_t i = 0; i < files.size(); i++){
		try{
			readFile(files[i], fs);
			break;
		}catch(...){
			continue;
		}
	}
    SimilarityString ss(fs, replaceStr);

    // init align object
    DistMat distMat;
    createDistMat(256, 0.0f, 1.0f, distMat);
    Hirschberg hAlign(distMat, 0.0f, gapPenalty);
    if (startAlignment != ""){
		std::string test;
		usedFiles.clear();
		readFromFile(startAlignment,test);
		ss.initializeFromFile(test,usedFiles);
		/*
		for (int i = 0; i < usedFiles.size(); ++i){
			std::cout << usedFiles[i] << std::endl;
		}
		*/
	}
	else {
		usedFiles.clear();
	}
	time_t start;
	start = time(NULL);
    for(size_t i = 1; i < files.size(); i++){
		//skip if files[i] is in usedFiles... (already used to create alignment)
		std::vector<std::string>::iterator result;
        if(!quiet)
            cout << "reading file " << files[i] << " ..." << endl;
        try{
			readFile(files[i], fs);
		}catch(...){
			if(!quiet)
				cout << "skipped ..." << endl << endl;
			continue;
		}
        if(!quiet)
            cout << "aligning pair " << i << " of " << files.size() - 1 << " ..." << endl << endl;

        hAlign.align(ss.original, fs);
        if(showAlignments){
            cout << strInline(hAlign.alignedX) << endl;
            cout << strInline(hAlign.alignedY) << endl;
            cout << endl;
        }
        ss.update(hAlign.alignedX, hAlign.alignedY);
        //cout << "updated" << endl;
        //cout << strInline(string(ss)) << endl;
        //cout << endl;
		if(!quiet){
			cout << "time to create alignment: " << time(NULL) - start << " sec." << endl;
			start = time(NULL);
		}
        if(stripDiffs)
            ss.condense();
    }
    if (outputAlignment != ""){
		ss.printToFile(outputAlignment, files);
	}

    if(stripNums){
		ss.stripNums();
	}
    ss.stripIsles(isleSize);
    if (output != ""){
		fstream f;
		f.open(output.c_str(), ios::out);
		f << string(ss) << flush;
		f.close();
	}
	if (!inboxMode){
		cout << string(ss) << endl;
	}
//    cout << string(ss) << endl;

    return 0;
}
