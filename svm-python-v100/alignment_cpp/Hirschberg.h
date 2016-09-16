
/***********************************************************************/
/*                                                                     */
/*   Hirschberg.h                                                      */
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

#ifndef HIRSCHBERG_H_
#define HIRSCHBERG_H_

#include <vector>
#include "Util.h"
#include "AlignedString.h"

class Hirschberg
{
    public:
                                                        Hirschberg(const DistMat& distMat,
                                                                   double gapStartPenalty = 0.0f, double gapExpandPenalty = 1.0f)
                                                               : distMat(distMat), gapStartPenalty(gapStartPenalty), 
                                                                 gapExpandPenalty(gapExpandPenalty) {}
        void                                            forward(const std::string& x, size_t xStart, size_t xLen, 
                                                                const std::string& y, size_t yStart, size_t yLen);
        void                                            backward(const std::string& x, size_t xStart, size_t xLen, 
                                                                 const std::string& y, size_t yStart, size_t yLen);
        void                                            align(const std::string& x, const std::string& y);
        void                                            align(const std::string& x, size_t xStart, size_t xLen,
                                                              const std::string& y, size_t yStart, size_t yLen);
        void                                            align1N(char c, const std::string& seq, size_t seqStart, 
                                                                size_t seqLen, AlignedString& cAligned, 
                                                                AlignedString& seqAligned);
        void											convertInt(int& input);

        AlignedString                                   alignedX;
        AlignedString                                   alignedY;
    private:

        double                                          gapStartPenalty;
        double                                          gapExpandPenalty;
        const DistMat&                                  distMat;
        std::vector<double>                             prefixScore;
        std::vector<double>                             suffixScore;
};

#endif /* HIRSCHBERG_H_ */

