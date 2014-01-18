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
import lastfm

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

#add word to word dictionary
#tagDict:word dictionary of a song(word:count)
#tagStr:tag string
#tagCount:the count of tag's appearance
def addItemToDict(tagDict,tagStr,tagCount):
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
def generateTagDictofSong(sname,aname,toptag):
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
      #print tag,tagCount
      addItemToDict(tagDict,tag,int(tagCount))
  return tagDict

#generate document of given song from its tagDict
def generateDocofSong(sid,tagDict):
  result = []
  #repeat: write tag into file
  for tag in tagDict.keys():
    count = (int)(tagDict[tag] / 4)
    tag = "%s " % tag
    result.append(tag*count)
  return " ".join(result)

def generateDocs(scale = 0):  
  try:
    #connect db and select db name
    conn = MySQLdb.Connect(host=const.DBHOST,user=const.DBUSER,passwd=const.DBPWD,port=const.DBPORT,charset=const.DBCHARSET)
    cur = conn.cursor()
    conn.select_db(const.DBNAME)
    #get all songs in playlist whose scale < 10
    print 'I am getting songs from playlist...'
    cur.execute('select playlist from user where scale < 10 and scale != -1')
    results = cur.fetchall()
    playlists = [result[0] for result in results]
    sids = []
    for playlist in playlists:
      items = playlist.split('==>')
      for item in items:
        value = item.split(':')
        sid = value[0]
        if sid not in sids:
          sids.append(sid)
    print '%d song are to be crawled...' % len(sids)
    print 'Begin to generate docs...'
    sFile = open('../txt/%s_song_Docs.txt' % const.DATASET_NAME,'w')
    dirname = '../txt/%s_songs' % const.DATASET_NAME
    rmDir(dirname)
    os.mkdir(dirname)

    size = len(sids)
    index = 0
    for songId in sids:
      index += 1
      print 'GenerateDocs:%d/%d' % (index,size)
      sql = "select sid,name,aname,toptag from song where sid = '%s'" % songId
      count = cur.execute(sql)
      result = cur.fetchone()
      sid = result[0]
      sname = result[1]
      aname = result[2]
      toptag = result[3]
      tagDict = generateTagDictofSong(sname,aname,toptag)
      text =  generateDocofSong(sid,tagDict)
      text = text.replace('\n',' ')
      sFile.write('%s>>%s\n' % (sid,text))
      filename = '%s/%s' % (dirname,sid)
      tmpFile = open(filename,'w')
      tmpFile.write(text)
      tmpFile.close()
    sFile.close()
    print 'Finish generating docs...'
    conn.commit()
    cur.close()
    conn.close()
  except MySQLdb.Error,e:
    print 'Mysql Error %d:%s' % (e.args[0],e.args[1])
    logging.error('Mysql Error %d:%s' % (e.args[0],e.args[1]))

if __name__ == "__main__":
  generateDocs()
