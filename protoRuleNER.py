'''
Copyright (c) <year>, <copyright holder>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of the FreeBSD Project.
'''

from nltk.tokenize import TweetTokenizer
import nltk
import re
from langdetect import detect

splitter = ['!',';',',',':','.','/','and']

def checkRange(tokenText, next):
    length = len(tokenText)
    if next >= length:
        return False
    else:
        return True

def preProcess (tokenizedText):
    if re.match(r"RT", tokenizedText[0]):
        tokenizedText.pop(0)

    hashRegex = re.compile(r"#\S+")
    tokenizedText = [s for s in tokenizedText if not hashRegex.match(s)]

    if re.match(r"\d+", tokenizedText[0]):
        tokenizedText.pop(0)

    if tokenizedText[0] in splitter:
        tokenizedText.pop(0)

    return tokenizedText

def postProcess(tempText):
    # needed to add in the functions
    cleanText = ' '.join(tempText)
    return cleanText

def chunkKM(tokenizedText):
    firstRegex = re.compile(r"(k|K)(m|M)\d*")
    secondRegex = re.compile(r"\d+$")
    thirdRegex = re.compile(r"\d+\.\d+$")
    temp = tokenizedText

    for i in tokenizedText:

        if firstRegex.match(i):
            pos = tokenizedText.index(i)
            # print(pos)
            iter = 1

            if checkRange(tokenizedText, pos+iter) and secondRegex.match(tokenizedText[pos + iter]):
                # temp[pos:pos + iter +1] = [''.join(tokenizedText[pos:pos + iter+1])]
                print(tokenizedText[pos + iter])
                # print('enter 2')
                iter += 1
                if checkRange(tokenizedText, pos+iter) and tokenizedText[pos + iter] == '.':
                    # print('enter 2.1')
                    iter += 1

                    if checkRange(tokenizedText, pos+iter) and secondRegex.match(tokenizedText[pos + iter]):
                        # print('enter 2.2')
                        iter += 1

                temp[pos:pos + iter + 1] = [''.join(tokenizedText[pos:pos + iter + 1])]

            if checkRange(tokenizedText, pos+iter) and tokenizedText[pos + iter] == '.':
                # print('enter 3')
                iter += 1

                if checkRange(tokenizedText, pos+iter) and secondRegex.match(tokenizedText[pos + iter]):
                    # print('enter 3.1')
                    iter += 1
                temp[pos:pos + iter] = [''.join(tokenizedText[pos:pos + iter])]

            if checkRange(tokenizedText, pos+iter) and thirdRegex.match(tokenizedText[pos + iter]):
                iter += 1
                temp[pos:pos + iter] = [''.join(tokenizedText[pos:pos + iter])]

    return temp
stateRemovalWords = ['is','still','expect','fatal','possible','the','an','a','slightly','long','traffic']
def postProcessState(state):
    cleanedState = [x for x in state if x not in stateRemovalWords]
    return cleanedState

tWords = ['from', 'to', 'near', 'along', 'towards', 'after', 'in','on', 'between','In','affecting','at','into','via']
cWords = ['due']
bWords = ['to', 'till', 'in','towards']
bkWords = ['the', 'almost','The']
eWords = ['roundabout', 'intersection', 'traffic light', 'highway', 'point','exit','hospital','school','toll',
          'station','city','mall','interchange','town','building','hotel','bridge']
pattern= [['VBP','NNS'],['VBN','RP'],['VBP','NN'],['VBG','NNS'],['VBZ','JJ'],['RB','JJ'],['NN','NNS'],
          ['DT','NN'],['CD','NN'],['JJ','NN'],['CD','NNP','NN'],['CD','NNS','VBP']]
state = []
loc = []
tag = []


sampleNegWords = ['slow','brutal','accident','delays','busy','crawl','delay','backed','flood']
samplePosWords = ['smooth','cleared']


def nerExtract(text):
    score = 0
    state = []
    loc = []
    text = text.strip()
    text = re.sub(r":", ' : ', text)
    tknzr = TweetTokenizer()
    tokenizedText = tknzr.tokenize(text)
    tokenizedText = preProcess(tokenizedText)
    tokenizedText = chunkKM(tokenizedText)

    listOflist = []
    lastPoint = 0
    iterSplit = 0

    while iterSplit < len(tokenizedText):
        if tokenizedText[iterSplit] in splitter:
            listOflist.append(tokenizedText[lastPoint:iterSplit])
            lastPoint = iterSplit + 1
        elif iterSplit == len(tokenizedText) - 1:
            listOflist.append(tokenizedText[lastPoint:iterSplit + 1])
        iterSplit += 1

    listOflist = [x for x in listOflist if x != []]

    for segText in listOflist:

        posTag = nltk.pos_tag(segText)
        # if choice == 'LOCATION':
        #     print(posTag)

        for eachTWord in tWords:
            if eachTWord in segText:
                indices = [i for i, x in enumerate(segText) if x == eachTWord]
                for tPos in indices:
                    iter = 1
                    tempLoc = []
                    segmentText = segText[tPos:tPos + 6]
                    for eachBkWord in bkWords:
                        while checkRange(segText, tPos + iter):
                            if segText[tPos + iter] == eachBkWord:
                                iter += 1
                            else:
                                break

                    # if checkRange(segText, tPos + iter) and re.match(r"NN\?*", posTag[tPos + iter][1]):
                    if checkRange(segText, tPos + iter) and (re.match(r"NNP", posTag[tPos + iter][1]) or re.match(r"-NONE-", posTag[tPos + iter][1])):
                        while checkRange(segText, tPos + iter):
                            if re.match(r"NNP", posTag[tPos + iter][1])or re.match(r"-NONE-", posTag[tPos + iter][1]):
                                tempLoc.append(segText[tPos + iter])
                                iter += 1
                            else:
                                break
                    else:
                        for eachBWord in bWords:
                            if eachBWord in segmentText:
                                pos2 = segmentText.index(eachBWord)
                                tempLoc = segmentText[:pos2]

                    if checkRange(segText, tPos + iter) and segText[tPos + iter] in eWords:
                        tempLoc.append(segText[tPos + iter])

                    if len(tempLoc) > 5:
                        if tempLoc:
                            loc.append(postProcess(tempLoc))
                    else:
                        if tempLoc:
                            loc.append(' '.join(tempLoc))
        # ##############################################################################################

        iter = 0

        for eachBkWord in bkWords:
            while checkRange(segText, iter):
                if segText[iter] == eachBkWord:
                    iter += 1
                else:
                    break

        if re.match(r"NNP", posTag[iter][1]):
            tempLoc = []

            while checkRange(segText, iter) and re.match(r"NN\?*", posTag[iter][1]):
                tempLoc.append(posTag[iter][0])
                iter += 1
            loc.append(' '.join(tempLoc))

        # ###############################################################################################

        tempState=[]
        tag = []
        for i in posTag:
            tag.append(i[1])

        for eachPattern in pattern:

            iter = 0
            if checkRange(segText, iter):
                while iter + 1 < len(segText):
                    if (tag[iter] == eachPattern[0]):
                        for x in range(len(eachPattern)):
                            if checkRange(segText, iter+x) and tag[iter + x] == eachPattern[x]:
                                tempState.append(segText[iter + x])
                            else:
                                tempState = []
                        if tempState:
                            tempState = postProcessState(tempState)
                            state.append(' '.join(tempState))
                            tempState = []
                    iter += 1

    # if choice == 'LOCATION':
    #     # print('location called')
    #     return loc
    # # print(loc)
    # if choice == 'STATE':
    #     # print('state called')
    #     return state
    for eachWord in state:
        if eachWord in sampleNegWords:
            score -=1
        if eachWord in samplePosWords:
            score +=1

    # hard coded contextual analysis
    textList = []
    for eachLoc in loc:
        eachLoc = eachLoc.strip()
        if score > 0:
            textList.append(eachLoc + ' should be clear and okay for driving.')
        elif score < 0:
            textList.append('It is not advisable to get near to ' + eachLoc + ' now.')
        else:
            textList.append('There might be something going on in '+ eachLoc + ' now.')
    return textList

