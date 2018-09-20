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


usedtosendEPCQueue = RedisQueue(name='UsedEPCSendQueue',host='127.0.0.1',psw='123456',db=1)

devID = b''


def GetRfidDevID():
    global devID
    if devID == b'':
        try:
            conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
            if conn.ping():
                print('conn ok')
            else:
                print('shawanyi')
        except:  #
            return devID
        #conn.set('RFIDDevID', devID)
        if conn.exists('RFIDDevID'):
            pass
        else:
            print(devID)
            return devID
        ret=conn.get('RFIDDevID')
        if ret!=devID:
            devID=ret
            print('devID',devID)
    return devID

def GetSysBluetoothCMD():
    cmd=0
    try:
        conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
    except:
        print('GetSysBluetoothCMD ERR')
        return 0
   
    ret=conn.get('RFIDSysBluetoothCMD')
    if ret==b'START':
        cmd=1
    elif ret==b'STOP':
        cmd=2
    elif ret==b'POWERUP':
        cmd=3
    elif ret==b'POWERDOWN':
        cmd=4
    else:
        cmd=0
    return cmd

def SetSysBluetoothCMD(cmd=0):
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
    else:
        strcmd='START'

    conn.set('RFIDSysBluetoothCMD',strcmd)
    return True


def EPCSendRoServerForBluetooth():
    global devID
    global usedtosendEPCQueue
    print('EPCSendRoServerForBluetooth')
    server_sock=BluetoothSocket( RFCOMM )
    server_sock.bind(("",PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]

    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

    advertise_service( server_sock, "SampleServer",
                       service_id = uuid,
                       service_classes = [ uuid, SERIAL_PORT_CLASS ],
                       profiles = [ SERIAL_PORT_PROFILE ], 
#                       protocols = [ OBEX_UUID ] 
                        )
                   
    print("Waiting for connection on RFCOMM channel %d" % port)

    client_sock, client_info = server_sock.accept()
    print("Accepted connection from ", client_info)

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
    SetSysBluetoothCMD(cmd=1)
    while devID==b'':
        retdevid=GetRfidDevID()
        time.sleep(2)
        

    try:
        while True:
            msg = usedtosendEPCQueue.get_nowait()
            print('msg:',msg)
            if msg!=None:
                pass
            else:
                time.sleep(1)
                continue
        
            varepc = msg.split(b':')
            sdevs = b'DEVID:' + devID + b';' + varepc[1] + b'+'
            print('queueSend:',sdevs)
            client_sock.send(sdevs)

            data = client_sock.recv(1024)
            if len(data) == 0: break
            print("received [%s]" % data)
            if b'START' in data:
                SetSysBluetoothCMD(cmd=1)
            elif b'STOP'in data:
                SetSysBluetoothCMD(cmd=2)
            elif b'POWERUP' in data:
                SetSysBluetoothCMD(cmd=3)
            elif b'POWERDOWN' in data:
                SetSysBluetoothCMD(cmd=4)
            else:
                pass
            
    except IOError:
        pass

    print("disconnected")

    SetSysBluetoothCMD(cmd=2)

    client_sock.close()
    server_sock.close()
    print("all done")
    





def RunMain():
    while True:
        EPCSendRoServerForBluetooth()


if __name__ == '__main__':
    RunMain()
