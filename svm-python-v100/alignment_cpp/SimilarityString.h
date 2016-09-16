
/***********************************************************************/
/*                                                                     */
/*   SimilarityString.h                                                */
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

#ifndef SIMILARITYSTRING_H_
#define SIMILARITYSTRING_H_

#include <vector>
#include <string>
#include <sstream>
#include "AlignedString.h"



class SimilarityString
{
    public:
        std::string                         original;
        std::vector<bool>                   mask;
        std::vector<size_t>                 gaps;     // is of size original.size() +  1 !!

                                            SimilarityString(const std::string& original, const std::string& replaceStr = "{n}") 
                                                : original(original), mask(original.size(), true), 
                                                  gaps(original.size() + 1, 0), replaceStr(replaceStr) { }
                                            operator std::string();
        void                                update(const AlignedString& x1, const AlignedString& x2);
        void                                condense();
        void                                stripIsles(size_t isleSize);
        void                                stripNums();
        void								printToFile(const std::string name, std::vector<std::string>& files);
        void								initializeFromFile(const std::string& input,std::vector<std::string>& usedList);
        void								printConsole();

    private:
        std::string                         replaceStr;
};

void readFromFile(const std::string& path, std::string& out);

#endif /* SIMILARITYSTRING_H_ */

