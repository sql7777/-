# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 10:58:50 2018

@author: root
"""
import sys
import ctypes
from ctypes import *
import time

import EmbeddedCom
import RfidCommandAnalysis

from PrintLoggerClass import Logger
# from  RedisMessagesHelper import RedisMessagesHelper
from redisqueue import RedisQueue
import redis

import RFIDSYSSqliteClass

import socket
import json

import threading
# import psycopg2
import datetime
import Com4GModularClass

sysdict = {'ts': 1, 'ss': 30, 'a1': 1, 'a2': 0, 'a3': 0, 'a4': 0, 'aw': 3000, 'sip1': '58.214.232.163', 'sip2': '',
           'sip3': '', 'sip4': ''}
sysopdict={"networkdevice":"ETH"}
pool = None
redisconnpool = None
loggererro = Logger(logname='logerro.txt', loglevel=1, logger='RfidReadAndWrite.py').getlog()
logger = Logger(logname='log.txt', loglevel=1, logger="RfidReadAndWrite.py").getlog()
# syskey=b''
# sysstatus=b''
usedAnt = 1
usedPower = 1024
EPCProsseRedisflg = 0
GetTagProsseFlg = 0

epcsendthreadalive = 0

isusesubcommand = 1
issysset = 0
rfidcallbackdata = b''
devID = b''
rfidcallbackProssdata = b''
RfidCMD = RfidCommandAnalysis.RfidCMDAnalysis()

usedtoshowtims=0

def WriteToJsonFile(fpath, fdict):
    try:
        with open(fpath, 'w') as f:
            json.dump(fdict, f)
            return 'OK'
    except:
        return None


def ReadFromJsonFile(fpath):
    try:
        with open(fpath, 'r') as f:
            data = json.load(f)
            print(data)
        return data
    except:
        return None

def SYSIniforSqlite():
    global sysopdict
    
    rt=RFIDSYSSqliteClass.RfidSysSqlite3Class(db='../pythonconfig/sql.db')
    ret = rt.Sqlite3Getsyssetdataforweb()
    print('sqlit')
    print(ret)
    if ret==None:
        return

    dictt=json.loads(ret[0][1])
#print (dictt)
    app=dictt['app']
#usdedb=dictt['db']
    #opsys=dictt['op']
#sysopdict=dictt['op']
    sysopdict=dictt['db']
    print(sysopdict)
#   print(dictt)
#   print(app)
    if isinstance(app['ts'], int):
        pass
    else:
        app['ts']=int(app['ts'])
    if isinstance(app['ss'], int):
        pass
    else:
        app['ss']=int(app['ss'])
    if isinstance(app['a1'], int):
        pass
    else:
        app['a1']=int(app['a1'])
    if isinstance(app['a2'], int):
        pass
    else:
        app['a2']=int(app['a2'])
    if isinstance(app['a3'], int):
        pass
    else:
        app['a3']=int(app['a3'])
    if isinstance(app['a4'], int):
        pass
    else:
        app['a4']=int(app['a4'])
    if isinstance(app['aw'], int):
        pass
    else:
        app['aw']=int(app['aw'])

#    print(app)
#    print(usdedb)
#    print(opsys)
#    print(dictt['app']['sip1'])
    rt.Sqlte3Closs()
    return app

def SysIniJson():
    global sysdict
    dictt = SYSIniforSqlite()
    #dictt = ReadFromJsonFile('Rfidsys.json')
    print ('ini')
    if dictt != None:
        sysdict = dictt
        print(sysdict)
    else:
        pass
        #WriteToJsonFile('Rfidsys.json', sysdict)
    print(sysdict['sip1'])
    print(sysopdict['uploaddevice'])

    try:
        conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=0)
        conn.mset(sysdict)
#print(sysdict)
    except:
        return False
    return True


def RfidCallbackprossData(data):
    global rfidcallbackProssdata
    global RfidCMD
    global e
    tempdata = b''
    tempuseddata = b''
    s = -1
    end = 0
    if len(rfidcallbackProssdata) == 0:
        rfidcallbackProssdata = data
    else:
        rfidcallbackProssdata += data
    #    print ('rfidcallbackProssdata start:{0}'.format(rfidcallbackProssdata))
    while True:
        if end == -1:
            break

        s = rfidcallbackProssdata.find(b'\xff', end)
        if s == -1:
            return
        end = rfidcallbackProssdata.find(b'\xff', s + 1)
        if end == -1:
            tempdata = rfidcallbackProssdata[s:]
        else:
            tempdata = rfidcallbackProssdata[s:end]
        tempuseddata += tempdata
        ret = RfidCMD.ProcessorData(tempdata)
        #        print('ProcessorData DevID{0}'.format(devID))
        #        print('Pro ok:{0},{1}'.format(ret[0], ret[1]))
        # logger.debug('RfidCallbackprossData:{0},{1}'.format(ret[0], ret[1]))
        if ret[0] > 0:
            ProssAll(ret[1])
            # tempnotusedata=rfidcallbackProssdata[len(tempdata):]
            #            rfidcallbackProssdata=tempnotusedata
            continue
        else:
            while end != -1:
                end = rfidcallbackProssdata.find(b'\xff', end + 1)
                if end == -1:
                    tempdata = rfidcallbackProssdata[s:]
                else:
                    tempdata = rfidcallbackProssdata[s:end]
                tempuseddata += tempdata
                ret = RfidCMD.ProcessorData(tempdata)
                #                print('ProcessorData DevID{0}'.format(devID))
                #                print('Pro ok in while:{0},{1}'.format(ret[0], ret[1]))
                # logger.debug('RfidCallbackprossData--:{0},{1}'.format(ret[0], ret[1]))
                if ret[0] > 0:
                    ProssAll(ret[1])
                    # tempnotusedata=rfidcallbackProssdata[len(tempdata):]
                    break
                else:
                    pass

    rfidcallbackProssdata = rfidcallbackProssdata[len(tempuseddata):]


edataqueueformat = 0

def EPCAddToShowredisqueue(epc=[b'',],times=0):
    print('EPCAddToShow-------')
    print(epc)
    #return
    if times > 1 or times <0:
        times=0
    s_conn = None

    try:
        s_conn = redis.Redis(host='127.0.0.1',password='123456',port=6379,db=0)
        if s_conn.ping():
            print('EPCAddToredisqueue ok')
        else:
            print('shawanyi')
    except:  #
        print('EPCAddToredisqueue err')
        s_conn = None
        return #False
    for var in epc:
        #NUM:0;DEVID:020001080003020900010902; EPC:BBBB0000000000000000A303
        sdevs = 'NUM:{0};DEVID:{1}; {2}'.format(times,devID.decode(encoding='utf-8'),var.decode(encoding='utf-8'))
        print('rpush:{0}'.format(sdevs))
        print(s_conn.rpush('showRFID', sdevs))

def EPCAddToShowredisqueueSS(epcD=[b'',]):
    global usedtoshowtims
    EPCAddToShowredisqueue(epc=epcD,times=usedtoshowtims)
    if usedtoshowtims==0:
        usedtoshowtims=1
    else:
        usedtoshowtims=0

def EPCSendToServerThreadsockt():
    # global redisconnpool
    times=0
    s_conn = None
    usedkey = ''

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
    print('----------------------------------------------------------------------------')
    while epcsendthreadalive:
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
                    #InsertToPostgresql(devID,epc)
                    #devs = b'DEVID:' + devID + b';NUMS:' + str(len(epc)).encode(encoding='utf-8') + b';'
                    #print(devs+usedkey)
                    #ser.sendall(devs)
#                    print(epc)
                    EPCAddToShowredisqueue(epc=epc,times=times)
                    if times==0:
                        times=1
                    else:
                        times=0
                    for var in epc:
                        varepc=var.split(b':')
                        #sdevs = b'DEVID:' + devID + b';' + var + b';'
                        sdevs = b'DEVID:' + devID + b';' + varepc[1] + b'+'

                        ser.sendall(sdevs)#ser.sendall(var + b';')
                    ser.close()
                    s_conn.delete(usedkey)
                    usedkey=''
                    time.sleep(1)
                except:
                    is4grun=0
                    #time.sleep(1)
                    continue
            else:
                usedkey=''
                continue
        time.sleep(2)


def EPCSendToServerThread():
    # global redisconnpool
    times=0
    s_conn = None
    usedkey = ''
    rt4g = Com4GModularClass.Com4GModularClass(Port='/dev/ttyAMA4')
    state=rt4g.Get4GmodeStartFlg()
    if 'OK' in state:
        while True:
            state = rt4g.StartTcpUseSockA(mode=1, protocol='TCP', address=sysdict['sip1'], port=9999)
            if 'OK' in state:
                state = rt4g.SetEnableSockA(mode=1, status='OFF')
                print('========================================================================')
                print(state)
                time.sleep(1)
                break
            else:
                time.sleep(2)

    try:
        s_conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
        if s_conn.ping():
            print('EPCSendToServerThread ok')
        else:
            print('shawanyi')
    except:  #
        print('EPCSendToServerThread err')
        s_conn = None
        return False
    print('----------------------------------------------------------------------------')
    while epcsendthreadalive:
        # InsertToPostgresql(devID,epc)
        if s_conn == None:
            try:
                s_conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
                if s_conn.ping():
                    print('EPCSendToServerThread ok')
                else:
                    print('shawanyi')
                s_conn = None
                time.sleep(1)
                continue
            except:  #
                print('EPCSendToServerThread err')
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
                while True:
                    state = rt4g.SetEnableSockA(mode=1, status='ON')
#if len(state)<=0:
#                        time.sleep(1)
#                        continue
#                    if 'OK' in state:
                    if 'OK' == state:
                        print('00000000000000000000000000000000000000000000000000')
                        time.sleep(1)
                        break
                    else:
                        time.sleep(3)
                try:
                    epc = s_conn.zrange(usedkey, 0, -1)
                    print('to postgresql')
#                    print(epc)
#EPCAddToShowredisqueue(times,epc)
                    EPCAddToShowredisqueue(epc=epc,times=times)
                    if times==0:
                        times=1
                    else:
                        times=0
                    print('++++++++++++++++++++++++++++++++++++++++++++++++++++')
                    for var in epc:
                        varepc=var.split(b':')
                        #sdevs = b'DEVID:' + devID + b';' + var + b';'
                        sdevs = b'DEVID:' + devID + b';' + varepc[1] + b'+'
                        print(sdevs)
                        state = rt4g.Senddatasfornet(sdevs)
                        print(state)
                        time.sleep(1)
                    s_conn.delete(usedkey)
                    usedkey = ''
                    state = rt4g.Senddatasfornet(b'Finish')
                    time.sleep(1)
                    #state = rt4g.Senddatasfornet(b'Finish')
                    state = rt4g.SetEnableSockA(mode=1, status='OFF')
                    time.sleep(1)
                    print('-------------------------------------------------')
                    print(state)
                except:
                    time.sleep(1)
                    continue
            else:
                usedkey = ''
                continue
        time.sleep(2)

def WriteDevIDtoRedis(devID=b''):
    try:
        conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
        if conn.ping():
            print('conn ok')
        else:
            print('shawanyi')
    except:  #
        return False
    #r.set('name', 'test')
    #print(r.get('name'))
    conn.set('RFIDDevID',devID)

    return True

def AddToshowFastSS():
#    return False
    try:
        conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
        if conn.ping():
            print('conn ok')
        else:
            print('shawanyi')
    except:  #
        return False
    if conn.exists('devIDEPC'):
        epcSS = conn.zrange('devIDEPC', 0, -1)
        if len(epcSS)<1:
            return False
        else:
            EPCAddToShowredisqueueSS(epcD=epcSS)
    return True

isSysFirstFlg=0
def FirstDataToSS(pool=None, keyname='EPCDatasqueuekey'):
    global isSysFirstFlg
    global usedtoshowtims
    if isSysFirstFlg!=0:
        return False
    print('FirstDataToss start')
    try:
        conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
        if conn.ping():
            print('conn ok')
        else:
            print('shawanyi')
    except:  #
        return False

#    usdnewkeyname = 'devIDEPC-%d' % (edataqueueformat)
#    print('EPCToSqueue:' + usdnewkeyname)
#    edataqueueformat = (edataqueueformat + 1) % 20
    epc=[]
    try:
        if conn.exists('devIDEPC'):
            epc = conn.zrange('devIDEPC', 0, -1)
            if len(epc)<1:
                return False

            if conn.exists('firstdevIDEPC'):
                conn.delete('firstdevIDEPC')

        #try:
            pipe = conn.pipeline()
            # pipe.watch(usedkey)
            pipe.multi()
            for v in epc:
                pipe.zadd('firstdevIDEPC', v, 1)
            #pipe.rename('devIDEPC', usdnewkeyname)
            #pipe.expire(usdnewkeyname, 1800)
            pipe.rpush(keyname, 'firstdevIDEPC')
            pipe.execute()
        #except:
            #print('pipe EPCToSqueue err')
            #return False
        else:
            return False
    except:
        print('FirstDataToSS err')
        return False
    isSysFirstFlg=1
    print('FirstDataToss ok')
    return True


def EPCToSqueue(pool=None, keyname='EPCDatasqueuekey'):
    global edataqueueformat
    global usedtoshowtims
    try:
        conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
        if conn.ping():
            print('conn ok')
        else:
            print('shawanyi')
    except:  #
        return False

    usdnewkeyname = 'devIDEPC-%d' % (edataqueueformat)
    print('EPCToSqueue:' + usdnewkeyname)
    edataqueueformat = (edataqueueformat + 1) % 20
    #    if conn==None:
    #        conn = redisconnpool
    if conn.exists('devIDEPC'):
#        epc = conn.zrange('devIDEPC', 0, -1)
#        EPCAddToShowredisqueue(epc=epc,times=usedtoshowtims)
#        if usedtoshowtims==0:
#            usedtoshowtims=1
#        else:
#            usedtoshowtims=0

        if conn.exists(usdnewkeyname):
            conn.delete(usdnewkeyname)

        try:
            pipe = conn.pipeline()
            # pipe.watch(usedkey)
            pipe.multi()
            pipe.rename('devIDEPC', usdnewkeyname)
            pipe.expire(usdnewkeyname, 1800)
            pipe.rpush(keyname, usdnewkeyname)
            pipe.execute()
        except:
            print('pipe EPCToSqueue err')
            return False
        # else:
        #        conn.rename('devIDEPC',usdnewkeyname)
        #        conn.expire(usdnewkeyname,1800)
        #        conn.rpush(keyname,usdnewkeyname)
        return True
    else:
        return False

def EPCProsseRedis():
    global isSysFirstFlg
    global EPCProsseRedisflg
#    if isSysFirstFlg==0:
#        return(FirstDataToSS(pool=redisconnpool, keyname='EPCDatasqueuekey')
               
    EPCProsseRedisflg += 1
    if EPCProsseRedisflg > int(sysdict['ss']):  # int(sysdict['ts']):  # 30:
        EPCProsseRedisflg = 0
        return (EPCToSqueue(pool=redisconnpool, keyname='EPCDatasqueuekey'))
    else:
        if isSysFirstFlg==0:
            return(FirstDataToSS(pool=redisconnpool, keyname='EPCDatasqueuekey'))


def EPCProsseRedis11():
    global EPCProsseRedisflg
    EPCProsseRedisflg += 1
    if EPCProsseRedisflg > int(sysdict['ss']):  # int(sysdict['ts']):  # 30:
        EPCProsseRedisflg = 0
        return (EPCToSqueue(pool=redisconnpool, keyname='EPCDatasqueuekey'))



def comrecvcallbackpross(data):
    global RfidCMD
    global e

    # logger.debug('comrecvcallbackpross data:{0}'.format(data))
    RfidCallbackprossData(data)
    return


e = EmbeddedCom.ComCOMThread(Port='/dev/ttyAMA3', baudrate=115200, timeout=0.1, RCallarg=rfidcallbackdata,
                             ReceiveCallBack=comrecvcallbackpross)
tag22rev = 0
tag29rev = 0


def ProssCommand(data):
    global issysset
    global devID
    global e
    global tag22rev
    global tag29rev
    sendcmd = b''
    if len(data) < 2:
        return False
    cm, cmvalue = data[0].split(b':')
    if b'Command' != cm:
        return False
    status, stvalue = data[1].split(b':')
    if b'Status' != status:
        return False
    if b'0000' != stvalue:
        return False

    if b'0C' == cmvalue:
        if issysset < 5:
            if len(data) >= 3:
                sys, value = data[2].split(b':')
                if b'SYS' != sys:
                    return False
                if b'BOOTLOADER' == value:  #
                    issysset = 1
                    return True
                elif b'APP' == value:
                    issysset = 2
                    return True
                else:
                    return False

            else:
                return False
    elif b'09' == cmvalue:
        issysset = 1
        return True
    elif b'04' == cmvalue:
        # issysset=2
        issysset = 10
        return True
    elif b'10' == cmvalue:
        if len(data) >= 3:
            sn, value = data[2].split(b':')
            if b'SN' == sn:
                devID = value
                WriteDevIDtoRedis(devID=devID)

                if isusesubcommand == 0:
                    issysset = 6
                else:
                    issysset = 8
                return True
            else:
                return False
        else:
            return False
    elif b'22' == cmvalue:
        if len(data) >= 3:
            nums, value = data[2].split(b':')
            if b'NUMS' == nums:
                tag22rev = int(value, base=16)
                tag29rev = 0
                print('22recvnum:{0},{1}'.format(tag22rev, tag29rev))
                # logger.debug('ProssCommand 22recvnum:{0},{1}'.format(tag22rev,tag29rev))
            else:
                pass
        #        print(data)
        issysset = 7
        return True
    elif b'29' == cmvalue:
        if len(data) >= 3:
            nums, value = data[2].split(b':')
            if b'NUMS' == nums:
                getnums = int(value, base=16)
                tag29rev += getnums  # int(value,base=16)
                print('29recvnum:{0},{1}'.format(tag22rev, tag29rev))
                # logger.debug('ProssCommand 29recvnum:{0},{1}'.format(tag22rev,tag29rev))
                if getnums <= 0:
                    tag22rev = 0
                    tag29rev = 0
                    issysset = 6
                    print('29finish is zero')
                    # logger.debug('ProssCommand 29finish is zero')
                    return True
                else:
                    # print(data)
                    for vdata in data:
                        if b'EPC:' in vdata:
                            # epcdata=devID+b','+vdata
                            if redisconnpool != None:
#                                print('vdata')
#                                print(vdata)
                                # redisconnpool.zadd('devIDEPC',epcdata,1)
                                #rpush(keyname, usdnewkeyname)
                                testret=redisconnpool.zadd('devIDEPC', vdata, 1)
                                if testret == 1:
                                    print('+++++++++++++++++++++++++++')
                                    print('testret', testret)
                                    testret=redisconnpool.rpush('queue:UsedEPCSendQueue',vdata)
                                    print('push:',vdata)
                                    print('+++++++++++++++++++++++++++')
                                else:
                                    print('----------++++++++++++---------------')
                                    print('testret:',testret)
                                    print('----------++++++++++++---------------')
                                # print('EPC:{0}'.format(vdata))
                    # print(redisconnpool.zrange('devIDEPC',0,-1))

            else:
                pass
        if tag29rev >= tag22rev:
            if tag29rev>0:
                AddToshowFastSS()
            tag22rev = 0
            tag29rev = 0
            issysset = 6
            print('29finish')
            # logger.debug('ProssCommand 29finish')
        else:
            #            pass
            sendcmd = RfidCMD.GetTagMultipleCommand()
            print('GetTagMultiple:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            # logger.debug('ProssCommand GetTagMultiple:{0},{1}'.format(tag22rev,tag29rev))
            send = e.WriteSerialCOM(sendcmd[1])
        #        print(data)
        return True
    elif b'91' == cmvalue:
        issysset = 2
        return True
    elif b'92' == cmvalue:
        issysset = 2
        return True
    else:
        return False


def ProssAll(data):
    s = -1
    end = -1
    Muldata = b''
    while True:
        s = data.find(b'Command', end + 1)
        if s == -1:
            break
        end = data.find(b'Command', s + 1)
        if end == -1:
            Muldata = data[s:]
        else:
            Muldata = data[s:end]
        td = Muldata.lstrip(b'\r\n')
        td = Muldata.rstrip(b'\r\n')
        t = td.split(b'\r\n')
        ProssCommand(t)
        if end == -1:
            break


def RFIDGetTagStarOrNotSub(flg=0):
    global isusesubcommand
    if flg == 0:
        isusesubcommand = 0
    else:
        isusesubcommand = 1
    RFIDGetTagStart()

def GetSysIsStart():
    try:
        conn = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=1)
    except:
        print('GetSysIsStart ERR')
        return False
    while 1:
        ret=conn.get('RFIDSysIsStart')
        if ret==b'isok':
            return True
        time.sleep(2)
    return True


def RFIDGetTagStart():
    global issysset
    global e
    global pool
    global redisconnpool
    global GetTagProsseFlg
    global epcsendthreadalive
    sl = 1

    if not SysIniJson():  # if not SysIni():
        print('SysIni Erro')
        return
    #return


    sleeptimes = 0
    if e.RunAllStart():
        pass
    else:
        print('RFIDGetTagStart ERR Return')
        return

    pool = redis.ConnectionPool(host='127.0.0.1', password='123456', port=6379, db=1)
    # q = RedisQueue(name='RfidControl',host='127.0.0.1',psw='123456')
    try:
        redisconnpool = redis.Redis(connection_pool=pool)
        if redisconnpool.ping():
            pass
    except:
        e.CloseSerialCOM()
        return
    q = RedisQueue(name='RfidControl', pool=pool)
    if not q.istrue:
        e.CloseSerialCOM()
        print('CloseSerialCOM 0')
        return

#    epcsendthreadalive = 1

#    if sysopdict["uploaddevice"]=="4G":
#        thread_sendepc = threading.Thread(target=EPCSendToServerThread, name='EPCSendToServerThreadsockt')
#    else:
#        thread_sendepc = threading.Thread(target=EPCSendToServerThreadsockt, name='EPCSendToServerThread')

#    thread_sendepc.setDaemon(True)
#    thread_sendepc.start()
#    if GetSysIsStart()==True:
#        print('sys start ok')
#    else:
#        print('start eerr')
#        return

    while issysset < 200:
        # msg = redis_sub.parse_response()
#        msg = q.get_nowait()
#        if msg != None:
#            print(msg)
#            if msg == b'Rfidstop':
#                issysset = 199
#                q.put_extend('RfidControlAnswer', 'RfidstopOK')
#            elif msg == b'Rfidstart':
#                issysset = 0;
#                q.put_extend('RfidControlAnswer', 'RfidstartOK')
        #        SysCommand1(q)
        # SysCommand(q=q,flg=1)

        if issysset != 199:
            # EPCProsseRedis()
            EPCProsseRedis()

        if issysset == 0:
            sendcmd = RfidCMD.IsAppoBootLoad()
            print('IsAppoBootLoad:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            send = e.WriteSerialCOM(sendcmd[1])
            time.sleep(sl)  # time.sleep(2)
            continue
        elif issysset == 1:
            sendcmd = RfidCMD.BtoApp()
            print('BtoApp:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            send = e.WriteSerialCOM(sendcmd[1])
            time.sleep(sl)  # time.sleep(2)
            continue
        elif issysset == 2:
            sendcmd = RfidCMD.GetDNum()
            # sendcmd=RfidCMD.ApptoB()
            print('GetDNum:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            send = e.WriteSerialCOM(sendcmd[1])
            time.sleep(sl)  # time.sleep(2)
            
            if GetSysIsStart()==True:
                print('sys start ok')
            else:
                print('start eerr')
                
            continue
        elif issysset == 6:
            GetTagProsseFlg += 1
            if GetTagProsseFlg < int(sysdict['ts']):
                time.sleep(sl)
                continue
            sendcmd = RfidCMD.GetTagMultiple()
            GetTagProsseFlg = 0
            print('GetTagMultiple:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            send = e.WriteSerialCOM(sendcmd[1])
            sleeptimes = 0
            issysset = 106
            time.sleep(sl)  # time.sleep(2)
            continue
        elif issysset == 7:
            sendcmd = RfidCMD.GetTagMultipleCommand()
            print('GetTagMultiple:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            send = e.WriteSerialCOM(sendcmd[1])
            sleeptimes = 0
            issysset = 107
            time.sleep(sl)  # time.sleep(2)
            continue
        elif issysset == 106:
            sleeptimes += 1
            if sleeptimes > 10:
                issysset = 6
                loggererro.debug('106Sleep')
            time.sleep(sl)  # time.sleep(2)
            continue
        elif issysset == 107:
            sleeptimes += 1
            if sleeptimes > 10:
                issysset = 7
                loggererro.debug('107Sleep')
            time.sleep(sl)  # time.sleep(2)
            continue
        elif issysset == 8:
            sendcmd = RfidCMD.SubSetGetTagData()
            print('GetTagMultiple:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            send = e.WriteSerialCOM(sendcmd[1])
            time.sleep(sl)  # time.sleep(2)
            continue
        elif issysset == 9:
            # if usedAnt==1:
            #    sendcmd=RfidCMD.SetAntEnable(ant1=usedAnt,ant2=0,ant3=0,ant4=0)
            # elif usedAnt==2:
            #    sendcmd=RfidCMD.SetAntEnable(ant1=0,ant2=usedAnt,ant3=0,ant4=0)
            # elif usedAnt==3:
            #    sendcmd=RfidCMD.SetAntEnable(ant1=0,ant2=0,ant3=usedAnt,ant4=0)
            # elif usedAnt==4:
            #    sendcmd=RfidCMD.SetAntEnable(ant1=0,ant2=0,ant3=0,ant4=usedAnt)
            # else:
            #    sendcmd=RfidCMD.SetAntEnable(ant1=1,ant2=0,ant3=0,ant4=0)
            sendcmd = RfidCMD.SetAntEnable(ant1=int(sysdict['a1']), ant2=int(sysdict['a2']), ant3=int(sysdict['a3']),
                                           ant4=int(sysdict['a4']))
            print('SetAntEnable:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            send = e.WriteSerialCOM(sendcmd[1])
            time.sleep(sl)  # time.sleep(2)
            continue
        elif issysset == 10:
            # if usedAnt==1:
            #    sendcmd=RfidCMD.SetAntPower(ant1=usedAnt,ant2=0,ant3=0,ant4=0,rpower=usedPower)
            # elif usedAnt==2:
            #    sendcmd=RfidCMD.SetAntPower(ant1=0,ant2=usedAnt,ant3=0,ant4=0,rpower=usedPower)
            # elif usedAnt==3:
            #    sendcmd=RfidCMD.SetAntPower(ant1=0,ant2=0,ant3=usedAnt,ant4=0,rpower=usedPower)
            # elif usedAnt==4:
            #    sendcmd=RfidCMD.SetAntPower(ant1=0,ant2=0,ant3=0,ant4=usedAnt,rpower=usedPower)
            # else:
            #    sendcmd=RfidCMD.SetAntPower()
            sendcmd = RfidCMD.SetAntPower(ant1=int(sysdict['a1']), ant2=int(sysdict['a2']), ant3=int(sysdict['a3']),
                                          ant4=int(sysdict['a4']), rpower=int(sysdict['aw']))
            print('SetAntPower:{0},{1}'.format(sendcmd[0], sendcmd[1]))
            send = e.WriteSerialCOM(sendcmd[1])
            time.sleep(sl)  # time.sleep(2)
            continue
        else:
            time.sleep(sl)  # time.sleep(2)



if __name__ == '__main__':
    RFIDGetTagStarOrNotSub(0)  # RFIDGetTagStart()#main()
