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
import Com4GModularClass
from redisqueue import RedisQueue

sysdict = {'ts': 1, 'ss': 30, 'a1': 1, 'a2': 0, 'a3': 0, 'a4': 0, 'aw': 3000, 'sip1': '58.214.232.163', 'sip2': '',
           'sip3': '', 'sip4': ''}
#sysopdict={"networkdevice":"ETH"}
sysopdict={"uploaddevice":"ETH","uploadmethod":"TCP","database":"materiel","user":"pms","password":"pms@pg123","host":"58.214.232.165","port":"5432"}

usedtosendEPCQueue = RedisQueue(name='UsedEPCSendQueue',host='127.0.0.1',psw='123456',db=1)

devID = b''

def SYSIniforSqlite():
    global sysopdict

    rt = RFIDSYSSqliteClass.RfidSysSqlite3Class(db='../pythonconfig/sql.db')
    ret = rt.Sqlite3Getsyssetdataforweb()
    print('sqlit')
    print(ret)
    if ret == None:
        return

    dictt = json.loads(ret[0][1])
    app = dictt['app']
    sysopdict = dictt['db']
    print(sysopdict)
    if isinstance(app['ts'], int):
        pass
    else:
        app['ts'] = int(app['ts'])
    if isinstance(app['ss'], int):
        pass
    else:
        app['ss'] = int(app['ss'])
    if isinstance(app['a1'], int):
        pass
    else:
        app['a1'] = int(app['a1'])
    if isinstance(app['a2'], int):
        pass
    else:
        app['a2'] = int(app['a2'])
    if isinstance(app['a3'], int):
        pass
    else:
        app['a3'] = int(app['a3'])
    if isinstance(app['a4'], int):
        pass
    else:
        app['a4'] = int(app['a4'])
    if isinstance(app['aw'], int):
        pass
    else:
        app['aw'] = int(app['aw'])
    rt.Sqlte3Closs()
    return app
def SysIniDict():
    global sysdict
    dictt = SYSIniforSqlite()
    print ('ini')
    if dictt != None:
        sysdict = dictt
        print(sysdict)
    else:
        pass
    print(sysdict['sip1'])
    print(sysopdict['uploaddevice'])

    try:
        conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=0)
#        conn.mset(sysdict)
    except:
        return False
    return True

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
        ret=conn.get('RFIDDevID')
        if ret!=devID:
            if ret==None:
                return b''
            devID=ret
    return devID

def EPCSendToServerThreadsockt1():
    times=0
    s_conn = None
    usedkey = ''
    print('EPCSendToServerThreadsockt')
    try:
        s_conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
        if s_conn.ping():
            print('EPCSendToServerThreadsockt ok')
        else:
            print('shawanyi')
    except:  #
        print('EPCSendToServerThreadsockt err')
        s_conn = None
        return False
    while devID==b'':
        retdevid=GetRfidDevID()
        time.sleep(2)

    print('----------------------------------------------------------------------------')
    while 1:
        # InsertToPostgresql(devID,epc)
        if s_conn == None:
            try:
                s_conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
                if s_conn.ping():
                    print('EPCSendToServerThreadsockt ok')
                else:
                    print('shawanyi')
                s_conn = None
                time.sleep(1)
                continue
            except:  #
                print('EPCSendToServerThreadsockt err')
                s_conn = None
                time.sleep(1)
                continue
        else:
            if usedkey == '':
                usedkey = s_conn.lpop('EPCDatasqueuekey')
                if usedkey == None:
                    time.sleep(2)
                    continue
            if s_conn.exists(usedkey):
                try:
                    ser = socket.socket()
                    ser.settimeout(5)
                    ser.connect((sysdict['sip1'], 9999))  # 12348
                    ser.settimeout(None)
                    epc = s_conn.zrange(usedkey, 0, -1)
                    print ('to postgresql')

                    #EPCAddToShowredisqueue(epc=epc,times=times)
                    if times==0:
                        times=1
                    else:
                        times=0
                    for var in epc:
                        varepc=var.split(b':')
                        sdevs = b'DEVID:' + devID + b';' + varepc[1] + b'+'

                        ser.sendall(sdevs)#ser.sendall(var + b';')
                        backe_msg=ser.recv(1024)
                    ser.close()
                    s_conn.delete(usedkey)
                    usedkey=''
                    time.sleep(1)
                except:
                    is4grun=0
                    print ('socket conn err')
                    #time.sleep(1)
                    continue
            else:
                usedkey=''
                continue
        time.sleep(2)

def EPCSendToServerThreadsockt():
    global devID
    times=0
    s_conn = None
    usedkey = ''
    epc=[]
    print('EPCSendToServerThreadsockt')
    try:
        s_conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
        if s_conn.ping():
            print('EPCSendToServerThreadsockt ok')
        else:
            print('shawanyi')
    except:  #
        print('EPCSendToServerThreadsockt err')
        s_conn = None
        return False
    time.sleep(3)
    while devID==b'':
        retdevid=GetRfidDevID()
        time.sleep(2)
    print(devID)

    print('----------------------------------------------------------------------------')
    while 1:
        # InsertToPostgresql(devID,epc)
        if s_conn == None:
            try:
                s_conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
                if s_conn.ping():
                    print('EPCSendToServerThreadsockt ok')
                else:
                    print('shawanyi')
                s_conn = None
                time.sleep(1)
                continue
            except:  #
                print('EPCSendToServerThreadsockt err')
                s_conn = None
                time.sleep(1)
                continue
        else:
            if usedkey == '':
                usedkey = s_conn.lpop('EPCDatasqueuekey')
                if usedkey == None:
                    time.sleep(2)
                    continue
            if s_conn.exists(usedkey):
                epcconn = s_conn.zrange(usedkey, 0, -1)
                for epcvar in epcconn:
                    epc.append(epcvar)
                s_conn.delete(usedkey)
                usedkey=''
                try:
                    ser = socket.socket()
                    ser.settimeout(5)
                    ser.connect((sysdict['sip1'], 9999))  # 12348
                    ser.settimeout(None)
                    #epc = s_conn.zrange(usedkey, 0, -1)
                    print ('to postgresql')

                    #EPCAddToShowredisqueue(epc=epc,times=times)
                    #if times==0:
                    #    times=1
                    #else:
                    #    times=0
                    for var in epc:
                        varepc=var.split(b':')
                        print (varepc)
                        print(devID)
#print('devID' devID)
                        sdevs = b'DEVID:' + devID + b';' + varepc[1] + b'+'

                        print(sdevs)
                        ser.sendall(sdevs)#ser.sendall(var + b';')
                        backe_msg=ser.recv(1024)
                    ser.sendall(b'Finish')
                    print('Finish')
                    time.sleep(1)
                    ser.close()
                    #s_conn.delete(usedkey)
                    #usedkey=''
                    epc.clear()
                    time.sleep(1)
                except:
                    is4grun=0
                    ser.close()
                    time.sleep(2)
                    print ('socket conn err')
                    #time.sleep(1)
                    continue
            else:
                usedkey=''
                continue
        time.sleep(2)
def EPCSendToServerFor4G():
    global devID
    print('EPCSendToServerFor4G')
    print(sysdict['sip1'])
    usedkey=''
    epc=[]
#    rt4g = Com4GModularClass.Com4GModularClass(Port='/dev/ttyAMA4', protocol='TCP', address='47.95.112.32',  netport=9999)
    rt4g = Com4GModularClass.Com4GModularClass(Port='/dev/ttyAMA4', protocol='TCP', address=sysdict['sip1'],  netport=9999)
    ret=rt4g.Get4GmodeStartFlgfortime(timeout=500)
    print (ret) #if 'OK' in ret:
    ret=rt4g.SysSet4Ginit(mode=1, protocol='TCP', address=sysdict['sip1'], port=9999)
    print(ret)
    if 'OK' in ret:
        pass
    else:
        while 1:
            time.sleep(2)
            ret = rt4g.SysSet4Ginit(mode=1, protocol='TCP', address=sysdict['sip1'], port=9999)
            print(ret)
            if 'OK' in ret:
                break
    ret=rt4g.GetSys4GLinkStateA(mode=1)
    print(ret)
    if 'OK' in ret:
        pass
    else:
        while 1:
            time.sleep(2)
            ret = rt4g.GetSys4GLinkStateA(mode=1)
            print(ret)
            if 'OK' in ret:
                break
    print('4G connect-----------------------')
    try:
        s_conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
        if s_conn.ping():
            print('EPCSendToServerThreadsockt ok')
        else:
            print('shawanyi')
    except:  #
        print('EPCSendToServerThreadsockt err')
        s_conn = None
        return False
    
    s_conn.set('RFIDSysIsStart','isok')
    
    while devID==b'':
        retdevid=GetRfidDevID()
        time.sleep(2)

    print('Start Get EPC to Send ---------------')
    while 1:
        # InsertToPostgresql(devID,epc)
        if s_conn == None:
            try:
                s_conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
                if s_conn.ping():
                    print('EPCSendToServerThreadsockt ok')
                else:
                    print('shawanyi')
                s_conn = None
                time.sleep(1)
                continue
            except:  #
                print('EPCSendToServerThreadsockt err')
                s_conn = None
                time.sleep(1)
                continue
        else:
            try:
                if usedkey == '':
                    usedkey = s_conn.lpop('EPCDatasqueuekey')
                    if usedkey == None:
                        time.sleep(2)
                        continue
            except:
                print('get EPCDatasqueuekey err')
                time.sleep(1)
                continue
            try:
                if s_conn.exists(usedkey):
                    epcconn = s_conn.zrange(usedkey, 0, -1)
                    for epcvar in epcconn:
                        epc.append(epcvar)
                    s_conn.delete(usedkey)
                    usedkey=''

                    for var in epc:
                        varepc = var.split(b':')
                        sdevs = b'DEVID:' + devID + b';' + varepc[1] + b'+'
                        print('sdevs',sdevs)

                        backe_msg = rt4g.SenddatafromSockArev(mode=1, revs=50, sddata=sdevs)
                        print('RECVdata:{0}',backe_msg)
                        while backe_msg==b'':
                            time.sleep(2)
                            backe_msg = rt4g.SenddatafromSockArev(mode=1, revs=50, sddata=sdevs)
                            print('RECVdata:{0}', backe_msg)
                    backe_msg = rt4g.SenddatafromSockArev(mode=1, revs=50, sddata=b'Finish')
                    print ('Send End : {0]',backe_msg)


#                s_conn.delete(usedkey)
#                usedkey=''
                    epc.clear()
                    time.sleep(1)
                else:
                    usedkey=''
                    time.sleep(1)
                    continue
            except:
                print('4G senddata err ------')
        time.sleep(2)
def EPCSendToServerFor4GQueue():
    global devID
    global usedtosendEPCQueue
    print('EPCSendToServerFor4G')
    print(sysdict['sip1'])
    usedkey=''
    epc=[]
#    rt4g = Com4GModularClass.Com4GModularClass(Port='/dev/ttyAMA4', protocol='TCP', address='47.95.112.32',  netport=9999)
    rt4g = Com4GModularClass.Com4GModularClass(Port='/dev/ttyAMA4', protocol='TCP', address=sysdict['sip1'],  netport=9999)
    ret=rt4g.Get4GmodeStartFlgfortime(timeout=500)
    print (ret) #if 'OK' in ret:
    ret=rt4g.SysSet4Ginit(mode=1, protocol='TCP', address=sysdict['sip1'], port=9999)
    print(ret)
    if 'OK' in ret:
        pass
    else:
        while 1:
            time.sleep(2)
            ret = rt4g.SysSet4Ginit(mode=1, protocol='TCP', address=sysdict['sip1'], port=9999)
            print(ret)
            if 'OK' in ret:
                break
    ret=rt4g.GetSys4GLinkStateA(mode=1)
    print(ret)
    if 'OK' in ret:
        pass
    else:
        while 1:
            time.sleep(2)
            ret = rt4g.GetSys4GLinkStateA(mode=1)
            print(ret)
            if 'OK' in ret:
                break
    print('4G connect-----------------------')
    try:
        s_conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
        if s_conn.ping():
            print('EPCSendToServerThreadsockt ok')
        else:
            print('shawanyi')
    except:  #
        print('EPCSendToServerThreadsockt err')
        s_conn = None
        return False
    
    s_conn.set('RFIDSysIsStart','isok')
    
    while devID==b'':
        retdevid=GetRfidDevID()
        time.sleep(2)

    print('Start Get EPC to Send ---------------')
    while 1:
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
        backe_msg = rt4g.SenddatafromSockArev(mode=1, revs=50, sddata=sdevs)
        print('RECVdata:{0}',backe_msg)
        while backe_msg==b'':
            time.sleep(2)
            backe_msg = rt4g.SenddatafromSockArev(mode=1, revs=50, sddata=sdevs)
            print('RECVdata:{0}', backe_msg)
        backe_msg = rt4g.SenddatafromSockArev(mode=1, revs=50, sddata=b'Finish')
        print ('Send End : {0]',backe_msg)




def RunMain():
    if not SysIniDict():  # if not SysIni():
        print('SysIni Erro')
        return

    if sysopdict["uploaddevice"] == "4G":
        #EPCSendToServerFor4G()
        EPCSendToServerFor4GQueue()
        #thread_sendepc = threading.Thread(target=EPCSendToServerThread, name='EPCSendToServerThreadsockt')
    else:
        EPCSendToServerThreadsockt()
        #thread_sendepc = threading.Thread(target=EPCSendToServerThreadsockt, name='EPCSendToServerThread')
#    rt4g = Com4GModularClass.Com4GModularClass(Port='/dev/ttyAMA4', protocol='TCP', address='47.95.112.32',  netport=9999)


if __name__ == '__main__':
    RunMain()
