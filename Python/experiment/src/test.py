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

reload(sys)
sys.setdefaultencoding('utf-8')

# set log's localtion and level
logging.basicConfig(filename=os.path.join(os.getcwd(),'../log/test_log.txt'),level=logging.DEBUG,format='%(asctime)s-%(levelname)s:%(message)s')

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
  plt.savefig("../img/hybrid_trend.png")
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
  plt.savefig("../img/average_hybrid_trend.png")
  plt.show()

#show mae and rmse trends of average similar methods with different coefficients
def showRecallTrendWithDifferentCoeff_AverageSimilar():
  songDict = persist.readSongFromFile()
  playlistDict = persist.readPlaylistFromFile()
  coeffs = [float(x) / 10 for x in range(0,11,1)]
  print coeffs
  recalls = []
  for coeff in coeffs:
    print 'hybrid  coeff = %f' % coeff
    recDict = predict.getRecDict(playlistDict,songDict,8,coeff)
    recall,precision,f1 = util.getTopNIndex(recDict,playlistDict)
    recalls.append(recall)
  plt.plot(coeffs,recalls,label="Recall")
  plt.title("Recall trends of Different Hybrid Coefficients")
  plt.xlabel("lambda")
  plt.ylabel("Recall")
  plt.legend(loc="upper right")
  plt.savefig("../img/average_similar_trend.png")
  plt.show()

#show mae and rmse trends of cold-law methods with different coefficients
def showRecallTrendWithDifferentCoeff_ColdLaw():
  songDict = persist.readSongFromFile()
  playlistDict = persist.readPlaylistFromFile()
  coeffs = [float(x) / 10 for x in range(0,100,10)]
  recalls = []
  for coeff in coeffs:
    print 'coldlaw coeff = %f' % coeff
    recDict = predict.getRecDict(playlistDict,songDict,2,0.5,coeff)
    recall,precision,f1 = util.getTopNIndex(recDict,playlistDict)
    recalls.append(recall)
  plt.plot(coeffs,recalls,label="Recall")
  plt.title("Recall trends of Different ColdLaw Coefficients")
  plt.xlabel("coefficients")
  plt.ylabel("Recall")
  plt.legend(loc="upper right")
  plt.savefig("../img/coldlaw_trend.png")
  #plt.show()

#show weight trends of different coefficients
def showColdLawWithDifferentCoeff():
  coeffs = [0.25,0.5,0.75,1.0,5.0]
  x = range(0,20,1)
  for coeff in coeffs:
    weight = [1*math.pow(math.e,-1*coeff*delta) for delta in x]
    label = "coeff = %f" % coeff
    plt.plot(x,weight,label=label)
  plt.xlabel("time")
  plt.ylabel("weight")
  plt.title("Weight Trend of Cold Law with Different Coefficients")
  plt.legend(loc = "upper right")
  plt.savefig("../img/cold-law.png")
  plt.show()

#test traditional method
#0: most similar
#1: average
#2: cold law
#3: Arima
#4: Arima + Similar
#5: Arima + Average
#6: Dis-Arima
#7: Sd-Arima 
#8: Sd-SVM
def testRecMethod(recType = 0):
  info = '############%s#############' % util.getMethodName(recType)
  start_time = time.time()
  songDict = persist.readSongFromFile()
  playlistDict = persist.readPlaylistFromFile()
  if recType < 6:
    recDict = predict.getRecDict(playlistDict,songDict,recType)
  elif recType == 6:
    recDict = predict.getRecDictOfDis(playlistDict,songDict)
  elif recType == 7 or recType == 8:
    recDict = predict.getRecDictOfSd(playlistDict,songDict,recType)
  recall,precision,f1 = util.getTopNIndex(recDict,playlistDict)
  mae,rmse = util.getMAEandRMSE(recDict,playlistDict,songDict)
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
#2: cold law
#3: Arima
#4: Arima + Similar
#5: Arima + Average
#6: Dis-Arima
#7: Sd-Arima 
#8: Sd-SVM
def getErrorOfRecMethod(recType = 0):
  start_time = time.time()
  songDict = persist.readSongFromFile()
  playlistDict = persist.readPlaylistFromFile()
  if recType < 6:
    if recType == 4:
      recDict = predict.getRecDict(playlistDict,songDict,recType,0.4)
    elif recType == 5:
      recDict = predict.getRecDict(playlistDict,songDict,recType,0.9)
    else:
      recDict = predict.getRecDict(playlistDict,songDict,recType)
  elif recType == 6:
    recDict = predict.getRecDictOfDis(playlistDict,songDict)
  elif recType == 7 or recType == 8:
    recDict = predict.getRecDictOfSd(playlistDict,songDict,recType)
  else:
    print '0 <= recType <= 8......'
    return
  recalls = []
  precisions = []
  f1s = []
  maes = []
  rmses = []
  for topN in range(1,311,10):
    recall,precision,f1 = util.getTopNIndex(recDict,playlistDict,topN)
    mae,rmse = util.getMAEandRMSE(recDict,playlistDict,songDict,topN)
    recalls.append(recall)
    precisions.append(precision)
    f1s.append(f1)
    maes.append(mae)
    rmses.append(rmse)
    print '%d:TopN = %d:%f %f %f %f %f' % (recType,topN,recall,precision,f1,mae,rmse)
    logging.info('%d>%d:%f %f %f %f %f' % (recType,topN,recall,precision,f1,mae,rmse))
  return recalls,precisions,f1s,maes,rmses  

def compareWithAverage(recType):
  if recType == 1:
    print 'You compare average with itsself......'
    return
  logging.info('I am in compareWithAverage......')
  filename = "../txt/testall.txt"
  x = range(1,311,10)
  result = [[[] for i in range(5)] for i in range(2)]
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
      if mid == 1:
        result[mid][0].append(float(valueItems[0]))
        result[mid][1].append(float(valueItems[1]))
        result[mid][2].append(float(valueItems[2]))
        result[mid][3].append(float(valueItems[3]))
        result[mid][4].append(float(valueItems[4]))
      elif mid == recType:
        result[0][0].append(float(valueItems[0]))
        result[0][1].append(float(valueItems[1]))
        result[0][2].append(float(valueItems[2]))
        result[0][3].append(float(valueItems[3]))
        result[0][4].append(float(valueItems[4]))
      else:
        continue
    rFile.close()
  #if some method is not in file, recreate it
  if len(result[0][0]) == 0:
    recalls,precisions,f1s,maes,rmses = getErrorOfRecMethod(recType)
    result[0][0] = recalls
    result[0][1] = precisions
    result[0][2] = f1s
    result[0][3] = maes
    result[0][4] = rmses
  if len(result[1][0]) == 0:
    recalls,precisions,f1s,maes,rmses = getErrorOfRecMethod(1)
    result[1][0] = recalls
    result[1][1] = precisions
    result[1][2] = f1s
    result[1][3] = maes
    result[1][4] = rmses
  for index in range(5):
    plt.figure(index)
    plt.plot(x,result[0][index],label=util.getMethodName(recType))
    plt.plot(x,result[1][index],label=util.getMethodName(1))
    plt.title("%s of Different Recommend Algorithms" % indexName)
    plt.xlabel("Number of recommendations")
    plt.ylabel(indexName)
    plt.savefig("../img/%s_with_average.png" % indexName)
    #plt.show()
  logging.info('I am out compareWithAverage......')

#show all recommend results with different methods
def showStatistics():
  logging.info('I am in showStatistics......')
  filename = "../txt/testall.txt"
  x = range(1,311,10)
  result = [[[] for i in range(5)] for i in range(9)]
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
  #if some method is not in file, recreate it
  for mid in range(9):
    if len(result[mid][0]) == 0:
      recalls,precisions,f1s,maes,rmses = getErrorOfRecMethod(mid)
      result[mid][0] = recalls
      result[mid][1] = precisions
      result[mid][2] = f1s
      result[mid][3] = maes
      result[mid][4] = rmses
  #plt first five method on one img
  for index in range(5):
    plt.figure(index)
    indexName = util.getIndexName(index)
    for mid in range(0,6,1):
      plt.plot(x,result[mid][index],label=util.getMethodName(mid))
    plt.title("%s of Different Recommend Algorithms" % indexName)
    plt.xlabel("Number of recommendations")
    plt.ylabel(indexName)
    if index == 0:
      plt.legend(loc="lower right")
    else:
      plt.legend()
    plt.savefig("../img/%s.png" % indexName)
    #plt.show()
  
  #plt last five method on one img
  for index in range(5):
    plt.figure(index+5)
    indexName = util.getIndexName(index)
    for mid in range(4,9,1):
      plt.plot(x,result[mid][index],label=util.getMethodName(mid))
    plt.title("%s of Different Recommend Algorithms" % indexName)
    plt.xlabel("Number of recommendations")
    plt.ylabel(indexName)
    plt.legend()
    plt.savefig("../img/%s_.png" % indexName)
    #plt.show()
  logging.info('I am out showStatistics......')
