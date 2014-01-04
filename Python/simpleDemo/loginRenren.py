#coding:utf8   
''''' 
模拟登陆人人 根据网上的资料和firefox做了下  
首先自己去探查了下 
页面元素： 
<input id="email" class="input-text" type="text" value="" tabindex="1" name="email" style="color: rgb(136, 136, 136);"></input 
<input id="password" class="input-text" type="password" autocomplete="off" tabindex="2" error="请输入密码" name="password"></input> 
     
cookie： 
jebecookies=523a9b12-658f-43c0-abf8-1ca1f3f87c10|||||; domain=.renren.com; path=/ 
     
'''  
import re,urllib,urllib2,cookielib,codecs,chardet,sys   
      
class LoginRenRen():  
          
  def __init__(self,name='',password='',domain=''):  
    self.name=name  
    self.password=password  
    self.domain=domain  
              
    self.cj = cookielib.LWPCookieJar()  
    try:  
      #自动去远程获取一个cookie  
      #self.cj.revert('renren.coockie')  #测试的时候每次都有异常但是毫无影响，注释掉了也不影响  
      print 'successed got a cookie..'  
    except Exception,e:  
      print 'Can not get the cookies',e.message  
              
    #装载cookies    
    self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))  
    urllib2.install_opener(self.opener)  
              
  def login(self):  
    params = {'domain':self.domain,'email':self.name,'password':self.password}  
    req = urllib2.Request(  'http://www.renren.com/PLogin.do',  urllib.urlencode(params))  
    print 'login.....'  
              
    self.openrate = self.opener.open(req)  
              
    #查看下返回的url来判断登陆进去了没  
    print self.openrate.geturl()  
    info = self.openrate.read()  
              
    #查看了一下页面编码 chardet是第三方库  
    print chardet.detect(info)  
    print ''          
    print re.findall(r'password',info)  
    #打印出了返回的内容  
    type = sys.getfilesystemencoding()     
    print info.decode("UTF-8").encode(type)   
              
                  
if __name__=='__main__':  
  username = 'wwssttt@163.com' #用户名  
  password = 'wst19871205' #密码  
  domain = 'renren.com'  
  ren = LoginRenRen(username,password,domain)  
  ren.login()  
