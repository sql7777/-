# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 10:58:50 2018

@author: root
"""
import sys
import ctypes
from ctypes import *
import time

import redis

#import RFIDSYSSqliteClass

import socket
import json

import threading
# import psycopg2
import datetime
#import Com4GModularClass
from redisqueue import RedisQueue

#from bluetooth import *
from PInfluxdbClass import PInfluxdbClass
from DataObjectJSRedisClass import DataObjectJSRedisClass
from mqttsendclass import EMQSendClass

import threading


class SendDataToDestinationBLC(object):
    def __init__(self):
 
        self.usedtosendEPCQueue = RedisQueue(name='UsedEPCSendQueue',host='127.0.0.1',psw='123456',db=1)
        self.influxdbclass=PInfluxdbClass(host='127.0.0.1', port=8086, username='root', password='root', database = 'RFIDreportdb')

        self.tagstoRedis=DataObjectJSRedisClass(host='127.0.0.1',psw='123456',port=6379,indexkey='EPC')

        self.devID = b''

        self.thread_read_flg=False
        self.thread_read=None

        self.runallflg=False

        self.allthread=None

        self.clientID=""
        self.sendEmqClient=EMQSendClass(host='192.168.1.178',port=1883,username='admin',pwd='shuiJing1',client_id='')



    def GetRfidDevID(self):
        if self.devID == b'':
            try:
                conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
                if conn.ping():
                    print('conn ok')
                else:
                    print('shawanyi')
            except:  #
                return self.devID
            #conn.set('RFIDDevID', devID)
            if conn.exists('RFIDDevID'):
                pass
            else:
                print(self.devID)
                return self.devID
            ret=conn.get('RFIDDevID')
            if ret!=self.devID:
                self.devID=ret
                print('devID',self.devID)
        return self.devID

    def GetSysBluetoothCMD(self):
        cmd=0
        try:
            conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
        except:
            print('GetSysBluetoothCMD ERR')
            return 0
   
        ret=conn.get('RFIDSysBluetoothCMD')
        if ret==None:
            return 0
    
        if ret==b'START':
            cmd=1
        elif ret==b'STOP':
            cmd=2
        elif ret==b'POWERUP':
            cmd=3
        elif ret==b'POWERDOWN':
            cmd=4
        elif b'POWER:' in ret:
            p,var = ret.split(b':')
            cmd=int(var)
        else:
            cmd=0
        return cmd

    def SetSysBluetoothCMD(self,cmd=0):
        try:
            conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
        except:
            print('GetSysBluetoothCMD ERR')
            return False
        strcmd=''
        #ret=conn.get('RFIDSysBluetoothCMD')
        if cmd==1:#b'START':
            strcmd='START'
        elif cmd==2:#b'STOP':
            strcmd='STOP'
        elif cmd==3:#b'POWERUP':
            strcmd='POWERUP'
        elif cmd==4:#b'POWERDOWN':
            strcmd='POWERDOWN'
        elif cmd==5:
            strcmd='RUN'
        elif cmd>=10 and cmd<=30:
            strcmd='POWER:'+str(cmd)
        else:
            strcmd='START'

        conn.set('RFIDSysBluetoothCMD',strcmd)
        return True

    def RecvThreading(self,s):
        pass

    def StopRecvThread(self):
        self.thread_read_flg=False
        self.thread_read.join()
        self.thread_read=None
    
        self.SetSysBluetoothCMD(cmd=2)

    def StopAll(self):
        self.runallflg=False
        self.StopRecvThread()
        self.allthread=None

    def listtodict(self,data):
        d={}
        for v in data:
            key,value=v.split(':')
            d[key]=value
            #key,value=v.split(b':')
            #d[key.decode(encoding='utf-8')]=value.decode(encoding='utf-8')

        d['devID']=self.devID
        return d

        
    def UseReportdata(self,data):
        udict=self.MakeDataToDictMode(data)
        print(udict)
        if len(udict) <= 0:
            return False
#        self.influxdbclass.SaveDataToInfluxdb(measurement='RFIDreporttabl',tags={"NUMS":udict['NUMS']},fields=udict)
#        print('Get:',self.influxdbclass.GetDataFrominfluxdb(measurement='RFIDreporttabl'))

        for v in udict['tags']:
            ret = self.tagstoRedis.AddObject(data=v)
            print(ret)
            if ret[1]==1:
                print('GetObjectObjectlist:',self.tagstoRedis.GetObjectObjectlist())#获得对象hash name 列表
                print('GetObjectindexKeylist:',self.tagstoRedis.GetObjectindexKeylist())#获得索引键列表
                print('GetObjectKVlist:',self.tagstoRedis.GetObjectKVlist())#获得索引hash里 索引key+对象id列表
                #发送数据
                if self.clientID == "":
                    self.clientID=self.tagstoRedis.GetSelfUUID
                    print ('Get client uuid:',self.clientID)
                self.sendEmqClient.PublishOnceS(topic='RFIDEPCTAG',payload=str(v),qos=1,retain=False, will=None, auth={'username':'admin', 'password':'shuiJing1'}, tls=None)

            else:
                print('GetObjectContentByName:',self.tagstoRedis.GetObjectContentByName(name=ret[0]))

        nums=self.tagstoRedis.GetObjectSize()
        if nums>50:
            self.tagstoRedis.DeleteObjectAll()
            print('It s new day')

        return True
        
        
            
    def MakeDataToDictMode(self,data):
        retdict={}
        print(data)
        print(type(data))
        strdata=data.decode(encoding='utf-8')

        
        ldata=strdata.split(',')
        nums, value = ldata[2].split(':')

        
        #nums, value = data[2].split(b':')
        if 'NUMS' == nums:
            getnums = int(value, base=16)
            if getnums <= 0:
                print('UseReportdata is zero')
                return retdict
            retdict['NUMS']=getnums
            tags=[]
            epcdata=ldata[3:]
            el=len(epcdata)
            gl=int(el/getnums)
            for i in range(getnums):
                l=epcdata[i*gl:i*gl+gl]
                d=self.listtodict(l)
                tags.append(d)
                
            retdict['tags']=tags
        else:
            print('nothing to do')


        self.influxdbclass.SaveDataToInfluxdb(measurement='RFIDreporttabl',tags={"NUMS":retdict['NUMS']},fields={"reportRfid":strdata})
        #print('Get:',self.influxdbclass.GetDataFrominfluxdb(measurement='RFIDreporttabl'))
            
        return retdict

        
    def EPCSendRoServerForBluetooth(self):
   
        try:
            s_conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
            if s_conn.ping():
                print('EPCSendRoServerForBluetooth ok')
            else:
                print('shawanyi')
        except:  #
            print('EPCSendRoServerForBluetooth err')
            s_conn = None
            return False

        s_conn.set('RFIDSysIsStart','isok')
        self.SetSysBluetoothCMD(cmd=1)
        while self.devID==b'':
            retdevid=self.GetRfidDevID()
            time.sleep(2)

        while True:
            msg = self.usedtosendEPCQueue.get_nowait()
            #print('msg:',msg)
            if msg==None:
                continue

            self.UseReportdata(msg)

#        try:    
#            while True:
#                msg = self.usedtosendEPCQueue.get_nowait()
#                #print('msg:',msg)
#                if msg==None:
#                    continue

#                self.UseReportdata(msg)
#                #varepc = msg.split(b':')
#                #sdevs = b'DEVID:' + self.devID + b';' + varepc[1] + b'+'
#                #print('queueSend:',sdevs)
#                #sock.send(sdevs)

#        except:
#            print('Bluetooth sock err')

        self.StopRecvThread()
        #self.thread_read_flg=False
        #self.thread_read.join()
        #self.thread_read=None
    
        #self.SetSysBluetoothCMD(cmd=2)
        sock.close()

    def EPCSendRoServerForBluetoothRUN(self):
        if self.runallflg==True:
            self.StopAll()
        self.runallflg=True
        while self.runallflg:
            self.EPCSendRoServerForBluetooth()

    def RunAll_Bluetooth(self):
        if self.allthread!=None:
            return False
        self.allthread=threading.Thread(target=self.EPCSendRoServerForBluetoothRUN)
        self.allthread.setDaemon(True)
        self.allthread.start()
        return True





def RunMain():
    test=SendDataToDestinationBLC()
    test.EPCSendRoServerForBluetoothRUN()


if __name__ == '__main__':
    RunMain()
