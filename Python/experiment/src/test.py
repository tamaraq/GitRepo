#!/usr/bin python
#coding:utf-8
############################
#give some test function
############################

import time
import persist
import predict
import util
import logging
import os
import math
import matplotlib.pyplot as plt
import sys
import const

reload(sys)
sys.setdefaultencoding('utf-8')

# set log's localtion and level
logging.basicConfig(filename=os.path.join(os.getcwd(),'../log/test_log_%s.txt' % const.DATASET_NAME),level=logging.DEBUG,format='%(asctime)s-%(levelname)s:%(message)s')

#show mae and rmse trends of most similarhybrid methods with different coefficients
def showRecallTrendWithDifferentCoeff_MostSimilarHybrid():
  songDict = persist.readSongFromFile()
  playlistDict = persist.readPlaylistFromFile()
  coeffs = [float(x) / 10 for x in range(0,11,1)]
  print coeffs
  recalls = []
  for coeff in coeffs:
    print 'hybrid  coeff = %f' % coeff
    recDict = predict.getRecDict(playlistDict,songDict,4,coeff)
    recall,precision,f1 = util.getTopNIndex(recDict,playlistDict)
    recalls.append(recall)
  plt.plot(coeffs,recalls,label="Recall")
  plt.title("Recall trends of Different Hybrid Coefficients")
  plt.xlabel("lambda")
  plt.ylabel("Recall")
  plt.legend(loc="upper right")
  plt.savefig("../img/%s_arima_similar_%d_%d.png" % (const.DATASET_NAME,const.TOPIC_NUM,const.TOP_N))
  plt.show()

#show mae and rmse trends of average hybrid methods with different coefficients
def showRecallTrendWithDifferentCoeff_AverageHybrid():
  songDict = persist.readSongFromFile()
  playlistDict = persist.readPlaylistFromFile()
  coeffs = [float(x) / 10 for x in range(0,11,1)]
  print coeffs
  recalls = []
  for coeff in coeffs:
    print 'hybrid  coeff = %f' % coeff
    recDict = predict.getRecDict(playlistDict,songDict,5,coeff)
    recall,precision,f1 = util.getTopNIndex(recDict,playlistDict)
    recalls.append(recall)
  plt.plot(coeffs,recalls,label="Recall")
  plt.title("Recall trends of Different Hybrid Coefficients")
  plt.xlabel("lambda")
  plt.ylabel("Recall")
  plt.legend(loc="upper right")
  plt.savefig("../img/%s_arima_average_%d_%d.png" % (const.DATASET_NAME,const.TOPIC_NUM,const.TOP_N))
  plt.show()

#test traditional method
#0: most similar
#1: average
#2: Arima
#3: Arima + Similar
#4: Arima + Average
#5: Matrix Factorization
def testRecMethod(recType = 0):
  info = '############%s#############' % util.getMethodName(recType)
  start_time = time.time()
  songDict = persist.readSongFromFile()
  allPlaylist = persist.readPlaylistFromFile()
  recallTotal = 0.0
  precisionTotal = 0.0
  f1Total = 0.0
  maeTotal = 0.0
  rmseTotal = 0.0
  for scale in range(10):
    playlistDict = allPlaylist[scale]
    if recType == const.ARIMA:
      recDict = predict.getRecDict(playlistDict,songDict,recType,scale)
    elif recType == const.SIMILAR:
      recDict = predict.getRecDict(playlistDict,songDict,recType,scale)
    elif recType == const.AVG:
      recDict = predict.getRecDict(playlistDict,songDict,recType,scale)
    elif recType == const.POPULAR:
      recDict = predict.getRecDictOfMostPopular(songDict,playlistDict,scale)
    elif recType == const.ARIMA_SIMILAR:
      recDict = predict.getRecDict(playlistDict,songDict,recType,scale)
    elif recType == const.ARIMA_AVG:
      recDict = predict.getRecDict(playlistDict,songDict,recType,scale)
    elif recType == const.MF:
      recDict = predict.getRecDictOfMF(songDict,playlistDict,scale)
    elif recType == const.KNN:
      recDict = predict.getRecDictOfUserKNN(songDict,playlistDict,scale)
    elif recType == const.LSA:
      recDict = predict.getRecDictOfLSA(songDict,playlistDict,scale)
    elif recType == const.MARKOV:
      recDict = predict.getRecDictOfMostMarkov(songDict,playlistDict,scale)
    elif recType == const.PATTERN:
      recDict = predict.getRecDictOfMostPattern(songDict,playlistDict,scale)
    elif recType == const.RANDOM:
      recDict = predict.getRecDictOfRandom(songDict,playlistDict,scale)
    recall,precision,f1 = util.getTopNIndex(recDict,playlistDict)
    mae,rmse = util.getMAEandRMSE(recDict,playlistDict,songDict)
    recallTotal += recall
    precisionTotal += precision
    f1Total += f1
    maeTotal += mae
    rmseTotal += rmse

  recall = recallTotal / 10
  precision = precisionTotal / 10
  f1 = f1Total / 10
  mae = maeTotal / 10
  rmse = rmseTotal / 10

  print info
  logging.info(info)
  print 'Recall = ',recall
  logging.info('Recall = %f' % recall)
  print 'Precision = ',precision
  logging.info('Precision = %f' % precision)
  print 'F1-Score = ',f1
  logging.info('F1-Score = %f' % f1)
  print 'MAE = ',mae
  logging.info('MAE = %f' % mae)
  print 'RMSE = ',rmse
  logging.info('RMSE = %f' % rmse)
  print 'Consumed: %ds' % (time.time()-start_time)
  logging.info('Consumed: %ds' % (time.time()-start_time))

#test traditional method
#0: most similar
#1: average
#2: Arima
#3: Arima + Similar
#4: Arima + Average
#5: Matrix Factorization
def getErrorOfRecMethod(recType = 0):
  start_time = time.time()
  songDict = persist.readSongFromFile()
  allPlaylist = persist.readPlaylistFromFile()
  recalls = []
  precisions = []
  f1s = []
  maes = []
  rmses = []
  for scale in range(10):
    playlistDict = allPlaylist[scale]
    if recType == const.ARIMA:
      recDict = predict.getRecDict(playlistDict,songDict,recType,scale)
    elif recType == const.SIMILAR:
      recDict = predict.getRecDict(playlistDict,songDict,recType,scale)
    elif recType == const.AVG:
      recDict = predict.getRecDict(playlistDict,songDict,recType,scale)
    elif recType == const.POPULAR:
      recDict = predict.getRecDictOfMostPopular(songDict,playlistDict,scale)
    elif recType == const.ARIMA_SIMILAR:
      recDict = predict.getRecDict(playlistDict,songDict,recType,scale)
    elif recType == const.ARIMA_AVG:
      recDict = predict.getRecDict(playlistDict,songDict,recType,scale)
    elif recType == const.MF:
      recDict = predict.getRecDictOfMF(songDict,playlistDict,scale)
    elif recType == const.KNN:
      recDict = predict.getRecDictOfUserKNN(songDict,playlistDict,scale)
    elif recType == const.LSA:
      recDict = predict.getRecDictOfLSA(songDict,playlistDict,scale)
    elif recType == const.MARKOV:
      recDict = predict.getRecDictOfMostMarkov(songDict,playlistDict,scale)
    elif recType == const.PATTERN:
      recDict = predict.getRecDictOfMostPattern(songDict,playlistDict,scale)
    elif recType == const.RANDOM:
      recDict = predict.getRecDictOfRandom(songDict,playlistDict,scale)
    index = 0
    for topN in range(1,const.TOP_N,1):
      recall,precision,f1 = util.getTopNIndex(recDict,playlistDict,topN)
      mae,rmse = util.getMAEandRMSE(recDict,playlistDict,songDict,topN)
      if scale == 0:
        recalls.append(recall)
        precisions.append(precision)
        f1s.append(f1)
        maes.append(mae)
        rmses.append(rmse)
      else:
        recalls[index] += recall
        precision2[index] += precision
        f1s[index] += f1
        maes[index] += mae
        rmses[index] += rmse
      index += 1

  #cal the avg value
  recalls = [recall / 10 for recall in recalls]
  precisions = [precision / 10 for precision in precisions]
  f1s = [f1 / 10 for f1 in f1s]
  maes = [mae / 10 for mae in maes]
  rmses = [rmse / 10 for rmse in rmses]

  #logging info to log
  index = 0
  for topN in range(1,const.TOP_N,1):
    print '%d:TopN = %d:%f %f %f %f %f' % (recType,topN,recalls[index],precisions[index],f1s[index],maes[index],rmses[index])
    logging.info('%d>%d:%f %f %f %f %f' % (recType,topN,recalls[index],precisions[index],f1s[index],maes[index],rmses[index]))
    index += 1
  end_time = time.time()
  print 'Consumed:%d' % (end_time-start_time)
  return recalls,precisions,f1s,maes,rmses  

#show all recommend results with different methods
def showResult():
  logging.info('I am in showResult......')
  filename = "../txt/%s_testall_%d_%d.txt" % (const.DATASET_NAME,const.TOPIC_NUM,const.TOP_N)
  x = range(1,const.TOP_N,1)
  result = [[[] for i in range(5)] for i in range(const.METHOD_SIZE)]
  #read result from file to result
  if os.path.exists(filename):
    print '%s is existing......' % filename    
    rFile = open(filename,"r")
    lines = rFile.readlines()
    for line in lines:
      line = line.rstrip('\n')
      items = line.split("INFO:")
      line = items[1]
      items = line.split(":")
      ids = items[0]
      values = items[1]
      idItems = ids.split(">")
      mid = int(idItems[0])
      topN = int(idItems[1])
      valueItems = values.split()
      result[mid][0].append(float(valueItems[0]))
      result[mid][1].append(float(valueItems[1]))
      result[mid][2].append(float(valueItems[2]))
      result[mid][3].append(float(valueItems[3]))
      result[mid][4].append(float(valueItems[4]))
    rFile.close()
  else:
    rFile = open(filename,"w")
    rFile.close()
  #if some method is not in file, recreate it
  for mid in range(const.METHOD_SIZE):
    if len(result[mid][0]) == 0:
      recalls,precisions,f1s,maes,rmses = getErrorOfRecMethod(mid)
      result[mid][0] = recalls
      result[mid][1] = precisions
      result[mid][2] = f1s
      result[mid][3] = maes
      result[mid][4] = rmses

  for index in range(const.METHOD_SIZE):
    for no in range(len(result[const.RANDOM][1])):
      if result[const.RANDOM][1][no] == 0:
        result[index][1][no] = 1.0
      else:
        result[index][1][no] = (result[index][1][no] - result[const.RANDOM][1][no]) / result[const.RANDOM][1][no]

      if result[const.RANDOM][2][no] == 0:
        result[index][2][no] = 1.0
      else:
        result[index][2][no] = (result[index][2][no] - result[const.RANDOM][2][no]) / result[const.RANDOM][2][no]

  #plt img of comparing with pure method
  for index in range(5):
    plt.figure(index)
    indexName = util.getIndexName(index)
    mids = [const.ARIMA,const.SIMILAR,const.AVG,const.POPULAR]
    for mid in mids:
      plt.plot(x,result[mid][index],label=util.getMethodName(mid))
    plt.title("%s of Different Recommend Algorithms" % indexName)
    plt.xlabel("Number of recommendations")
    plt.ylabel(indexName)
    plt.legend()
    plt.xlim(1,160)
    plt.savefig("../img/pure_%s_%s_%d_%d.png" % (const.DATASET_NAME,indexName,const.TOPIC_NUM,const.TOP_N))
    #plt.show()

  #plt img of comparing with pure method
  for index in range(5):
    plt.figure(index+5)
    indexName = util.getIndexName(index)
    mids = [const.ARIMA,const.ARIMA_SIMILAR,const.ARIMA_AVG]
    for mid in mids:
      plt.plot(x,result[mid][index],label=util.getMethodName(mid))
    plt.title("%s of Different Recommend Algorithms" % indexName)
    plt.xlabel("Number of recommendations")
    plt.ylabel(indexName)
    plt.legend()
    plt.xlim(1,160)
    plt.savefig("../img/hybrid_%s_%s_%d_%d.png" % (const.DATASET_NAME,indexName,const.TOPIC_NUM,const.TOP_N))
    #plt.show()

  #plt img of comparing with pure method
  for index in range(5):
    plt.figure(index+10)
    indexName = util.getIndexName(index)
    mids = [const.ARIMA,const.KNN,const.MF,const.PATTERN,const.MARKOV]
    for mid in mids:
      plt.plot(x,result[mid][index],label=util.getMethodName(mid))
    plt.title("%s of Different Recommend Algorithms" % indexName)
    plt.xlabel("Number of recommendations")
    plt.ylabel(indexName)
    plt.legend()
    plt.xlim(1,160)
    plt.savefig("../img/cf_%s_%s_%d_%d.png" % (const.DATASET_NAME,indexName,const.TOPIC_NUM,const.TOP_N))
    #plt.show()

  #plt img of comparing with pure method
  for index in range(5):
    plt.figure(index+15)
    indexName = util.getIndexName(index)
    mids = [const.ARIMA,const.PATTERN,const.LSA,const.MARKOV]
    for mid in mids:
      plt.plot(x,result[mid][index],label=util.getMethodName(mid))
    plt.title("%s of Different Recommend Algorithms" % indexName)
    plt.xlabel("Number of recommendations")
    plt.ylabel(indexName)
    plt.legend()
    plt.xlim(1,160)
    plt.savefig("../img/sequential_%s_%s_%d_%d.png" % (const.DATASET_NAME,indexName,const.TOPIC_NUM,const.TOP_N))
    #plt.show()

  logging.info('I am out showResult......')
