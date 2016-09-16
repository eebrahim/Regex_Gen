
/***********************************************************************/
/*                                                                     */
/*   Hirschberg.cpp                                                    */
/*                                                                     */
/*   Part of the hirschberg-align-algorithm to compute a alignment     */
/*   Description : implementation of the hirschberg algorithm          */
/*                 runtime compl. O(n*m)                               */
/*                 space compl.   O(min(n,m))                          */
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

#include "Hirschberg.h"
#include <iostream>
#include "Util.h"
#include <time.h>
#include <cstdlib>

using std::cout;
using std::endl;
using std::vector;
using std::string;
using std::stringstream;


void Hirschberg::forward(const string& x, size_t xStart, size_t xLen, const string& y, size_t yStart, size_t yLen)
{
	time_t start;
	start = time(NULL);
	//cout << "start forward" << endl;
    for(size_t i = 0; i < yLen + 1; i++)
        prefixScore[i] = i * gapExpandPenalty; 

    size_t xIdx = xStart;
    for(size_t i = 1; i < xLen + 1; i++){
        double upperLeft = prefixScore[0];
        prefixScore[0] += gapExpandPenalty;

        size_t yIdx = yStart;
        for(size_t j = 1; j < yLen + 1; j++){
			int a = x[xIdx];
            convertInt(a);
            int b = y[yIdx];
            convertInt(b);
            double min = min3(prefixScore[j-1] + gapExpandPenalty,
                              prefixScore[j] + gapExpandPenalty,
                              upperLeft + distMat[a][b]);
            upperLeft = prefixScore[j];
            prefixScore[j] = min;
            yIdx++;
        }
		if ((time(NULL) -start) > 300){
			cout << "Alignment took too long" << endl;
			exit(0);
		}
        xIdx++;
    }
//    cout << "ende forward" << endl;
}

void Hirschberg::convertInt(int& input)
{	
	if(input < 0){
//		cout << "vorher: " << input << endl;
		input = 256 + input;
//		cout << "nachher: " << input << endl;
	}	
}

void Hirschberg::backward(const string& x, size_t xStart, size_t xLen, const string& y, size_t yStart, size_t yLen)
{
	time_t start;
	start = time(NULL);
    for(size_t i = 0; i < yLen + 1; i++)
        suffixScore[i] = i * gapExpandPenalty; 
    size_t xIdx = xStart + xLen;
    for(size_t i = 1; i < xLen + 1; i++){
        xIdx--;
        double upperLeft = suffixScore[0];
        suffixScore[0] += gapExpandPenalty;
        size_t yIdx = yStart + yLen;
        int a = x[xIdx];
        for(size_t j = 1; j < yLen + 1; j++){
            yIdx--;
            int a = x[xIdx];
            convertInt(a);
            int b = y[yIdx];
            convertInt(b);
            double min = min3(suffixScore[j-1] + gapExpandPenalty,
                              suffixScore[j] + gapExpandPenalty,
                              upperLeft + distMat[a][b]);
            upperLeft = suffixScore[j];
            suffixScore[j] = min;
        }
		if ((time(NULL) -start) > 300){
			cout << "Alignment took too long" << endl;
			exit(0);
		}
    }
//    cout << "ende backward" << endl;
}


void Hirschberg::align1N(char c, const string& seq, size_t seqStart, size_t seqLen, AlignedString& cAligned, AlignedString& seqAligned)
{
    size_t minIdx = seqStart;
    double min = 10000000;
    for(size_t i = seqStart; i < seqStart + seqLen; i++){
		int a = c;
        convertInt(a);
        int b = seq[i];
        convertInt(b);
        if(distMat[a][b] < min){
            min = distMat[a][b];
            minIdx = i;
        }
    }
    if(min < 2 * gapExpandPenalty){
        for(size_t i = seqStart; i < seqStart + seqLen; i++){
            if(i == minIdx){
                cAligned.appendChar(c);
            }else{
                cAligned.appendGap();
            }
            seqAligned.appendChar(seq[i]);
        }
    }else{
        for(size_t i = seqStart; i < seqStart + seqLen; i++){
            if(i == minIdx){
                cAligned.appendChar(c);
                cAligned.appendGap();
                seqAligned.appendGap();
                seqAligned.appendChar(seq[i]);
            }else{
                cAligned.appendGap();
                seqAligned.appendChar(seq[i]);
            }
        }
    }
}

void Hirschberg::align(const string& x, size_t xStart, size_t xLen, const string& y, size_t yStart, size_t yLen)
{
    if(xLen == 0 && yLen == 0){
        return;
    }else if(xLen == 0 && yLen > 0){
        for(size_t i = yStart; i < yStart + yLen; i++){
            alignedX.appendGap();
            alignedY.appendChar(y[i]);
        }
    }else if(xLen > 0 && yLen == 0){
        for(size_t i = xStart; i < xStart + xLen; i++){
            alignedX.appendChar(x[i]);
            alignedY.appendGap();
        }
    }else if(xLen == 1 && yLen >= 1){
        align1N(x[xStart], y, yStart, yLen, alignedX, alignedY);
    }else if(xLen >= 1 && yLen == 1){
        align1N(y[yStart], x, xStart, xLen, alignedY, alignedX);
    }else{
        size_t mid = xLen / 2;
        forward(x, xStart, mid, y, yStart, yLen);
        backward(x, xStart + mid, xLen - mid, y, yStart, yLen);
        double minVal = 100000.0f;
        size_t minJ = yStart;
        for(size_t j = 0; j < yLen + 1; j++){
            double score = prefixScore[j] + suffixScore[yLen - j];
            if(score < minVal){
                minVal = score;
                minJ = j;
            }
        }
        align(x, xStart, mid, y, yStart, minJ);
        align(x, xStart + mid, xLen - mid, y, yStart + minJ, yLen - minJ);
    }
}


void Hirschberg::align(const string& x, const string& y)
{
    size_t n = x.size();
    size_t m = y.size();
    prefixScore.resize(m + 1);
    suffixScore.resize(m + 1);
    alignedX = AlignedString();
    alignedY = AlignedString();
    align(x, 0, n, y, 0, m);
}
