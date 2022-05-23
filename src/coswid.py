#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# CoSwID - Code Switching Identification
#
# Author :  Laurent Kevers - University of Corsica
#           kevers_l@univ-corse.fr
#
#           CoSwID is designed to work with ldig as a external library (https://github.com/shuyo/ldig) - MIT license. As a consequence Detector class is partly inspired by ldig code.
#           Note that CoSwID could be adapted to work with another language identification library by adapting the Detector class (the only requirement is to output in the same format)
#           
#

# 
# Copyright University of Corsica -- Laurent Kevers (2022)
# 
# kevers_l@univ-corse.fr
# 
# This software is a computer program whose purpose is Code Switching Identification.
# 
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software. You can use, 
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info". 
# 
# As a counterpart to the access to the source code and rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty and the software's author, the holder of the
# economic rights, and the successive licensors have only limited
# liability.
# 
# In this respect, the user's attention is drawn to the risks associated
# with loading, using, modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean that it is complicated to manipulate, and that also
# therefore means that it is reserved for developers and experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and, more generally, to use and operate it in the 
# same conditions as regards security. 
# 
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
# 

import sys, getopt
import os, errno
import numpy
import codecs
import re
import json
import operator
import socket

#
# INSTALL : Specify where the LDIG folder is located
#
sys.path.append('../../ldig-python3')
import ldig

# 
# Detection of the language word by word, using a sliding window and the language detector LDIG + dictionaries
#
# This script could analyse a TXT file or a small text given directly on the command line.
# Some parameters are adjustable (see help for more information)
# Output is written in an output file (original file postfixed by '.out') or 'default.out' in current directory
#
# This script need external service to proceed
# --> dicServer : if it is not available, a warning is outputed and a default value is attributed
# 
# NB : language codes outputed are 3-chars codes (ISO 639-3); this could be set through a parameter in the future
#





#
# Language detection class
# CoSwID is curently designed to work with ldig as an external library. In order to adapt it to another language identification module, this class has to be modified.
#
class Detector(object):
    def __init__(self, modeldir):
        self.ldig = ldig.ldig(modeldir)
        self.features = self.ldig.load_features()
        self.trie = self.ldig.load_da()
        self.labels = self.ldig.load_labels()
        self.param = numpy.load(self.ldig.param)

    def detect(self, st):
        label, text, org_text = ldig.normalize_text(st)
        events = self.trie.extract_features(u"\u0001" + text + u"\u0001")
        sum = numpy.zeros(len(self.labels))

        for id in sorted(events, key=lambda id:self.features[id][0]):
            phi = self.param[id,]
            sum += phi * events[id]
        sumPositive=sum[sum > 0].sum()
        prob=[]
        for x in sum:
            if x>0 :
                prob.append(x/sumPositive)
            else :
                prob.append(0)
        # put result into JSON format
        labelsList=""
        for x in self.labels:
            if x in toLongLgCode : # always output in long lg code (3 chars)
                x=toLongLgCode[x]
            labelsList+="\"%s\"," % x
        labelsList=labelsList[:-1]
        probList=""
        for x in prob:
            probList+="\"%0.3f\"," % x
        probList=probList[:-1]
        return "{\"labels\":[%s], \"prob\":[%s]}" % (labelsList,probList)



#
# Remove from the results (resJson) all languages that are not in acceptedLg, and normalize probabilities for the remaining lg
#
def recalibrateResults(resJson, acceptedLg):
    res=json.loads(resJson)
    recalibrated={'labels':[],'prob':[]}
    tot=0
    i=0
    for lg in res['labels'] :
        prob=float(res['prob'][i])
        if lg in acceptedLg :
            recalibrated['labels'].append(lg)
            recalibrated['prob'].append(prob)
            tot+=prob
        i+=1
    if tot==0 : # if no lg in acceptedLg : fill with all acceptedLd and balance the probabilities
        nbAccepted=len(acceptedLg)
        for (i,prob) in enumerate(recalibrated['prob']) :
            recalibrated['prob'][i]=1/nbAccepted
    else :
        for (i,prob) in enumerate(recalibrated['prob']) :       # normalize the prob values
            recalibrated['prob'][i]=recalibrated['prob'][i]/tot

    return recalibrated


#
# Update the score for a token and its context (i.e. for a sliding window / a fragment)
#   - resLgID : results of the language identification for a fragment 
#   - toUpdate : ids of the tokens to update
#   - results : structure like [ tokenId : {lg:sum, ... ,lg:sum} , ... , tokenId : {lg:sum, ... ,lg:sum} to update
# For each token in the fragment, add the probabilities for all the languages in the language identification result to the current recorded scores 
# (in other words, for each language in the lgId result, add the given probability to the score of each fragment' token)
#
def updateResults(resLgID, toUpdate, results):
    i=0
    for lg in resLgID['labels'] :
        prob=float(resLgID['prob'][i])
        for idx in toUpdate:
            if lg in results[idx] :
                results[idx][lg]+=prob
            else:
                results[idx][lg]=prob
        i+=1
    return results


#
# For each token, norm the languages score in order to express it as a probability
# (i.e. divide the cumulated score by the length of the sliding window)
#   - Input (values are sums of probabilities) : [ tokenId : {lg:sum, ... ,lg:sum} , ... , tokenId : {lg:sum, ... ,lg:sum} ]
#   - Output (values are normalised probabilities) : [ tokenId : {lg:prob, ... ,lg:prob} , ... , tokenId : {lg:prob, ... ,lg:prob} ]
#
def normLanguageScores(results):
    filteredResults=[]
    for (idx,tokProb) in enumerate(results):
        filteredResults.append({})
        for (lg,prob) in tokProb.items() :  
            filteredResults[idx][lg]=results[idx][lg]/((swSize*2)+1)
    return filteredResults



#
# Remove languages with a probability lesser than (best language score - threshold)
#   - Input : { lg:prob , ... , lg:prob } dictionary with N items
#   - Output : { lg:prob , ... , lg:prob } dictionary with M items, M<=N
#
def removeUnsignificantLanguages(resProb, threshold):
    bestLg=max(resProb.items(), key=operator.itemgetter(1))[0]
    bestLgProb=resProb[bestLg]
    resProbFiltered={}
    for (lg,prob) in resProb.items():
        if prob>=(bestLgProb-threshold) :
            resProbFiltered[lg]=prob
    return resProbFiltered


#
# _lgID_ method for verifying possible languages (when several languages remain after thresholding)
#   = run the language identification on the single token and choose among the possible languages (i.e. the remaining languages after thresholding, listed in 'detectedLg') the language with the highest probability in the new result
#   If there is no common language between the new lgId result (on the single token) and 'detectedLg' list, the returned values will be empty
#   - Input : token="tok", detectedLg=(lg, ... ,lg)
#   - Output : (lg,score)
#
def simpleVote_lgID (token, detectedLg) :
    tokResJson=detector.detect(token)
    tokRes=json.loads(tokResJson)
    print("lgID vote : ")
    print(tokRes)
    vote=""
    bestProba=0
    i=0
    for lg in tokRes['labels'] :
        if lg in detectedLg and float(tokRes['prob'][i])>bestProba :
            vote=lg
            bestProba=float(tokRes['prob'][i])
            res=1
        i+=1

    return (vote,bestProba)


#
# _dico_ method for verifying possible languages (when several languages remain after thresholding)
#   = verify the presence of the token into dictionaries (of possible languages, i.e. the remaining languages after thresholding, listed in 'detectedLg') 
#   If there is no common language between the dico result and 'detectedLg' list, the returned values will be empty
#   If the token is present in more than one language dictionary, the result will be empty (no decision possible)
#   If the token is presnt in one (and only one) language dictionary, the language code will be returned in 'vote', the score ('res') will be 1 
#   - Input : token="tok", detectedLg=(lg, ... ,lg)
#   - Output : (lg,score)
#   __REM__ : this method uses the dictionary server through TCP Socket (port 1112). It must be up and running.
#
def simpleVote_dico (token, detectedLg) :
    res=0
    vote=""
    HOST, PORT = "", 1112
    # clean token
    cleanedToken=re.sub(r"([^%s0-9]+)$"%(alphabet),r"", token) # remove unalpha at the end
    cleanedToken=re.sub(r"^([^%s0-9]+)"%(alphabet),r"", cleanedToken) # remove unalpha at the begining
    cleanedToken=re.sub(r"([^%s0-9]+)"%(alphabet),r" ", cleanedToken) # replace remaining unalpha (inside the token) by a space char
    # extract the longest subtoken (separated by space char)
    cleanedTokenList=cleanedToken.split()
    extractedToken=""
    for tok in cleanedTokenList:
        if len(tok)>len(extractedToken):
            extractedToken=tok
    req=" word_possibleLanguages::%s::%s"%(extractedToken,",".join(detectedLg))   # REM: max legth of req is 2048 chars
    print("Sending request : %s"%req)
    # -- Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dicRes=list()
    try:
        # -- Connect to server and send data
        sock.connect((HOST, PORT))
        sock.sendall(("%s\n"%req).encode(encoding='utf-8'))
        # Receive data from the server and shut down
        received = sock.recv(1024)
        dicRes=json.loads(received)
    except:
        print("ERROR : it wasn't possible to get result from dicServer (%s)"%req)
    finally:
        sock.close()
    print("DicRes: {}".format(dicRes))
    nbLgOk=0
    for (lgIdx,lgDic) in enumerate(dicRes):
        if lgDic in detectedLg:
            print("%s %s in Dico and detectedLg"%(lgIdx,lgDic))
            nbLgOk+=1
            lgToVote=lgIdx
    if nbLgOk==1 :
        # we only decide if there is only one detetcted language amongst the given detectedLg!
        print(" %s (%s) is the only to know the token "%(dicRes[lgToVote],lgToVote))
        vote=dicRes[lgToVote]
        res=1
    else :
        print("No decision (possible lg: %s)"%(nbLgOk))
    return (vote,res)


#
# _full_ method for verifying possible languages (when several languages remain after thresholding)
#   This method will go through three steps :
#       1. lgID method on the token alone : the language with the highest probability wich is also present into detectedLg will score 1 point (into 'votes[lg]')
#       2. dico method : if the token is present into the dictionary of one (and only one) of the predetermined detectedLg, this language will score 1 point (into 'votes[lg]')
#       3. If the two first steps gave different results, try to choose between those languages by comparing to the best language detected globally (bestGlobLg). If it doesn't match with one language chose during steps 1 or 2, do not choose (empty result)
#   - Input : token="tok", detectedLg=(lg, ... ,lg), bestGlobLg="lg"
#   - Output : (lg,score)
#
def voteForAmbigousLg (token, detectedLg, bestGlobLg) :
    votes={x:0 for x in detectedLg}
    totVote=0
    winLg=""
    res=0

    # --- VOTE 1 : first get an estimation from lgID for the token alone (best probability amongst the predetermined detectedLg given as parameter) ---
    tokResJson=detector.detect(token)
    tokRes=json.loads(tokResJson)
    print(tokRes)
    vote1=""
    bestProba=0
    i=0
    for lg in tokRes['labels'] :
        if lg in detectedLg and float(tokRes['prob'][i])>bestProba :
            vote1=lg
            bestProba=float(tokRes['prob'][i])
        i+=1
    if vote1 != "" :
        votes[vote1]+=1
        totVote+=1
    print("Votes after (1): ")
    print(votes)

    # --- VOTE 2 : check dictionary (check if we can find the token into the dictionary of one (and only one) of the predetermined detectedLg) ---
    vote2=""
    HOST, PORT = "", 1112
    # clean token
    cleanedToken=re.sub(r"([^%s0-9]+)$"%(alphabet),r"", token) # remove unalpha at the end
    cleanedToken=re.sub(r"^([^%s0-9]+)"%(alphabet),r"", cleanedToken) # remove unalpha at the begining
    cleanedToken=re.sub(r"([^%s0-9]+)"%(alphabet),r" ", cleanedToken) # replace remaining unalpha (inside the token) by a space char
    # extract the longest subtoken (separated by space char)
    cleanedTokenList=cleanedToken.split()
    extractedToken=""
    for tok in cleanedTokenList:
        if len(tok)>len(extractedToken):
            extractedToken=tok
    req=" word_possibleLanguages::%s::%s"%(extractedToken,",".join(detectedLg))   # REM: max legth of req is 2048 chars
    # -- Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dicRes=list()
    try:
        # -- Connect to server and send data
        sock.connect((HOST, PORT))
        sock.sendall(("%s\n"%req).encode(encoding='utf-8'))
        # Receive data from the server and shut down
        received = sock.recv(1024)
        dicRes=json.loads(received)
    except:
        print("ERROR : it wasn't possible to get result from dicServer (%s)"%req)
    finally:
        sock.close()
    print("DicRes: {}".format(dicRes))
    nbLgOk=0
    for (lgIdx,lgDic) in enumerate(dicRes):
        if lgDic in detectedLg:
            print("%s %s in Dico and detectedLg"%(lgIdx,lgDic))
            nbLgOk+=1
            lgToVote=lgIdx
    if nbLgOk==1 :
        # we only give this vote if there is only one detetcted language amongst the given detectedLg!
        print("Vote2 given to %s (%s)"%(dicRes[lgToVote],lgToVote))
        vote2=dicRes[lgToVote]
        votes[vote2]+=1
        totVote+=1
    else :
        print("Vote2 is not given (possible lg: %s)"%(nbLgOk))
    
    print("Votes after (2) : ")
    print(votes)

    # --- VOTE 3 : if we have 2 different votes, try to decide using global probability (or do not decide at all) ---
    if totVote == 2 and vote1 != vote2 :
        if bestGlobLg in votes :
            votes[bestGlobLg]+=1
        else :
            # cannot decide...
            votes[vote1]=0
            votes[vote2]=0
            totVote=0

    # --- FINAL DECISION AND RESULT ---
    if totVote>0 :
        winLg=max(votes.items(), key=operator.itemgetter(1))[0]
        res=votes[winLg]
    print("FinalVotes: ")
    print(votes)
    return (winLg,res)



# ___ MAIN ___

# --- default parameters ---

# INSTALL : Insert your models.
modelList={ 
            "MODEL1" : "/home/lkevers/Documents/BDLC/laurent/articles-rapports/2022__CoSwID/models/all_9lgs_VERIF/",
            "MODEL2" : "/home/lkevers/Documents/BDLC/laurent/articles-rapports/2022__CoSwID/models/all_9lgs_FILTRE/",
          }

lgList={ 
         "MODEL1" : ["cos","deu","eng","fra","ita","nld","por","ron","spa"],
         "MODEL2" : ["cos","deu","eng","fra","ita","nld","por","ron","spa"],
       }

toShortLgCode={"bul":"bg","ces":"cs","cos":"co","dan":"da","deu":"de","ell":"el","eng":"en","fin":"fi","fra":"fr","hun":"hu","ita":"it","lit":"lt","nld":"nl","pol":"pl","por":"pt","ron":"ro","spa":"es","swe":"sv"}
toLongLgCode={"bg":"bul","cs":"ces","co":"cos","da":"dan","de":"deu","el":"ell","en":"eng","fi":"fin","fr":"fra","hu":"hun","it":"ita","lt":"lit","nl":"nld","pl":"pol","pt":"por","ro":"ron","es":"spa","sv":"swe"}

alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÀÂÄĂÇÈÉÊËÎÏÒÓÔÖȘȚÙÛÜàâäăçèéêëìîïòóôöșțùûüÿŸ"

modelName="FILTER2"
model=modelList[modelName]      # default model
modelLg=lgList[modelName]       # modelLg are the languages supported by the language identification model
text=""                         # text to analyse
swSize=1                        # context size to set the lenght of the sliding window: tot length = (swSize*2)+1) ; (swSize token before) TOK (swSize tokens after)
filterGlob=0                    # filter threshold for global language detetction: probability must be higher than filterGlob; 0 = keep all languages; 0.01 = remove languages with a probability lesser than 0.01 during the global evaluation
significantGap=0.1              # minimum gap/margin between the first and the second languages detected (if the difference is smaller: keep uncertainty); 0 = keep the two first
voteMethod="dico"               # when several lg after thresholding according to GAP, use VOTE METHOD in order to choose; possible values : "full", "lgID", "dico" (REM: to choose the best lg after lg identification, without voting, put GAP to 0)
acceptedLg=modelLg              # it is possible (for the user) to force the use of a subset of languages, DEFAULT = all languages supported by the model
outputFile="default.out"        # default output file

# --- Parsing command line parameters ---
try:
    opts, args = getopt.getopt(sys.argv[1:],"hm:t:c:f:g:v:s:",["model=","txt=","ctxtsize=","fltrtresh=","gap=","vote=","subset="])
except getopt.GetoptError:
    print ('ldig_insideDoc.py -m modelName -t <text or filename> -c <context size> -f <(global) filter threshold> -g <minimum gap to choose lg> -v <voting method> -s <subset of accepted languages: list separated by a "," whithout spaces>')
    print ('ldig_insideDoc.py -h for more options')
    sys.exit(2)

if len(opts)==0 :
    print ('ldig_insideDoc.py -m modelName -t <text or filename> -c <context size> -f <(global) filter threshold> -g <minimum gap to choose lg> -v <voting method> -s <subset of accepted languages: list separated by a "," whithout spaces>')
    print ('ldig_insideDoc.py -h for more options')
    sys.exit(2)


print("%s"%str(opts))
for opt, arg in opts:
    if opt == '-h':
        print ('ldig_insideDoc.py -m <model name> -t <text or filename> -c <context size> -f <(global) filter threshold> -g <minimum gap to choose lg> -v <voting method> -s <subset of accepted languages: list separated by a "," whithout spaces>')
        print ('OR : ldig_insideDoc.py --model <model name> --txt <text or filename> --ctxtsize <context size> --fltrtresh <(global) filter threshold> --gap <min gap to choose lg> --vote <voting method>  --subset <subset of accepted languages: list separated by a "," whithout spaces>')
        print ('DEFAULT : -c 1 -f 0 -g 0.1 -v dico')
        print ('  Model : %s'%model)
        print ('  Languages : %s'%str(modelLg))
        print ('WARNING : dictionary server must be started before using this script')
        sys.exit()
    elif opt in ('-m','--model') :          # MODEL : get model path and possible languages from provided model name
        model=modelList[arg]
        modelLg=lgList[arg]
    elif opt in ('-t','--txt') :            # TEXT : try to open a file, if it's not working use the provided string as text to process
        txtArg=arg
        try :
            ftxt=codecs.open(txtArg,'r',"utf-8")
            text=ftxt.read()
            ftxt.close()
            outputFile="%s.out"%txtArg
            print ("Opening text file : %s [Output to %s]"%(txtArg,outputFile))
        except IOError as e :
            print(os.strerror(e.errno))
            print("Using the provided chars as text to analyse [Output to %s]"%outputFile)
            text=txtArg
    elif opt in ('-c','--ctxtsize') :
        swSize=int(arg)                     # CONTEXT SIZE : number of token(s) before AND after to build a fragment (total size=(swSize*2)+1)
    elif opt in ('-f','--fltrtresh') :
        filterGlob=float(arg)               # FILTER TRESHOLD : threshold filter to keep only globally detected languages (keep all : 0)
    elif opt in ('-g','--gap'):
        significantGap=float(arg)           # GAP : Treshold for choosing a language or keeping uncertainty between two languages (0 = do not choose between the two first if there are more than one language)
    elif opt in ('-v','--vote'):
        voteMethod=arg
    elif opt in ('-s', '--subset'):
        acceptedLg=arg.split(',')           # ACCEPTED LANGUAGES : user defined possible languages


# --- initialisation of the language detector ---
detector = Detector(model)


# --- Output selected parameters for user information ---
print("___ Parameters ___\n")
print("Total length of the sliding Window : %s"%((swSize*2)+1))
print("Treshold for keeping globally detected languages (0=all) : %s"%filterGlob)
print("Treshold for choosing a language or keeping uncertainty between two languages : %s"%significantGap)
print("Voting method : %s"%voteMethod)
print ('Model : %s'%model)
print("Languages : %s"%str(acceptedLg))
print("__________________")


# --- Tokenize and preprocessing ---

# _ Preprocessing/cleaning _
cleanedText=text.replace('\u00AC','') # U+00AC	NOT SIGN / SIGNE NÉGATION
cleanedText=cleanedText.replace('\u00AD','') # U+00AD	SOFT HYPHEN / TRAIT D'UNION CONDITIONNEL

# _ Norm spaces / tabulations _
cleanedText=re.sub(r"\s+",r" ",cleanedText) 
#print("%s --> %s"%(text,cleanedText))

# _ Split on whitespaces _
tokens=cleanedText.split()
nbToks=len(tokens)
results=[]
cleanedTokens=[]
for tok in tokens:
    results.append({})  # initialize an empty dictionary for each token in order to store future results
    cleanedTok=re.sub(r"([^%s0-9]+)$"%(alphabet),r"", tok) # remove unalpha at the end
    cleanedTok=re.sub(r"^([^%s0-9]+)"%(alphabet),r"", cleanedTok) # remove unalpha at the begining
    cleanedTokens.append(cleanedTok)


# --- detect languages globally ---
globRes=detector.detect(cleanedText)
globRes=json.loads(globRes)
print (globRes)
possibleLg=[]  # IF filterGlob==0 THEN possibleLg will be equivalent to acceptedLg ELSE possibleLg will be the intersection between languages that are detected globally _AND_ the user defined language (if set, or by default the languages defined in the chosen model)
bestGlobLg=""
bestGlobProb=0
for (idx,prob) in enumerate(globRes["prob"]) :
    if globRes["labels"][idx] in acceptedLg :
        if float(prob)>=filterGlob : # allow to remove languages with a global probability less than 'filterGlob' (given as a parameter; default value 0 keeps all languages)
            possibleLg.append(globRes["labels"][idx])
            # REM : filtering on a list of possible languages detected globally could work for a sentence or a small paragraph with a small number of different languages,
            # BUT it is not appropriate for a big text with many different languages --> BY DEFAULT it is recommended to use all languages !!!
        if float(prob) > bestGlobProb :
            bestGlobLg=globRes["labels"][idx]
            bestGlobProb=float(prob)
print ("Possible languages found globally (user defined -- if any -- and globally detected) : ")
print (possibleLg)
print ("Best language globally detected : %s"%bestGlobLg)
if len(possibleLg)==0:
    print("[ERROR] : no language available!")
    sys.exit()

# --- Generate sliding window data & detect language (we use CLEANED tokens to build fragment with sliding window) ---
print("Nombre de tokens : %s"%nbToks)
curTok=0
fragment=""
while curTok<nbToks :
    # construct and test the 'fragment' around the token
    toksToUpdate=[]
    # initialize fragment with current token
    fragment=cleanedTokens[curTok]
    toksToUpdate.append(curTok)
    # add swSize tokens BEFORE curTok
    i=1
    while i<=swSize:
        if curTok-i<0 :
            # begining of the text : get "previous" tokens at the end of the text to have a full sliding window (TODO: this could be modified for something more relevant in the future)
            fragment="%s %s"%(cleanedTokens[nbToks+(curTok-i)],fragment)
            toksToUpdate.append(nbToks+(curTok-i))
        else :
            # add token before the current fragment
            fragment="%s %s"%(cleanedTokens[curTok-i],fragment)
            toksToUpdate.append(curTok-i)
        i+=1
    # add swSize tokens AFTER curTok
    i=1
    while i<=swSize:
        if curTok+i>=nbToks :
            # end of the text : get "following" tokens at the begining of the text to have a full sliding window (TODO: this could be modified for something more relevant in the future)
            fragment="%s %s"%(fragment,cleanedTokens[(curTok+i)-nbToks])
            toksToUpdate.append((curTok+i)-nbToks)
        else :
            # add token after the current fragment
            fragment="%s %s"%(fragment,cleanedTokens[curTok+i])
            toksToUpdate.append(curTok+i)
        i+=1
    
    # detect language of a fragment
    print("%s : "%fragment)
    fragRes=detector.detect(fragment)

    # recalibrate probabilities with regard to possibleLg
    print("raw : %s"%str(fragRes))
    recRes=recalibrateResults(fragRes,possibleLg)
    print("recalibrated : %s"%str(recRes))

    print("Tokens to update [cur, prev, next] :")
    print(toksToUpdate)
    # add the results to the already collected data
    results=updateResults(recRes, toksToUpdate, results)
    curTok+=1   # move forward the sliding window (1 token)


# --- Finalize the results  ---
# this step is needed to transform scores into probabilities
filteredResults=normLanguageScores(results)


# --- Outputs in a human friendly format (we use ORIGINAL tokens to output) ---
print("OUTPUT")
fout=codecs.open(outputFile,'w',"utf-8")
for (idx,tok) in enumerate(tokens):
    print ("[%s] : %s"%(idx,tok))
    resProb=filteredResults[idx]
    print(resProb)
    # tresholding (remove lg with probability < (best language probability) - margin
    resProbTresholded=removeUnsignificantLanguages(resProb, significantGap)
    print ("Thresholding :")
    print(resProbTresholded)
    tokRes="%s : "%tok
    # if there are still several possibilities, use the voting procedure
    detectedLg=resProbTresholded.keys()
    bestLg=""
    score=0
    winLg=""
    ccl=""
    if len(resProbTresholded)>1 :
        print ("Vote for remaining languages after thresholding :")
        if voteMethod=="full":
            (winLg,score)=voteForAmbigousLg (tok, detectedLg, bestGlobLg)
        elif voteMethod=="lgID":
            (winLg,score)=simpleVote_lgID (tok, detectedLg)
        else :
            (winLg,score)=simpleVote_dico (tok, detectedLg)
        print(" %s : %s"%(winLg,score))
        if score>0 :
            ccl=" => %s (%s)"%(winLg,score)
        else: # if voting doesn't help, keep the language with the higher probability
            bestLg=max(resProbTresholded.items(), key=operator.itemgetter(1))[0]
            ccl="=> %s (%s)"%(bestLg,resProbTresholded[bestLg])
    else :
        bestLg=max(resProbTresholded.items(), key=operator.itemgetter(1))[0]
    # display all the languages kept after tresholding in descending order (for information)
    prob=1
    while (prob>0):
        lg=max(resProbTresholded.items(), key=operator.itemgetter(1))[0]
        prob=resProbTresholded[lg]
        if prob>0 :
            tokRes="%s%s (%s)  "%(tokRes, lg, prob)
        resProbTresholded[lg]=0
    print ("%s%s"%(tokRes,ccl))
    if len(winLg)==0 :
        fout.write("%s\t%s\n"%(tok,bestLg))
    else:
        fout.write("%s\t%s\n"%(tok,winLg))

fout.close()

