# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 21:58:41 2018

@author: root
"""

import mqttrevclass
import time
import redis
import threading

class EMQRevToredisQueueClass(object):
    def __init__(self,emqsetinfo={'host':'192.168.1.112','port':1883,'username':'admin','pwd':'shuiJing1','client_id':'','topic':[('test',1)]},
                 redissetinfo={'host':'127.0.0.1','port':6379,'pwd':'123456','db':0}):
        self.emqhost=emqsetinfo['host']
        self.emqport=emqsetinfo['port']
        self.emqusrname=emqsetinfo['username']
        self.emqpwd=emqsetinfo['pwd']
        self.emqclient_id=emqsetinfo['client_id']
        self.topic=emqsetinfo['topic']

        self.redishost=redissetinfo['host']
        self.redisport=redissetinfo['port']
        self.redispwd=redissetinfo['pwd']
        self.redisdb=redissetinfo['db']

        self.thread_read=None
        self.isredistrue=False
        #self.__connredis=None
        self.__emq=mqttrevclass.EMQRevClass(host=self.emqhost,port=self.emqport,username=self.emqusrname,pwd=self.emqpwd,
                                            client_id=self.emqclient_id,callbackMessage=self.puttorediscallbacke,callbackEvent=None)

        try:
            self.__connredis = redis.Redis(host=self.redishost,password=self.redispwd,port=self.redisport,db=self.redisdb)
            if self.__connredis.ping():
                print('conn ok')
                self.isredistrue=True
            else:
                print('shawanyi')
        except :#redis.exceptions.ResponseError:#redis.ConnectionError:
            print('Error conn')
            self.isredistrue=False
            return None
    
    def putdatatoredisqueue(self,key,item):
        if self.isredistrue==False:
            return False
        #if  self.__connredis==None:
            #if self.connectRedis()==False:
                #print('conn put err')
                #return False
        try:
            if self.__connredis.ping():
                pass
        except :
            print('except')
            return False
        print('key:',key)
        print('item:',item)
        print(self.__connredis.rpush(key, item))  # 添加新元素到队列最右方
        return True

    def puttorediscallbacke(self,data):
        if isinstance(data,dict):
            pass
        else:
            return False
        try:
            key=data['topic']
            item=data['payload']
            #print('put:{0}',data)
            ret=self.putdatatoredisqueue(key,item)
            return ret
            #return self.putdatatoredisqueue(key,item)
        except :
            return False

    def StartToRun(self):
        #if self.connectRedis()==False:
        if self.isredistrue==False:
            return False
        self.__emq.AddTopic(self.topic)
        if self.thread_read!=None:
            self.__emq.Close()
            self.thread_read.join()
            self.thread_read=None
        self.thread_read=threading.Thread(target=self.__emq.client_loop)
        self.thread_read.setDaemon(True)
        self.thread_read.start()
        return True

    def StopRun(self):
        if self.thread_read!=None:
            self.__emq.Close()
            self.thread_read.join()
            self.thread_read=None
           
if __name__ == '__main__':
    emqsetinfo={'host':'192.168.1.112','port':1883,'username':'admin','pwd':'shuiJing1','client_id':'1234567890','topic':[('test1',1),('test rev',1)]}
    redissetinfo={'host':'127.0.0.1','port':6379,'pwd':'123456','db':0}
    tc=EMQRevToredisQueueClass(emqsetinfo=emqsetinfo,redissetinfo=redissetinfo)
    if tc.StartToRun()==True:
        while 1:
            q=input('input q to exit:')
            if q=='q':
                tc.StopRun()
                break
