#!/usr/bin python
#coding:utf-8
############################
#give some useful function
############################

import math
import smtplib
from email.mime.text import MIMEText

#getHammingDict
def getHammingDict(topicDict,baseDict):
  hammingDict = {}
  for topic in topicDict.keys():
    delta = topicDict[topic] - baseDict[topic]
    if delta >= 0:
      hammingDict[topic] = 1
    else:
      hammingDict[topic] = 0
  return hammingDict

#calculate hamming distance of two signal vector
def hammingDis(sigDict1,sigDict2):
  count = 0
  for key in sigDict1.keys():
    if sigDict1[key] != sigDict2[key]:
      count = count + 1
  return count

#calculate cosine similarity of two distribution
#input are two topic dicts
#output is the cosine similarity
def cosineSim(topicDict1,topicDict2):
  dotProduct = 0
  dictPower1 = 0
  dictPower2 = 0
  for key in topicDict1.keys():
    if key not in topicDict2:
      print '%d is not in another dict...' % key
      return
    else:
      dotProduct = dotProduct + topicDict1[key] * topicDict2[key]
      dictPower1 = dictPower1 + topicDict1[key]**2
      dictPower2 = dictPower2 + topicDict2[key]**2
  similarity = dotProduct / (math.sqrt(dictPower1) * math.sqrt(dictPower2))
  return similarity

#calculate KL distance of two distribution
#input are two topic dicts
#output is the cosine similarity
def KLDis(topicDict1,topicDict2):
  distance = 0
  for key in topicDict1.keys():
    if key not in topicDict2:
      print '%d is not in another dict...' % key
      return
    else:
      pro1 = topicDict1[key]
      pro2 = topicDict2[key]
      if pro1 <= 0:
        pro1 = 1.0 / 10000000
      if pro2 <= 0:
        pro2 = 1.0 / 10000000
      distance = distance + pro1 * math.log(pro1 / pro2)
  return distance

#calculate KL similarity of two distribution
#input are two topic dicts
#output is the cosine similarity
def KLSim(topicDict1,topicDict2):
  dis1 = KLDis(topicDict1,topicDict2)
  dis2 = KLDis(topicDict2,topicDict1)
  return (dis1 + dis2) / 2.0

#calculate Hellinger distance of two discrete distribution
def HellDis(topicDict1,topicDict2):
  K = len(topicDict1)
  hellDis = 0
  for key in topicDict1.keys():
    if key not in topicDict2:
      print '%d is not in another dict...' % key
      return
    else:
      if topicDict1[key] < 0:
        topicDict1[key] = 1.0 / 10000000
      if topicDict2[key] < 0:
        topicDict2[key] = 1.0 / 10000000
      hellDis += (math.sqrt(topicDict1[key]) - math.sqrt(topicDict2[key]))**2
  hellDis = math.sqrt(hellDis)
  hellDis *= 1/math.sqrt(2)
  return hellDis

#universe interface to calculate similarity of two distributions
def similarity(topicDict1,topicDict2):
  return HellDis(topicDict1,topicDict2)

#calculate recall,preision and F1-Score
def getTopNIndex(recDict,playlistDict,topN = 300):
  if topN < 0:
    print 'topN should be > 0'
    return 0
  hit = 0
  testNum = len(playlistDict)
  total = 0
  for pid in playlistDict.keys():
    playlist = playlistDict[pid]
    lastSid = playlist.getLastSid()
    recList = recDict[pid]
    recNum = len(recList)
    if recNum >= topN:
      recNum = topN
    newList = recList[0:recNum]
    total = total + recNum
    if lastSid in newList:
      hit = hit + 1
  recall = float(hit * 1.0) / testNum
  if total == 0:
    total = 1
  precision = float(hit * 1.0) / total
  if recall == 0 and precision == 0:
    f1 = 0
    print 'recall = 0 and precision = 0'
  else:
    f1 = 2 * ((recall * precision) / (recall + precision))
  return recall,precision,f1

#calculate mae and rmse
def getMAEandRMSE(recDict,playlistDict,songDict,topN = 300):
  if topN < 0:
    print 'topN should be > 0'
    return 0
  mae = 0
  rmse = 0
  testNum = len(playlistDict)
  for pid in playlistDict.keys():
    playlist = playlistDict[pid]
    lastSid = playlist.getLastSid()
    tarDict = songDict[lastSid].getTopicDict()
    recList = recDict[pid]
    recNum = len(recList)
    if recNum >= topN:
      recNum = topN
    totalError = 0
    for i in range(0,recNum):
      recSid = recList[i]
      recTopicDict = songDict[recSid].getTopicDict()
      recError = KLSim(recTopicDict,tarDict)
      totalError = totalError + recError
    if recNum == 0:
      recNum = 0.0001
    avgError = float(totalError*1.0) / recNum
    mae = mae + math.fabs(avgError)
    rmse = rmse + avgError**2
  mae = mae / testNum
  rmse = rmse / (testNum - 1)
  rmse = math.sqrt(rmse)
  return mae,rmse

#return text info of method
def getMethodName(mid):
  if mid == 0:
    return "Most Similar"
  elif mid == 1:
    return "Average"
  elif mid == 2:
    return "ColdLaw"
  elif mid == 3:
    return "Arima"
  elif mid == 4:
    return "Arima+Similar"
  elif mid == 5:
    return "Arima+Average"
  elif mid == 6:
    return "Dis-Arima"
  elif mid == 7:
    return "Sd-Arima"
  elif mid == 8:
    return "Sd-SVM"
  else:
    print '%d does not exist......' % mid
    return

#return text info of validation
def getIndexName(index):
  if index == 0:
    return "Hit Ratio"
  elif index == 1:
    return "Precision"
  elif index == 2:
    return "F1-Score"
  elif index == 3:
    return "MAE"
  elif index == 4:
    return "RMSE"
  else:
    print '%d does not exist......' % index
    return

#send email to me
def sendMail(to,subtitle,content):
    #定义发送列表
    #mailto_list = ['wwssttt@163.com']
    #设置服务器
    mail_host = 'smtp.163.com'
    mail_port = '25'
    mail_user = 'wwssttt'
    mail_password = 'hxl111wst'
    mail_postfix = '163.com'
    me = mail_user+'<'+mail_user+'@'+mail_postfix+'>'
    msg = MIMEText(content)
    msg['Subject'] = subtitle
    msg['From'] = mail_user+'@'+mail_postfix
    msg['To'] = to
    try:
        send_smtp = smtplib.SMTP()
        send_smtp.connect(mail_host,mail_port)
        send_smtp.login(mail_user,mail_password)
        send_smtp.sendmail(me,to,msg.as_string())
        send_smtp.close()
        print 'success'
        return True
    except Exception as e:
        print(str(e))
        print 'false'
