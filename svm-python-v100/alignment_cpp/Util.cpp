
/***********************************************************************/
/*                                                                     */
/*   Util.h                                                      */
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


#include "Util.h"
#include <fstream>
#include <stdexcept>
#include <iostream>
#include <sstream>

using std::vector;
using std::string;
using std::cout;
using std::endl;


void createDistMat(size_t size, double matchPenalty, double mismatchPenalty, 
                      DistMat& matrix)
{
    matrix = vector<vector<double> >(size, vector<double>(size, mismatchPenalty));

    for(size_t i = 0; i < size; i++)
        matrix[i][i] = matchPenalty;
}


// new readFile wich can add exotic characters wich are often in HTML-Mails

void readFile2(const string& path, string& out)
{
	std::ifstream is;
	char c;

	is.open (path.c_str());        // open file
	out.clear();
	while (is.good())     // loop while extraction from file is possible
	{
		c = is.get();       // get character from file
		if (is.good()){
			out += c;
		}
	}
	is.close();           // close file
//	std::cout << out << std::endl;
}

void readFile(const string& path, string& out)
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
//				cout << "Warning the file contains exotic characters" << endl;
//                throw std::out_of_range(string("File '") + path + string("' contains exotic characters!"));
//				out.clear();
//				out += (-128 + (c - 127));
//				out += -1;
				out += c;
//				std::cout << "Warning the file contains exotic characters: " << c << " in int: " << a << " in datei: " << path << std::endl;
//				std::cout << "bis jetzt: " << out << std::endl;
//				out += c;
//				readFile2(path,out);				
			}
        }
    }
//    cout << "read: " << out << endl;
}






string strInline(const string& s)
{
    std::stringstream ret;
    for(size_t i = 0; i < s.size(); i++){
        char c = s[i];
        if(isCtrlChar(c))
            ret << 'X';
        else
            ret << c;
    }
    return ret.str();
}


bool isCtrlChar(int c)
{
    return (c < 32 && c >= 0) || (c == 127);
}


string replaceString(const string& context, const string& from, const string& to)
{
    size_t foundHere;
    string ret = context;
    if((foundHere = ret.find(from, 0)) != string::npos)
        ret.replace(foundHere, from.size(), to);
    return ret;
}
