#!/usr/bin python
#coding:utf-8
############################
#define models of song ans playlist
############################

import math
import os
import DBProcess
import sys
import matplotlib.pyplot as plt
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import time

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
def topicDictForNextSongByColdLaw(playlist,songDict,coeff):
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
      for t in range(0,length)
        baseDict[t] = 1.0 / length
    disList.append(KLSim(sTopicDict,baseDict))

  #using auto arima to forecast the kl distance
  vec = robjects.FloatVector(disList)
  ts = robjects.r['ts'](vec)
  fit = robjects.r['auto.arima'](ts)
  next = robjects.r['forecast'](fit,h=1)
  return float(next.rx('mean')[0][0])

#write topic dict of Arima to file to avoid re-computation
def writeTopicDictOfArimaToFile(playlistDict,songDict):
  filename = "txt/arima.txt"
  if os.path.exists(filename):
    print '%s is existing......' % filename
    return
  print 'Begin to write topic dict to file......'
  aFile = open(filename,"w")
  index = 0
  many = len(playlistDict)
  for pid in playlistDict.keys():
    print '%d/%d' % (index,many)
    index += 1
    playlist = playlistDict[pid]
    predictTopicDict = topicDictForNextSongByArima(playlist,songDict)
    content = '%d#' % pid
    for topic in predictTopicDict.keys():
      content = '%s%d:%f,' % (content,topic,predictTopicDict[topic])
    content = content[:len(content)-1]
    aFile.write(content+"\n")
  aFile.close()
  print 'End of writing topic dict to file......'

#read Predicted Topic Dict Of Arima
def readPredictedTopicDictOfArima():
  print 'I am reading predicted topic dict of arima......'
  filename = "txt/arima.txt"
  if not os.path.exists(filename):
    playlistDict = readPlaylistFromFile()
    songDict = readSongFromFile()
    writeTopicDictOfArimaToFile(playlistDict,songDict)
  predictDict = {}
  aFile = open(filename,"r")
  lines = aFile.readlines()
  for line in lines:
    line = line.rstrip("\n")
    items = line.split("#")
    pid = int(items[0])
    topicDict = {}
    topics = items[1].split(",")
    for topic in topics:
      info = topic.split(":")
      tid = int(info[0])
      pro = float(info[1])
      topicDict[tid] = pro
    #normalize
    #make sum of pro equals to 1
    proSum = sum(topicDict.values())
    for tid in topicDict.keys():
      topicDict[tid] = topicDict[tid] / proSum
    predictDict[pid] = topicDict
  print 'Finish reading predicted topic dict of arima......'
  return predictDict

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

#show mae and rmse trends of hybrid methods with different coefficients
def showErrorTrendWithDifferentCoeff_Hybrid(playlistDict,songDict):
  coeffs = [float(x) / 10 for x in range(0,11,1)]
  print coeffs
  maes = []
  rmses = []
  for coeff in coeffs:
    mae,rmse = MAEandRMSE(playlistDict,songDict,5,0,coeff)
    maes.append(mae)
    rmses.append(rmse)
    print mae,rmse
  plt.plot(coeffs,maes,label="MAE")
  plt.plot(coeffs,rmses,label="RMSE")
  plt.title("MAE and RMSE trends of Different Hybrid Coefficients")
  plt.xlabel("lambda")
  plt.ylabel("error")
  plt.legend(loc="upper right")
  plt.savefig("img/hybrid.png")
  plt.show()

#return MAE and RMSE of testing set
#mae = sum of abs of predict value and real value and then return sum divide count of testing set
#RMSE = sum of square of similarity and divide N-1 and the sqrt
# predictType means different methods to predict topic dict of next song
#1: average
#2: most similar
#3: cold law
#4: arima
#5: hybrid
def MAEandRMSE(playlistDict,songDict,predictType,coeff=5.0,lamda = 0.5):
  count = len(playlistDict)
  mae = 0
  rmse = 0
  if predictType == 4 or predictType == 5:
    predictedDict = readPredictedTopicDictOfArima()
  else:
    predictedDict = {}
  for pid in playlistDict.keys():
    playlist = playlistDict[pid]
    if predictType == 1:
      predictTopicDict = topicDictForNextSongByAverage(playlist,songDict)
    elif predictType == 2:
      predictTopicDict = topicDictForNextSongByMostSimilar(playlist,songDict)
    elif predictType == 3:
      predictTopicDict = topicDictForNextSongByColdLaw(playlist,songDict,coeff)
    elif predictType == 4:
      #predictTopicDict = topicDictForNextSongByArima(playlist,songDict)
      predictTopicDict = predictedDict[pid]
    elif predictType == 5:
      predictTopicDict = topicDictForNextSongByHybrid(playlist,songDict,predictedDict,lamda)
    song = songDict[playlist.getLastSid()]
    mae = mae + math.fabs(song.compareWithDict(predictTopicDict))
    rmse = rmse + song.compareWithDict(predictTopicDict)**2
  mae = mae / count
  rmse = rmse / (count - 1)
  rmse = math.sqrt(rmse)
  return mae,rmse

#read all songs from file and construct them
#output is a dict whose key is sid and value is song object
def readSongFromFile():
  print 'I am reading songs from doc-topic file......'
  filename = "txt/songs-doc-topics.txt"
  if os.path.exists(filename):
    songDict = {}
    dtFile = open(filename,"r")
    content = dtFile.readlines()
    #remove the first extra info
    del content[0]
    count = len(content)
    #loop all lines to construct all songs
    for i in range(0,count):
      items = content[i].rstrip('\n').split()
      rIndex = items[1].rfind('/')
      sid = int(items[1][rIndex+1:])
      del items[0]
      del items[0]
      num = len(items)
      j = 0
      topicDict = {}
      while 1:
        #get tid
        tid = int(items[j])
        #move to next:topic pro
        j = j + 1
        #get topic pro
        tpro = float(items[j])
        if tpro == 0:
          print 'pro of topic must bigger than 0......'
          return
        #move to next topic pair
        topicDict[tid] = tpro
        j = j + 1
        if j >= num:
          break
      song = Song(sid,topicDict)
      songDict[sid] = song
    print 'There are %d songs have been read.' % len(songDict)
    dtFile.close()
    print 'Finish reading songs from doc-topic file......'
    return songDict
  else:
    print 'cannot find doc-topic file......'

#read playlists from db and construct dict of playlists
def readPlaylistFromDB():
  playlistDict = {}
  effectivePlaylist = DBProcess.getEffectivePlaylist()
  for pid in effectivePlaylist.keys():
    pList = Playlist(pid,effectivePlaylist[pid])
    playlistDict[pid] = pList
  print 'Thare are %d playlist have been read.' % len(playlistDict)
  return playlistDict

#write playlists to file
def writePlaylistsToFile():
  filename = "txt/playlists.txt"
  if os.path.exists(filename):
    print '%s is existing......' % filename
    return
  else:
    print 'Begin to write playlists......'
    pFile = open(filename,"w")
    effectivePlaylist = DBProcess.getEffectivePlaylist()
    for pid in effectivePlaylist.keys():
      pList = effectivePlaylist[pid]
      content = "%d:" % pid
      count = len(pList)
      for i in range(0,count-1):
        content = "%s%d," % (content,pList[i])
      content = "%s%d" % (content,pList[count-1])
      pFile.write(content+'\n')
    pFile.close()
    print 'End of writing playlists......'

#read playlists from file and construct dict of playlists
def readPlaylistFromFile():
  filename = "txt/playlists.txt"
  if not os.path.exists(filename):
    writePlaylistsToFile()
  pFile = open(filename,"r")
  playlistDict = {}
  lines = pFile.readlines()
  for line in lines:
    line = line.rstrip('\n')
    items = line.split(":")
    pid = int(items[0])
    sids = items[1].split(",")
    pList = [int(sid) for sid in sids]
    playlist = Playlist(pid,pList)
    playlistDict[pid] = playlist
  print 'Thare are %d playlist have been read.' % len(playlistDict)
  return playlistDict
