#!/usr/bin python
#coding=utf-8
############################
# @author Jason Wong
# @date 2013-12-08
############################
# connect to aotm db
# get useful playlists and songs
# generate documents of songs
############################

import MySQLdb
import sys

# reload sys and set encoding to utf-8
reload(sys)
sys.setdefaultencoding('utf-8')

# define some global varibale
DBHOST = 'localhost'
DBUSER = 'root'
DBPWD = 'wst'
DBPORT = 3306
DBNAME = 'aotm'
DBCHARSET = 'utf8'

# get effective_playlists which part < 3
# @return: two dictionaries
# the first dict contains songs in selected playlists,that is, the keys of the dict are effective_songs' ids and values are appearance count numbers of these songs in selected playlists
# the second dict stands for length of each playlist like <pid:count>
def genEffectivePlaylist():
  #init the dicts to be returned
  songDict = {}
  playlistDict = {}
  #include global varibles
  global DBHOST
  global DBUSER
  global DBPWD
  global DBPORT
  global DBNAME
  global DBCHARSET
  
  try:
    #connect to db
    conn = MySQLdb.Connect(host=DBHOST,user=DBUSER,passwd=DBPWD,port=DBPORT,charset=DBCHARSET)
    #get the cursor of db
    cur = conn.cursor()
    #select db
    conn.select_db(DBNAME)
    #select effective playlists
    count = cur.execute('select id,count,songs from effective_playlists where part != -1 and part < 3')
    print 'there are %d playlists selected' % count
    if count == 0:
      print 'No effective playlists selected......'
      return
    else:
      results = cur.fetchall()
      for result in results:
        pid = int(result[0])
        length = int(result[1])
        playlistDict[pid] = length
        songs = result[2]
        songItems = songs.split('==>')
        for song in songItems:
          sid = int(song)
          if sid not in songDict:
            songDict[sid] = 1
          else:
            old = songDict[sid]
            new = old + 1
            songDict[sid] = new
    print 'There are %d songs in %d playlists' % (len(songDict),len(playlistDict))
    return songDict,playlistDict       
  except MySQLdb.Error,e:
    print 'Mysql Error %d:%s' % (e.args[0],e.args[1])

if __name__ == '__main__':
  genEffectivePlaylist()
  

