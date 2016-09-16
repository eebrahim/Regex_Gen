/***********************************************************************/
/*                                                                     */
/*   AlignedString.cpp                                                 */
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



#include "AlignedString.h"
#include <sstream>
#include <iostream>

using std::string;
using std::cout;
using std::endl;


AlignedString::operator string()
{
    std::stringstream ret;

    for(size_t i = 0; i < aligned.size(); i++){
       if(aligned[i] == GAP_CODE)
           ret << '_';
       else
           ret << (char)aligned[i];
    }
    return ret.str();
}


void AlignedString::appendGap()
{
    aligned.push_back(GAP_CODE);
    gaps.back()++;
    originalIndices.push_back(currentIdx);
}


void AlignedString::appendChar(char c)
{
    aligned.push_back(c);
    currentIdx++;
    originalIndices.push_back(currentIdx);
    gaps.push_back(0);
}
