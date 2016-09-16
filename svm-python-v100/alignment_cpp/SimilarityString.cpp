
/***********************************************************************/
/*                                                                     */
/*   SimilarityString.cpp                                              */
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



#include "SimilarityString.h"
#include <sstream>
#include <iostream>
#include <vector>
#include <fstream>
#include <stdexcept>
#include "Util.h"
#include <cstdlib>

using std::string;
using std::cout;
using std::endl;
using std::vector;
using namespace std;



SimilarityString::operator string()
{
    std::stringstream ret;
    size_t currentGap = 0;

    for(size_t i = 0; i < mask.size(); i++){
        currentGap += gaps[i];
        if(!mask[i]){
            currentGap++;
        }else{
            if(currentGap){
                ret << replaceString(replaceStr, "n", toStr(currentGap));
                currentGap = 0;
            }
            if(original[i] == '.'){
				ret << "\\.";
			}else if(original[i] == '*'){
				ret << "\\*";
			}else if(original[i] == '+'){
				ret << "\\+";
			}else if(original[i] == '?'){
				ret << "\\?";
			}else if(original[i] == '['){
				ret << "\\[";
			}else if(original[i] == '('){
				ret << "\\(";
				
			}else if(original[i] == ')'){
				ret << "\\)";
			}else if(original[i] == ']'){
				ret << "\\]";
			}else if(original[i] == '\\'){
				ret << "\\\\";
			}else if(original[i] == '$'){
				ret << "\\$";
			}else if(original[i] == '|'){
				ret << "\\|";
			}else{
				ret << original[i];
			}
        }
    }
    if(gaps[original.size()])
        ret << replaceString(replaceStr, "n", toStr(gaps[original.size()]));

    return ret.str();
}


void SimilarityString::update(const AlignedString& x1, const AlignedString& x2)
{
    if(x1.aligned.size() != x2.aligned.size())
        cout << "WARNING!" << endl;
    for(size_t i = 0; i < x1.aligned.size(); i++){
        if(x1.aligned[i] != GAP_CODE && x1.aligned[i] != x2.aligned[i])
            mask[x1.originalIndices[i]] = false;
    }
    for(size_t i = 0; i < x1.gaps.size(); i++){
        if(x1.gaps[i] > gaps[i])
            gaps[i] = x1.gaps[i];
    }
}


void SimilarityString::condense()
{
    for(signed int i = original.size() - 1; i >= 0; i--){
        if(!mask[i]){
            original.erase(i, 1);
            mask.erase(mask.begin() + i);
            gaps[i] += gaps[i+1] + 1;
            gaps.erase(gaps.begin() + i + 1);
        }
    }
}


void SimilarityString::stripIsles(size_t isleSize)
{
    vector<size_t> isle;
    for(size_t i = 0; i < mask.size(); i++){
        if(mask[i] && !isCtrlChar(original[i]))
            isle.push_back(i);

        if(!mask[i] || isCtrlChar(original[i]) || gaps[i+1] > 0 || i == mask.size() - 1){
            if(isle.size() <= isleSize){
                for(size_t j = 0; j < isle.size(); j++)
                    mask[isle[j]] = false;
            }
            isle.clear();
        }
    }
}


void SimilarityString::stripNums()
{
    for(size_t i = 0; i < mask.size(); i++){
        if(original[i] >= 48 && original[i] <= 57)
            mask[i] = false;
    }
}

void SimilarityString::printToFile(const std::string name, std::vector<std::string>& files){
	fstream f;
    f.open(name.c_str(), ios::out);
	f << "###FileList###" << endl;
	for (int i = 0; i < files.size(); ++i){
		f << files[i] << " " << flush;
	}
	f << endl;
	f << "###FileList###" << endl;
    f << "###ORIGINAL###" << endl;
    f << original << flush;
    f << endl;
    f << "###ORIGINAL###" << endl;
    f << "###MASK###" << endl;
    for (int i = 0; i < mask.size(); ++i){
		f << mask[i] << " " << flush;
	}
	f << endl;
	f << "###MASK###" << endl;
	f << "###GAPS###" << endl;
    for (int i = 0; i < gaps.size(); ++i){
		f << gaps[i] << " " << flush;
	}
	f << endl;
	f << "###GAPS###" << endl;
	f << "###REPLACE STRING###" << endl;
	f << replaceStr << endl;
	f << "###REPLACE STRING###" << endl;
    f.close();
}

void SimilarityString::printConsole(){
	cout << "###ORIGINAL###" << endl;
    cout << original << flush;
    cout << endl;
    cout << "###ORIGINAL###" << endl;
    cout << "###MASK###" << endl;
    for (int i = 0; i < mask.size(); ++i){
		cout << mask[i] << " " << flush;
	}
	cout << endl;
	cout << "###MASK###" << endl;
	cout << "###GAPS###" << endl;
    for (int i = 0; i < gaps.size(); ++i){
		cout << gaps[i] << " " << flush;
	}
	cout << endl;
	cout << "###GAPS###" << endl;
	cout << "###REPLACE STRING###" << endl;
	cout << replaceStr << endl;
	cout << "###REPLACE STRING###" << endl;
}

void SimilarityString::initializeFromFile(const string& input, std::vector<std::string>& usedList){
	std::string usedListHelp = input.substr(input.find("###FileList###") + 15, (input.rfind("###FileList###") - input.find("###FileList###") -16));
	std::string originalHelp = input.substr(input.find("###ORIGINAL###") + 15, (input.rfind("###ORIGINAL###") - input.find("###ORIGINAL###") -16));
	std::string maskHelp = input.substr(input.find("###MASK###") + 11, (input.rfind("###MASK###") - input.find("###MASK###") - 13));
	std::string gapsHelp = input.substr(input.find("###GAPS###") + 11, (input.rfind("###GAPS###") - input.find("###GAPS###") -12));
	std::string replaceHelp = input.substr(input.find("###REPLACE STRING###") + 21, (input.rfind("###REPLACE STRING###") - input.find("###REPLACE STRING###") -22));

	
	// create usedList
	std::istringstream issss(usedListHelp);
	usedList.clear();
	while (issss) {
		string subs;
		issss >> subs;
		if (subs != ""){
			usedList.push_back(subs);
		}
	} 
	
	// create original
	original = originalHelp;	
	
	// create mask
	std::istringstream iss(maskHelp);
	mask.clear();
	while (iss) {
		string subs;
		iss >> subs;
		if (subs == "1"){
			mask.push_back(true);			
		}
		else{
			if (subs != ""){
				mask.push_back(false);
			}
		}
	}
	
	// create gaps
	std::istringstream isss(gapsHelp);
	gaps.clear();
	while (isss) {
		string subs;
		isss >> subs;
		if (subs != ""){
			int val = atoi(subs.c_str());
			gaps.push_back(val);
		}
	} 
	
	// create replaceString
	replaceStr = replaceHelp;
};

void readFromFile(const string& path, string& out)
{
    std::ifstream f(path.c_str());
    if(!f){
		cout << "Warning cannot read file: " << path << endl;
        throw std::runtime_error(string("Cannot read file '") + path + "'!");
	}
		
    out.clear();
    
    while(!f.eof()){
        int c = f.get();
        if(c >= 0 && c < 128){
            out += c;
        }else{
            if(c >= 128){
				out += c;		
			}
        }
    }
}
