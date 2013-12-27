#!/usr/bin python
#-coding:utf-8-------
#############################
#some methods to crawl data from lastfm
#############################

import urllib
import json
import os
import time

#define function to crawl friends of user with specific username from lastfm
def crawlInfoOfUser(username,infoType = 0,page = 1):
  if infoType == 0:
    #get friends
    url = 'http://ws.audioscrobbler.com/2.0/?method=user.getfriends&user=%s&api_key=550633c179112c8002bc6a0942d55b2a&format=json&page=%d' % (username,page)
  elif infoType == 1:
    #get recent tracks
    url = 'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=550633c179112c8002bc6a0942d55b2a&format=json&page=%d' % (username,page)
  #url = url.replace('&','%26')
  #url = url.replace('+','%2b')
  page = urllib.urlopen(url)
  data = page.read()
  ddata = json.loads(data)
  return ddata

def crawlUsersFromLastfm():
  filename = "../txt/users.txt"
  if os.path.exists(filename):
    print '%s is existing......'
    return
  uFile = open(filename,'w')
  allUserName = []
  allUserId = []
  index = -1
  while len(allUserId) < 10000:
    if index == -1:
      username = 'rj'
    else:
      username = allUserName[index]
    print 'curUser = %s' % username
    try:
      friendDict = crawlInfoOfUser(username,0)
      users = friendDict['friends']['user']
      count = len(users)
      for i in range(count):
        uid = users[i]['id']
        name = users[i]['name']
        country = users[i]['country']
        if country == '':
          country = 'n'
        age = users[i]['age']
        if age == '':
          age = 0  
        gender = users[i]['gender']
        if gender == '':
          gender = 'n'
        registeredText = users[i]['registered']['#text']
        if registeredText == '':
          registeredText = time.ctime()
        registeredTime = users[i]['registered']['unixtime']
        if registeredTime == '':
          registeredTime = time.time()
        if not uid in allUserId:
          info = '%s+%s+%s+%s+%s+%s+%s\n' % (uid,name,country,age,gender,registeredTime,registeredText)
          uFile.write(info)
          allUserId.append(uid)
          allUserName.append(name)
    except:
      print '%s causes exception......' % username
    print '%d loop has %d users......' % (index,len(allUserId))
    index += 1
  uFile.close()

#get all users from file named user.txt in txt folder
def getAllUserFromFile():
  filename = "../txt/users.txt"
  if not os.path.exists(filename):
    crawlUsersFromLastfm()
  allUserId = []
  allUserName = []
  uFile = open(filename,'r')
  lines = uFile.readlines()
  for line in lines:
    items = line.rstrip('\n').split('+')
    allUserId.append(items[0])
    allUserName.append(items[1])
  print 'There are %d users...' % len(allUserId)
  uFile.close()
  return allUserId,allUserName
  
def crawlRecentTracksFromLastfm():
  filename = "../txt/tracks.txt"
  if os.path.exists(filename):
    print '%s is existing......'
    return
  sFile = open(filename,'w')
  allUserId,allUserName = getAllUserFromFile()
  userCount = len(allUserId)
  for index in range(userCount):
    user = allUserName[index]
    uid = allUserId[index]
    for page in range(1,4,1):
      try:
        print '%d/%d >>> %d/4' % (index,userCount,page)
        trackDict = crawlInfoOfUser(user,1,page)
        tracks = trackDict['recenttracks']['track']
        count = len(tracks)
        for i in range(count):
          mbid = tracks[i]['mbid']
          uts = tracks[i]['date']['uts']
          dateText = tracks[i]['date']['#text']
          info = '%s+%s+%s+%s\n' % (uid,mbid,uts,dateText)
          sFile.write(info)
        attr = trackDict['recenttracks']['@attr']
        totalPages = int(attr['totalPages'])
        if totalPages < (page+1):
          break
      except:
        print '%s(%d/%d) causes exception in page %d......' % (user,index,userCount,page)
        continue
  sFile.close()

def getAllSongFromFile():
  filename = "../txt/tracks.txt"
  if not os.path.exists(filename):
    crawlRecentTracksFromLastfm()
  sFile = open(filename,'r')
  allSid = []
  lines = sFile.readlines()
  for line in lines:
    items = line.rstrip('\n').split('+')
    mbid = items[1]
    if not mbid in allSid:
      allSid.append(mbid)
  print 'There are %d unique songs...' % len(allSid)
  sFile.close()
def crawlSongInfoFromLastfm():

if __name__ == "__main__":
  crawlRecentTracksFromLastfm()
      
