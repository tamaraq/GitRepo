#!/usr/bin python
#coding:utf-8
############################
#define models of song ans playlist
############################

import math
import sys
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import persist
import util
import matplotlib.pyplot as plt
from sklearn.svm import SVC

#set default encoding
reload(sys)
sys.setdefaultencoding("utf-8")

#get predicted topic dict of next song by averaging all songs' topic distribution
#we treat it as the user's global preference
def topicDictForNextSongByAverage(playlist,songDict):
  #get playlist's training list
  trainingList = playlist.getTrainingList()
  count = len(trainingList)
  topicDict = {}
  #add each key of every song to topicDict
  for i in range(0,count):
    sid = trainingList[i]
    sTopicDict = songDict[sid].getTopicDict()
    for key in sTopicDict.keys():
      if key not in topicDict:
        topicDict[key] = sTopicDict[key]
      else:
        topicDict[key] = topicDict[key] + sTopicDict[key]
  #average
  for key in topicDict.keys():
    topicDict[key] = topicDict[key] / count
  return topicDict

#get predicted topic dict of next song using most similar to last song
def topicDictForNextSongByMostSimilar(playlist,songDict):
  trainingList = playlist.getTrainingList()
  count = len(trainingList)
  sid = trainingList[count-1]
  return songDict[sid].getTopicDict()

#get predicted topic dict of next song by cold law
def topicDictForNextSongByColdLaw(playlist,songDict,coeff = 5.0):
  #get playlist's training list
  trainingList = playlist.getTrainingList()
  count = len(trainingList)
  topicDict = {}
  totalWeight = 0
  #add each key of every song to topicDict
  for i in range(0,count):
    delta = count-i
    weight = math.pow(math.e,-1*coeff*delta)
    sid = trainingList[i]
    sTopicDict = songDict[sid].getTopicDict()
    for key in sTopicDict.keys():
      if key not in topicDict:
        topicDict[key] = sTopicDict[key] * weight
      else:
        topicDict[key] = topicDict[key] + sTopicDict[key] * weight
    totalWeight = totalWeight + weight
  #average
  for key in topicDict.keys():
    topicDict[key] = topicDict[key] / totalWeight
  return topicDict

#get predicted topic dict of next song by auto_arima
def topicDictForNextSongByArima(playlist,songDict):
  importr("forecast")
  #get playlist's training list
  trainingList = playlist.getTrainingList()
  count = len(trainingList)
  #predicted topic distribution
  topicDict = {}
  #multi-dimensional time series
  #the number of topics is the dimension
  tsDict = {}
  #loop every song in training list
  #add distribution of sids to tsDict to construct some time series
  for i in range(0,count):
    sid = trainingList[i]
    sTopicDict = songDict[sid].getTopicDict()
    for key in sTopicDict.keys():
      #if the topic do not exist,new a list and append it to dict
      if key not in tsDict:
        tsDict[key] = []
        tsDict[key].append(sTopicDict[key])
      #else append it directly
      else:
        tsDict[key].append(sTopicDict[key])
  #using auto arima to forecast the next value of all time series
  total = 0
  for key in tsDict.keys():
    if total == 0:
      total = len(tsDict[key])
    if len(tsDict[key]) != total:
      print '....Error:Time Series do not have same length......'
      return
    vec = robjects.FloatVector(tsDict[key])
    ts = robjects.r['ts'](vec)
    fit = robjects.r['auto.arima'](ts)
    next = robjects.r['forecast'](fit,h=1)
    topicDict[key] = float(next.rx('mean')[0][0])
  return topicDict

#get predicted topic dict of next song by hybrid method
def topicDictForNextSongByHybrid(playlist,songDict,arimaDict,lamda):
  trainingList = playlist.getTrainingList()
  pid = playlist.getPid()
  count = len(trainingList)
  sid = trainingList[count-1]
  lastTopicDict =  songDict[sid].getTopicDict()
  lastSum = sum(lastTopicDict.values())
  arima = arimaDict[pid]
  arimaSum = sum(arima.values())
  topicDict = {}
  for topic in lastTopicDict.keys():
    pro = lamda*lastTopicDict[topic] + (1 - lamda)*arima[topic]
    topicDict[topic] = pro
  return topicDict

#get recommend songs list of playlist comparing with target dict
def getRecSongs(songDict,topN,tarDict):
  recDict = {}
  for sid in songDict.keys():
    song = songDict[sid]
    topicDict = song.getTopicDict()
    sim = util.KLSim(topicDict,tarDict)
    recDict[sid] = sim
  recList = sorted(recDict.iteritems(),key=lambda x:x[1])
  result = []
  for i in range(0,topN):
    result.append(recList[i][0])
  return result

#generate rec dict
#0: most similar
#1: average
#2: cold law
#3: arima
#4: hybrid
#default: most similar
def getRecDict(playlistDict,songDict,recType = 0,lamda = 0.5,coeff = 5.0,topN = 300):
  recDict = {}
  if recType == 3 or recType == 4:
    arimaDict = persist.readPredictedTopicDictOfArima()
  index = 0
  count = len(playlistDict)
  if recType == 0:
    typeName = "Most Similar"
  elif recType == 1:
    typeName = "Average"
  elif recType == 2:
    typeName = "Cold Law"
  elif recType == 3:
    typeName = "Arima"
  elif recType == 4:
    typeName = "Hybrid"
  else:
    typeName = "Most Similar"
  for pid in playlistDict.keys():
    print '%s:%d/%d' % (typeName,index,count)
    playlist = playlistDict[pid]
    if recType == 0:
      tarDict = topicDictForNextSongByMostSimilar(playlist,songDict)
    elif recType == 1:
      tarDict = topicDictForNextSongByAverage(playlist,songDict)
    elif recType == 2:
      tarDict = topicDictForNextSongByColdLaw(playlist,songDict,coeff)
    elif recType == 3:
      tarDict = arimaDict[pid]
    elif recType == 4:
      tarDict = topicDictForNextSongByHybrid(playlist,songDict,arimaDict,lamda)
    else:
      tarDict = topicDictForNextSongByMostSimilar(playlist,songDict)
    recSong = getRecSongs(songDict,topN,tarDict)
    recDict[pid] = recSong
    index = index + 1
  return recDict

#get predicted KL distance with base distribution by auto_arima
def getPredictedKLDisByArima(playlist,songDict):
  importr("forecast")
  #get playlist's training list
  trainingList = playlist.getTrainingList()
  count = len(trainingList)
  #define base diatribution and dis list
  baseDict = {}
  disList = []
  #loop every song in training list
  #add distribution of sids to tsDict to construct some time series
  for i in range(0,count):
    sid = trainingList[i]
    sTopicDict = songDict[sid].getTopicDict()
    if len(baseDict) == 0:
      length = len(sTopicDict)
      for t in range(0,length):
        baseDict[t] = 1.0 / length
    disList.append(util.KLSim(sTopicDict,baseDict))

  #using auto arima to forecast the kl distance
  vec = robjects.FloatVector(disList)
  ts = robjects.r['ts'](vec)
  fit = robjects.r['auto.arima'](ts)
  next = robjects.r['forecast'](fit,h=1)
  #robjects.r['plot'](next)
  return float(next.rx('mean')[0][0])

#get recommend songs list of playlist by dis
def getRecSongsOfDis(playlist,songDict,topN,tarDis):
  recDict = {}
  baseDict = {}
  trainingList = playlist.getTrainingList()
  size = len(trainingList)
  lastTopicDict = songDict[trainingList[size-1]].getTopicDict()
  for sid in songDict.keys():
    song = songDict[sid]
    topicDict = song.getTopicDict()
    if len(baseDict) == 0:
      length = len(topicDict)
      for i in range(0,length):
        baseDict[i] = 1.0 / length
    baseDis = util.KLSim(topicDict,baseDict)
    value = math.fabs(baseDis-tarDis)
    recDict[sid] = value
  recList = sorted(recDict.iteritems(),key=lambda x:x[1])
  result = []
  for i in range(0,topN):
    result.append(recList[i][0])
  return result

#generate rec dict
def getRecDictOfDis(playlistDict,songDict,topN = 300):
  recDict = {}
  index = 0
  count = len(playlistDict)
  for pid in playlistDict.keys():
    print 'Dis:%d/%d' % (index,count)
    playlist = playlistDict[pid]
    tarDis = getPredictedKLDisByArima(playlist,songDict)
    recSong = getRecSongsOfDis(playlist,songDict,topN,tarDis)
    recDict[pid] = recSong
    index = index + 1
  return recDict

#get predicted sd by auto_arima
def getPredictedSdByArima(playlist,songDict):
  importr("forecast")
  #get playlist's training list
  trainingList = playlist.getTrainingList()
  count = len(trainingList)
  #sd list
  sdList = []
  #loop every song in training list
  #add distribution of sids to tsDict to construct some time series
  for i in range(0,count):
    sid = trainingList[i]
    sd = songDict[sid].getSd()
    sdList.append(sd)

  #using auto arima to forecast the kl distance
  vec = robjects.FloatVector(sdList)
  ts = robjects.r['ts'](vec)
  fit = robjects.r['auto.arima'](ts)
  next = robjects.r['forecast'](fit,h=1)
  #robjects.r['plot'](next)
  return float(next.rx('mean')[0][0])

#get predicted sd by SVM
def getPredictedSdBySVM(playlist,songDict):
  #get playlist's training list
  trainingList = playlist.getTrainingList()
  count = len(trainingList)
  #sd list
  sdList = []
  #loop every song in training list
  #add distribution of sids to tsDict to construct some time series
  for i in range(0,count):
    sid = trainingList[i]
    sd = songDict[sid].getSd()
    sdList.append(sd)
  
  K = 5
  trainingX = [sdList[i:K+i] for i in range(0,count-K)]
  trainingY = [sdList[i] for i in range(K,count)]
  testingX = sdList[count-K:count]
  svc = SVC()
  fit = svc.fit(trainingX,trainingY)
  predict = fit.predict(testingX)
  return float(predict)

#get recommend songs list of playlist by hamming dis
def getRecSongsOfSd(playlist,songDict,topN,tarSd):
  recDict = {}
  trainingList = playlist.getTrainingList()
  size = len(trainingList)
  for sid in songDict.keys():
    song = songDict[sid]
    sd = song.getSd()
    value = math.fabs(sd - tarSd)
    recDict[sid] = value
  recList = sorted(recDict.iteritems(),key=lambda x:x[1])
  result = []
  for i in range(0,topN):
    result.append(recList[i][0])
  return result

#generate rec dict
def getRecDictOfSd(playlistDict,songDict,recType = 0,topN = 300):
  recDict = {}
  index = 0
  count = len(playlistDict)
  preSds = []
  realSds = []
  for pid in playlistDict.keys():
    print 'Sd:%d/%d' % (index,count)
    playlist = playlistDict[pid]
    if recType == 0:
      tarSd = getPredictedSdByArima(playlist,songDict)
    elif recType == 1:
      tarSd = getPredictedSdBySVM(playlist,songDict)
    preSds.append(tarSd)
    realSds.append(songDict[playlist.getLastSid()].getSd())
    recSong = getRecSongsOfSd(playlist,songDict,topN,tarSd)
    recDict[pid] = recSong
    index = index + 1
  plt.plot(preSds,label="predict Sds")
  plt.plot(realSds,label="real Sds")
  plt.title("Predict Sds and Real Sds")
  plt.xlabel("pid")
  plt.ylabel("sd")
  plt.legend()
  if recType == 0:
    plt.savefig("../img/sdArimarror.png")
  elif recType == 1:
    plt.savefig("../img/sdSVMError.png")
  plt.show()
  return recDict