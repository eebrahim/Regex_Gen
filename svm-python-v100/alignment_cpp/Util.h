/***********************************************************************/
/*                                                                     */
/*   Util.h                                                            */
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

#ifndef UTIL_H_
#define UTIL_H_

#include <vector>
#include <string>
#include <sstream>


typedef std::vector<std::vector<double> >    DistMat;


/**
 * returns the minimum of all three arguments
 */
template<class T>
inline T min3(const T& x1, const T& x2, const T& x3)
{
    if(x1 < x2){
        return (x1 < x3 ? x1 : x3);
    }else{
        return (x2 < x3 ? x2 : x3);
    }
}


/**
 * takes a string and returns a one line version
 */
std::string strInline(const std::string& s);


/**
 * creates a default distance matrix with penalty 'match' for matches
 * and penalty 'mismatch' for mismatches
 */
void createDistMat(size_t size, double matchPenalty, double mismatchPenalty, 
                      DistMat& matrix);


/**
 * reads the content of a file into @out
 */
void readFile(const std::string& path, std::string& out);


/**
 * returns whether the character is an ASCII control character
 */
bool isCtrlChar(int c);


/**
 * replaces the first occurence of string @from in @context with @to and returns the result
 */
std::string replaceString(const std::string& context, const std::string& from, const std::string& to);


/**
 * converts T to string
 */
template<class T>
std::string toStr(const T& arg)
{
    std::stringstream ss;
    ss << arg;
    return ss.str();
}


#endif /* UTIL_H_ */

