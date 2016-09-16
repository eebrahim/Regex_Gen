/***********************************************************************/
/*                                                                     */
/*   AlignedString.h                                                   */
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

#ifndef ALIGNEDSTRING_H_
#define ALIGNEDSTRING_H_

#include <string>
#include <vector>

const signed int GAP_CODE = -5;

class AlignedString
{
    public:
        std::vector<signed int>                aligned;
        std::vector<size_t>                    gaps;           // always of size of original.size() + 1
        std::vector<size_t>                    originalIndices;

                                               AlignedString() : gaps(1, 0), currentIdx(-1) {}
                                               operator std::string();
        void                                   appendGap();
        void                                   appendChar(char c);
    private:
        size_t                                 currentIdx;
};

#endif /* ALIGNEDSTRING_H_ */

