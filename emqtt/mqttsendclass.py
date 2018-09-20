# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 21:58:41 2018

@author: root
"""

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publishOnce
import time

class EMQSendClass(object):
    def __init__(self,host='192.168.1.112',port=1883,username='admin',pwd='shuiJing1',client_id=''):
        self.host=host
        self.port=port
        self.usrname=username
        self.pwd=pwd
        self.client_id=client_id
        self.client=None

        self.isconnect=False
        

    def Connect(self):
        if self.client_id=="":
            self.client_id = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        if self.client==None:
            self.client = mqtt.Client(self.client_id,clean_session=True, userdata=None)
        try:
            self.client.connect(self.host, self.port, 60)
        except:
            return False
        self.client.loop_start()
        self.isconnect=True
        return True

    def ReConnect(self):
        if self.isconnect:
            self.Close()
            self.Connect()

    def Close(self):
        if self.isconnect:
            self.client.disconnect()
            self.client.loop_stop()
            self.isconnect=False
            self.client=None

    def Publish(self,topic,payload=None,qos=0,retain=False):
        if self.isconnect==True and self.client!=None:
            return self.client.publish(topic=topic,payload=payload,qos=qos,retain=retain)

    def PublishOnceS(self,topic='', payload=None, qos=0, retain=False, hostname='',port=0, client_id="", keepalive=60, will=None, auth=None, tls=None):
        uhostname=hostname
        if uhostname=='':
            uhostname=self.host
        uclientid=client_id
        if uclientid=="":
            uclientid = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        uauth=auth
        if uauth==None:
            uauth={'username':self.usrname, 'password':self.pwd}
        uport=port
        if uport==0:
            uport=self.port
        return publishOnce.single(topic=topic,payload=payload,qos=qos,retain=retain,hostname=uhostname,port=uport,client_id=uclientid,keepalive=keepalive,will=will,auth=uauth,tls=tls)

    def PublishOnceM(self,msgs='', hostname="", port=0, client_id="", keepalive=60, will=None, auth=None, tls=None):
        uhostname=hostname
        if uhostname=='':
            uhostname=self.host
        uclientid=client_id
        if uclientid=="":
            uclientid = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        uauth=auth
        if uauth==None:
            uauth={'username':self.usrname, 'password':self.pwd}
        uport=port
        if uport==0:
            uport=self.port
        return publishOnce.multiple(msgs=msgs,hostname=uhostname,port=uport,client_id=uclientid,keepalive=keepalive,will=will,auth=uauth,tls=tls)

if __name__ == '__main__':
    t=EMQSendClass(host='192.168.1.112',port=1883,username='admin',pwd='shuiJing1',client_id='')
    t.PublishOnceS(topic='test rev',payload='send test',qos=1,retain=False, hostname='192.168.1.112',port=1883, client_id="123456", keepalive=60, will=None, auth={'username':'admin', 'password':'shuiJing1'}, tls=None)
    for i in range(10):
        sendstr='send times:'+str(i)
        t.PublishOnceS(topic='test1',payload=sendstr,qos=1,retain=False, hostname='192.168.1.112',port=1883, client_id="123456", keepalive=60, will=None, auth={'username':'admin', 'password':'shuiJing1'}, tls=None)
