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

import RFIDSYSSqliteClass

import socket
import json

import threading
# import psycopg2
import datetime
#import Com4GModularClass
from redisqueue import RedisQueue

from bluetooth import *
import threading


class SendDataToDestinationBLC(object):
    def __init__(self, bluetuuid="94f39d29-7d6d-437d-973b-fba39e49d4ee"):
 
        self.usedtosendEPCQueue = RedisQueue(name='UsedEPCSendQueue',host='127.0.0.1',psw='123456',db=1)

        self.devID = b''
        self.uuid=bluetuuid

        self.thread_read_flg=False
        self.thread_read=None

        self.runallflg=False

        self.allthread=None



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
        #global thread_read_flg
        while self.thread_read_flg:
            data = s.recv(1024)
            if len(data) == 0:
                continue#break
            print("received [%s]" % data)
            if b'START' in data:
                self.SetSysBluetoothCMD(cmd=1)
            elif b'STOP'in data:
                self.SetSysBluetoothCMD(cmd=2)
            elif b'POWERUP' in data:
                self.SetSysBluetoothCMD(cmd=3)
            elif b'POWERDOWN' in data:
                self.SetSysBluetoothCMD(cmd=4)
            elif b'POWER:' in data:
                p,var = data.split(b':')
                self.SetSysBluetoothCMD(cmd=int(var))
            else:
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
        
    def EPCSendRoServerForBluetooth(self):
        #global devID
        #global usedtosendEPCQueue
        #global thread_read_flg
        #global thread_read
        print('EPCSendRoServerForBluetooth')

        #uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
        uuid = self.uuid

        try:
            service_matches = find_service( uuid = uuid, address = None )

            if len(service_matches) == 0:
                print("couldn't find the SampleServer service =(")
                return

            first_match = service_matches[0]
            port = first_match["port"]
            name = first_match["name"]
            host = first_match["host"]

            print("connecting to \"%s\" on %s" % (name, host))

            # Create the client socket
            sock=BluetoothSocket( RFCOMM )
            sock.connect((host, port))

            self.thread_read_flg=True
            self.thread_read=threading.Thread(target=self.RecvThreading,args=(sock,))
            self.thread_read.setDaemon(True)
            self.thread_read.start()

            print("connected.  type stuff")
        except:
            print("Bluetooth connect err")
            return
    
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

        try:    
            while True:
                msg = self.usedtosendEPCQueue.get_nowait()
                #print('msg:',msg)
                if msg==None:
                    continue
        
                varepc = msg.split(b':')
                sdevs = b'DEVID:' + self.devID + b';' + varepc[1] + b'+'
                print('queueSend:',sdevs)
                sock.send(sdevs)

        except:
            print('Bluetooth sock err')

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
