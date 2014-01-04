#!/usr/bin python
#coding=utf-8
############################
# @author Jason Wong
# @date 2013-12-08
############################
# connect to aotm db
# generate documents of songs
############################

import MySQLdb
import sys
import numpy
import pylab as pl
import logging
import os
from nltk.stem.lancaster import LancasterStemmer
import DBProcess
import matplotlib.pyplot as plt
import util
import const

# reload sys and set encoding to utf-8
reload(sys)
sys.setdefaultencoding('utf-8')
# set log's localtion and level
logging.basicConfig(filename=os.path.join(os.getcwd(),'log/docgenerate_log.txt'),level=logging.DEBUG,format='%(asctime)s-%(levelname)s:%(message)s')

#read stop words from stop words file
# return stop words list
def readStopwordsFromFile(filename):
  words = []

  stopfile = open(filename,"r")
  while 1:
    line = stopfile.readline()
    if not line:
      break
    line = line.rstrip('\n')
    line = line.strip()
    line = line.lower()
    if line not in words:
      words.append(line)
  stopfile.close()
  return words

#combine two stop words lists
#return a combined stopwords list/file
def combineTwoStopwordsFile():
  if os.path.exists("../txt/stopwords.txt"):
    print "stop words file is existing......"
    return
  first = readStopwordsFromFile("EnglishStopWords_datatang.txt")
  second = readStopwordsFromFile("EnglishStopWords_url.txt")
  result = list(set(first).union(set(second)))
  rFile = open("stopwords.txt","w")
  for word in result:
    rFile.write(word+'\n')
  rFile.close()
  return result

#get stopwords list
stopwords = readStopwordsFromFile("../txt/stopwords.txt")
vocabulary = []

#add word to word dictionary
#tagDict:word dictionary of a song(word:count)
#tagStr:tag string
#tagCount:the count of tag's appearance
def addItemToDict(tagDict,tagStr,tagCount):
  #include global variable
  global vocabulary
  #stemmer
  st = LancasterStemmer()
  #split tagStr
  item = "%20".join(tagStr.split())
  item = item.lower()
  #stem
  item = st.stem(item)
  #remove stopwords and too short words
  if item not in stopwords:
    if item not in tagDict:
      tagDict[item] = tagCount
    else:
      tagDict[item] = tagDict[item] + tagCount
    #add item to vocabulary list
    if item not in vocabulary:
      vocabulary.append(item)
    

#generate tag dictionary of given song
def generateTagDictofSong(sname,aname,tags):
  tagDict = {}
  #add sname to tagDict
  addItemToDict(tagDict,sname,100)
  #add aname to tagDict
  addItemToDict(tagDict,aname,100)
  for item in sname.split():
    addItemToDict(tagDict,item,100)
  #add aname to tagDict
  for item in aname.split():
    addItemToDict(tagDict,item,100)
  #split tags<tag:count>
  tagInfos = tags.split("##==##")
  #loop every tag Information
  for tagInfo in tagInfos:
    #cannot use split(":") because some tag contains ":" like <hello:world:3>
    #find : from right index
    index = tagInfo.rfind(":")
    tagStr = tagInfo[:index]
    tagCount = tagInfo[index+1:]
    #avoid some tags without count
    #if a tag has no count, ignore it
    if len(tagCount) == 0:
      continue
    else:
      #add tag to dict
      addItemToDict(tagDict,tagStr,int(tagCount))
  return tagDict

#rm dir,no matter it is empty or not
def rmDir(whichdir):
  if not os.path.exists(whichdir):
    return
  print 'begin to rm dir %s' % whichdir
  for dirpath,dirname,filenames in os.walk(whichdir):
    for filename in filenames:
      filepath = os.path.join(dirpath,filename)
      os.remove(filepath)
  print 'delete %d files in %s' % (len(filenames),whichdir)
  os.rmdir(whichdir)
  print 'end of rming dir %s' % whichdir

#generate document of given song from its tagDict
def generateDocofSong(sid,tagDict):
  result = []
  #repeat: write tag into file
  for tag in tagDict.keys():
    count = (int)(tagDict[tag] / 4)
    tag = "%s " % tag
    result.append(tag*count)
  return " ".join(result)

#generate all docs of all songs
#get statistics of tags,listener number and playcount
def generateAotmDocs():
  if const.DATASET_NAME != 'Aotm':
    print 'dataset is not Aotm'
    return 
  #rm folder songs
  rmDir("../txt/%s_songs" % const.DATASET_NAME)
  #mkdir songs
  os.mkdir("../txt/%s_songs" % const.DATASET_NAME)  
  #filename = "../txt/songDocs.txt"
  #if os.path.exists(filename):
    #print '%s is existing...' % filename
    #return

  #docFile = open(filename,'w')

  try:
    #connect db and select db name
    conn = MySQLdb.Connect(host=const.DBHOST,user=const.DBUSER,passwd=const.DBPWD,port=const.DBPORT,charset=const.DBCHARSET)
    cur = conn.cursor()
    conn.select_db(const.DBNAME)
    #get song dict and playlist dict from DBProcess
    songDict,playlistDict = DBProcess.genEffectivePlaylist()
    #tags'count:number
    countDict = {}
    #listeners'count:number
    lisDict = {}
    #playcount:number
    playDict = {}
    songNum = len(songDict)
    index = 0
    for sid in songDict.keys():
      sFile = open('../txt/songs/%s' % sid,'w')
      index = index + 1
      print 'begin to generate file of song %d(%d/%d)' % (sid,index,songNum)
      logging.debug('begin to generate file of song %d(%d/%d)' % (sid,index,songNum))
      #select info of a song with sid
      cur.execute('select sname,aname,count,tags,listeners,playcount,useful from effective_song where id = %d' % sid)
      result = cur.fetchone()
      sname = result[0]
      aname = result[1]
      count = int(result[2])
      #update count dict
      if count not in countDict:
        countDict[count] = 1
      else:
        countDict[count] = countDict[count] + 1
      tags = result[3]
      #update listener dict
      listeners = int(result[4])
      if listeners not in lisDict:
        lisDict[listeners] = 1
      else:
        lisDict[listeners] = lisDict[listeners] + 1
      #update playcount dict
      playcount = int(result[5])
      if playcount not in playDict:
        playDict[playcount] = 1
      else:
        playDict[playcount] = playDict[playcount] + 1

      useful = int(result[6])
      if useful == 0:
        print '%d useful is 0...' % sid
        logging.warning('%d useful is 0...' % sid)
        return

      tagDict = generateTagDictofSong(sname,aname,tags)
      text =  generateDocofSong(sid,tagDict)
      sFile.write(text)
      #md5 = util.getMD5("%s,%s" % (sname,aname))
      #info = '%s X   \"%s\"\n' % (md5,text)
      #docFile.write(info)
      sFile.close()
      print 'end of generating file of song %d' % sid
      logging.debug('end of generating file of song %d' % sid)
    conn.commit()
    cur.close()
    conn.close()
    #docFile.close()
    print 'There are %d different tag count' % len(countDict)
    print 'There are %d different listener numbers' % len(lisDict)
    print 'There are %d different playcount numbers' % len(playDict)
    return countDict,lisDict,playDict
  except MySQLdb.Error,e:
    print 'Mysql Error %d:%s' % (e.args[0],e.args[1])
    logging.error('Mysql Error %d:%s' % (e.args[0],e.args[1]))

def Lastfm_generateDocs():
  if const.DATASET_NAME != 'Lastfm':
    print 'dataset is not Lastfm'
    return 
  #rm folder songs
  rmDir("../txt/%s_songs" % const.DATASET_NAME)
  #mkdir songs
  os.mkdir("../txt/%s_songs" % const.DATASET_NAME)  
  try:
    #connect db and select db name
    conn = MySQLdb.Connect(host=const.DBHOST,user=const.DBUSER,passwd=const.DBPWD,port=const.DBPORT,charset=const.DBCHARSET)
    cur = conn.cursor()
    conn.select_db(const.DBNAME)
    count = cur.execute('select sid,name,aname,toptag from song where scale = 0')
    results = cur.fetchall()
    index = 0
    for result in results:
      index += 1
      print '%d/%d' % (index,count)
      sid = result[0]
      sname = result[1]
      aname = result[2]
      toptag = result[3]
      sFile = open('../txt/%s_songs/%s' % (const.DATASET_NAME,sid),'w')
      tagDict = Lastfm_generateTagDictofSong(sname,aname,toptag)
      text =  Lastfm_generateDocofSong(sid,tagDict)
      sFile.write(text)
      sFile.close()
    conn.commit()
    cur.close()
    conn.close()
  except MySQLdb.Error,e:
    print 'Mysql Error %d:%s' % (e.args[0],e.args[1])
    logging.error('Mysql Error %d:%s' % (e.args[0],e.args[1]))

#add word to word dictionary
#tagDict:word dictionary of a song(word:count)
#tagStr:tag string
#tagCount:the count of tag's appearance
def Lastfm_addItemToDict(tagDict,tagStr,tagCount):
  #stemmer
  st = LancasterStemmer()
  #split tagStr
  for item in tagStr.split():
    item = item.lower()
    #stem
    item = st.stem(item)
    #remove stopwords and too short words
    if item not in stopwords:
      if item not in tagDict:
        tagDict[item] = tagCount
      else:
        tagDict[item] = tagDict[item] + tagCount

#generate tag dictionary of given song
def Lastfm_generateTagDictofSong(sname,aname,toptag):
  tagDict = {}
  #add sname to tagDict
  addItemToDict(tagDict,sname,100)
  #add aname to tagDict
  addItemToDict(tagDict,aname,100)
  #split tags<tag:count>
  tagInfos = eval(toptag)
  #loop every tag Information
  for tag in tagInfos.keys():
    tagCount = tagInfos[tag]
    #avoid some tags without count
    #if a tag has no count, ignore it
    if len(tagCount) == 0:
      continue
    else:
      #add tag to dict
      addItemToDict(tagDict,tag,int(tagCount))
  return tagDict

#generate document of given song from its tagDict
def Lastfm_generateDocofSong(sid,tagDict):
  result = []
  #repeat: write tag into file
  for tag in tagDict.keys():
    count = (int)(tagDict[tag] / 4)
    tag = "%s " % tag
    result.append(tag*count)
  return " ".join(result)

if __name__ == "__main__":
  Lastfm_generateDocs()

