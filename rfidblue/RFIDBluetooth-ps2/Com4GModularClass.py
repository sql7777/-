# -*- coding: utf-8 -*-
"""
Created on Wed March 15 11:06:31 2018

@author: root
"""
import sys
import ctypes
from ctypes import *
import EmbeddedCom4G
#import CUartThread
import time


sys4gcmddict={'AT':'AT','Zreboot':'Z','devreboot':'REBOOT','issetopen':'E',
              'outcmd':'ENTM','workmod':'WKMOD','cmdPW':'CMDPW','Startinformation':'STMSG',
              'signalintensity':'CSQ','rstarttime':'RSTIM','networkinfo':'SYSINFO',
              'FactoryDefault':'RELD','ofsetting':'CLEAR','saveset':'CFGTF',
              'getver':'VER','getSN':'SN','getICCID':'ICCID','getIMEI':'IMEI',
              'UART':'UART','UARTFT':'UARTFT','UARTFL':'UARTFL','RFCEN':'RFCEN',
              'APN':'APN','SOCKA':'SOCKA','SOCKB':'SOCKB','SOCKC':'SOCKC',
              'SOCKD':'SOCKD','SOCKAEN':'SOCKAEN','SOCKBEN':'SOCKBEN','SOCKCEN':'SOCKCEN',
              'SOCKDEN':'SOCKDEN','SOCKASL':'SOCKASL','SOCKBSL':'SOCKBSL','SOCKCSL':'SOCKCSL',
              'SOCKDSL':'SOCKDSL','SOCKALK':'SOCKALK','SOCKBLK':'SOCKBLK','SOCKCLK':'SOCKCLK',
              'SOCKDLK':'SOCKDLK','SHORATO':'SHORATO','SHORBTO':'SHORBTO','SHORCTO':'SHORCTO',
              'SHORDTO':'SHORDTO','SOCKATO':'SOCKATO','SOCKBTO':'SOCKBTO','SOCKCTO':'SOCKCTO',
              'SOCKDTO':'SOCKDTO','SOCKIND':'SOCKIND','SDPEN':'SDPEN','REGEN':'REGEN',
              'REGTP':'REGTP','REGDT':'REGDT','REGSND':'REGSND','CLOUD':'CLOUD',
              'HEARTEN':'HEARTEN','HEARTDT':'HEARTDT','HEARTSND':'HEARTSND','HEARTTM':'HEARTTM',
              'HTPTP':'HTPTP','HTPURL':'HTPURL','HTPSV':'HTPSV','HTPHD':'HTPHD','HTPTO':'HTPTO',
              'HTPFLT':'HTPFLT','SMSEND':'SMSEND','CISMSSEND':'CISMSSEND'}
#sysdict={'commandkey':'usr.cn','DeviceRuninformation':'[USR-LTE-7S4]'}

#'\r\n'
class Com4GModularClass(object):
    def __init__(self,Port='/dev/ttySAC2',baudrate=115200,protocol='TCP',address='218.240.49.25',netport=9999,ReceiveCallBack=None,RCallarg=None):

        self.sysdict={'commandkey':'usr.cn','DeviceRuninformation':'[USR-LTE-7S4]'}
        self.comisopen=False
        self.comport=Port
        self.combaudrate=baudrate
        self.receivecallback=ReceiveCallBack
        self.rcallarg=RCallarg
        self.usedcom_callbackdata=b''
#        self.usedcom_4G=EmbeddedCom4G.ComCOMThread(Port=self.comport,baudrate=self.combaudrate,timeout=0.5,RCallarg=self.usedcom_callbackdata,ReceiveCallBack=self.usedcom_callbackpross)
        self.usedcom_4G=EmbeddedCom4G.ComCOMThread(Port=self.comport,baudrate=self.combaudrate,timeout=0.5,RCallarg=None,ReceiveCallBack=None)
        #        self.usedcom_4G=CUartThread.CUartThread(Port=self.comport,baudrate=self.combaudrate,RCallarg=self.usedcom_callbackdata,ReceiveCallBack=self.usedcom_callbackpross)
        self.is4gsysrun=0
        self.sysstate=0
        self.operationdict={'usingcmd':'','value':''}
        self.readtimesout=100

        self.pl=protocol
        self.ad=address
        self.netport=netport

    def usedcom_callbackpross(self,data):
        if self.is4gsysrun == 0:
            ffutf8 = self.sysdict['DeviceRuninformation'].encode(encoding='utf-8')
            if ffutf8 in data:
                self.is4gsysrun = 1
                print('4G Run OK')
                #self.GetCMDPW()
        else:
            if self.sysstate==200:
                if self.receivecallback!=None:
                    self.receivecallback(data)
                else:
                    pass
            else:
                pass

    def Get4GmodeStartFlgfortime(self,timeout=100):
        times=0
        if self.is4gsysrun == 0:

            ret=self.usedcom_4G.OpenSerialCOM()
            print (ret)
            if ret < 0:
                return 'ERR'
            self.comisopen=True
            print('Get4GmodeStartFlg')
            ffutf8 = self.sysdict['DeviceRuninformation'].encode(encoding='utf-8')
            revdata = b''
            while True:
                tdata=self.usedcom_4G.ReadDataFromSerialCOM()
                #print (tdata)
                if len(tdata)>0:
                    print (tdata)
                    times=0
                    if ffutf8 in tdata:
                        print('4G Run OK')
                        self.is4gsysrun=1
                        return 'OK'
                else:
                    times=times+1
                    if times>=timeout:
                        return 'ERR'

    def Get4GmodeStartFlg(self):
        if self.is4gsysrun == 0:

            ret=self.usedcom_4G.OpenSerialCOM()
            print (ret)
            if ret < 0:
                return 'ERR'
            self.comisopen=True
            print('Get4GmodeStartFlg')
            ffutf8 = self.sysdict['DeviceRuninformation'].encode(encoding='utf-8')
            revdata = b''
            while True:
                tdata=self.usedcom_4G.ReadDataFromSerialCOM()
                #print (tdata)
                if len(tdata)>0:
                    print (tdata)
                    if ffutf8 in tdata:
                        print('4G Run OK')
                        self.is4gsysrun=1
                        return 'OK'
                    #else:
                        #revdata+=tdata
                        #if ffutf8 in revdata:
                            #print('4G Run OK 1')
                            #self.is4gsysrun=1
                            #return 'OK'

    def SendCmdByAT(self,cmd,parameter=''):
        #if self.is4gsysrun == 0:
        #    return 0
        self.operationdict['usingcmd'] = cmd
        cmdstr='AT+'+cmd+parameter+'\r'
        print (cmdstr)
        return self.usedcom_4G.WriteSerialCOM(cmdstr.encode(encoding='utf-8'))
        #self.usedcom_4G.SendUart(cmdstr.encode(encoding='utf-8'))
        #return 1

    def SendCmdByPassword(self,cmd,parameter=''):
        #if self.is4gsysrun == 0:
        #    return 0
        self.operationdict['usingcmd']=cmd
        cmdstr=self.sysdict['commandkey']+'AT+'+cmd+parameter+'\r'
        print (cmdstr)
        return self.usedcom_4G.WriteSerialCOM(cmdstr.encode(encoding='utf-8'))
        #self.usedcom_4G.SendUart(cmdstr.encode(encoding='utf-8'))
        #return 1

    def RebootSoftware(self,mode=1):
        cmd=sys4gcmddict['Zreboot']
        print('RebootSoftware')
        comret=0
        if mode==0:
            comret = self.SendCmdByAT(cmd)
        else:
            comret = self.SendCmdByPassword(cmd)
        if comret <= 0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        return 'ERR'
        #else:
        #    return 'ERR'

    def RebootDevice(self,mode=1):
        cmd=sys4gcmddict['devreboot']
        print('RebootDevice')
        comret=0
        if mode==0:
            comret = self.SendCmdByAT(cmd)
        else:
            comret = self.SendCmdByPassword(cmd)
        if comret <= 0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        return 'ERR'
        #else:
        #    return 'ERR'

    def GetStatus(self,mode=1):
        if self.comisopen==False:
            return 'ERR'
        cmd=sys4gcmddict['issetopen']
        print ('GetStatus')
        comret=0
        if mode==0:
            comret = self.SendCmdByAT(cmd)
        else:
            comret = self.SendCmdByPassword(cmd)
        if comret <= 0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'+E' in getrevdata:
                if b'ON' in getrevdata:
                    return 'ON'
                elif b'OFF' in getrevdata:
                    return 'OFF'
                else:
                    return 'ERR'
        return 'ERR'
        #else:
        #    return 'ERR'

    def SetStatus(self,mode=1,status='ON'):
        if status == 'ON' or status == 'OFF':
            pass
        else:
            return 'ERR'
        cmd=sys4gcmddict['devreboot']
        print('SetStatus')
        comret=0
        if mode==0:
            comret = self.SendCmdByAT(cmd,'='+status)
        else:
            comret = self.SendCmdByPassword(cmd,'='+status)
        if comret <= 0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        return 'ERR'
        #else:
        #    return 'ERR'

    def BackMode(self,mode=1):
        cmd=sys4gcmddict['outcmd']
        print('BackMode')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd)
        else:
            comret = self.SendCmdByPassword(cmd)
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        return 'ERR'
        #else:
        #    return 'ERR'

    def GetWKMod(self,mode=1):
        cmd=sys4gcmddict['workmod']
        print('GetWKMod')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd)
        else:
            comret = self.SendCmdByPassword(cmd)
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'+WKMOD' in getrevdata:
                if b'NET' in getrevdata:
                    return 'NET'
                elif b'HTTPD' in getrevdata:
                    return 'HTTPD'
                else:
                    return 'ERR'
        return 'ERR'
        #else:
        #    return 'ERR'

    def SetWKMod(self,mode=1,status='NET'):
        if status == 'NET' or status == 'HTTPD':
            pass
        else:
            return 'ERR'
        cmd=sys4gcmddict['workmod']
        print('SetWKMod')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd,'='+status)
        else:
            comret = self.SendCmdByPassword(cmd,'='+status)
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        return 'ERR'
        #else:
        #    return 'ERR'

    def GetCMDPW(self,mode=1):#...
        cmd=sys4gcmddict['cmdPW']
        print('GetCMDPW')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd)
        else:
            comret = self.SendCmdByPassword(cmd)
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'+CMDPW' in getrevdata:
                return getrevdata
        return 'ERR'
        #else:
        #    return 'ERR'

    def SetCMDPW(self,mode=1,password='usr.cn'):
        cmd=sys4gcmddict['cmdPW']
        print('SetCMDPW')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd,'='+password)
        else:
            comret = self.SendCmdByPassword(cmd,'='+password)
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        return 'ERR'
        #else:
        #    return 'ERR'

    def SaveTodefault(self,mode=1):
        cmd=sys4gcmddict['saveset']
        print ('SaveTodefault')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd)
        else:
            comret = self.SendCmdByPassword(cmd)
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        return 'ERR'
        #else:
        #    return 'ERR'

    def GetSockA(self,mode=1):
        cmd=sys4gcmddict['SOCKA']
        print('GetSockA')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd)
        else:
            comret = self.SendCmdByPassword(cmd)
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'+SOCKA' in getrevdata:
                return getrevdata
        return 'ERR'
        #else:
        #    return 'ERR'

    def SetSockA(self,mode=1,protocol='TCP',address='218.240.49.25',port=9999):
        if protocol == 'TCP' or protocol == 'UDP':
            pass
        else:
            return 'ERR'
        cmd=sys4gcmddict['SOCKA']
        print('SetSockA')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd,'='+protocol+','+address+','+str(port))
        else:
            comret = self.SendCmdByPassword(cmd,'='+protocol+','+address+','+str(port))
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        return 'ERR'
        #else:
        #    return 'ERR'


    def GetEnableSockA(self,mode=1):
        cmd=sys4gcmddict['SOCKAEN']
        print('GetEnableSockA')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd)
        else:
            comret = self.SendCmdByPassword(cmd)
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'+SOCKAEN' in getrevdata:
                if b'ON' in getrevdata:
                    return 'ON'
                elif b'OFF' in getrevdata:
                    return 'OFF'
                else:
                    return b'ERR'
        return 'ERR'
        #else:
        #    return 'ERR'


    def SetEnableSockA(self,mode=1,status='ON'):
        if status == 'ON' or status == 'OFF':
            pass
        else:
            return 'ERR'
        cmd=sys4gcmddict['SOCKAEN']
        print('SetEnableSockA')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd,'='+status)
        else:
            comret = self.SendCmdByPassword(cmd,'='+status)
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        return 'ERR'
        #else:
        #    return 'ERR'

    def GetLinkstatusSockA(self,mode=1):
        cmd=sys4gcmddict['SOCKALK']
        print('GetLinkstatusSockA')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd)
        else:
            comret = self.SendCmdByPassword(cmd)
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'+SOCKALK' in getrevdata:
                if b'ON' in getrevdata:
                    return 'ON'
                elif b'OFF' in getrevdata:
                    return 'OFF'
                else:
                    return 'ERR'
        return 'ERR'
        #else:
        #    return 'ERR'

    def GetTransmission(self,mode=1):
        cmd=sys4gcmddict['SOCKIND']
        print('GetTransmission')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd)
        else:
            comret = self.SendCmdByPassword(cmd)
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'+SOCKIND' in getrevdata:
                if b'ON' in getrevdata:
                    return 'ON'
                elif b'OFF' in getrevdata:
                    return 'OFF'
                else:
                    return 'ERR'
        return 'ERR'
        #else:
        #    return 'ERR'

    def SetTransmission(self,mode=1,status='ON'):
        if status == 'ON' or status == 'OFF':
            pass
        else:
            return 'ERR'
        cmd=sys4gcmddict['SOCKIND']
        print('SetTransmission')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd,'='+status)
        else:
            comret = self.SendCmdByPassword(cmd,'='+status)
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        return 'ERR'
        #else:
        #    return 'ERR'

    def GetReconnectionSockA(self,mode=1):
        cmd=sys4gcmddict['SOCKATO']
        print('GetReconnectionSockA')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd)
        else:
            comret = self.SendCmdByPassword(cmd)
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'+SOCKATO' in getrevdata:
                if b':' in getrevdata:
                    getrevdata.strip()
                    devid, value = getrevdata.split(b':')
                    return value.decode(encoding='utf-8')
                else:
                    return 'ERR'
        return 'ERR'
        #else:
        #    return 'ERR'

    def SetReconnectionSockA(self,mode=1,s=1):
        if s < 1 or s > 100:
            s=1
        cmd=sys4gcmddict['SOCKATO']
        print('SetReconnectionSockA')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd,'='+str(s))
        else:
            comret = self.SendCmdByPassword(cmd,'='+str(s))
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        return 'ERR'
        #else:
        #    return 'ERR'

    def GetConnectModeSockA(self,mode=1):
        cmd=sys4gcmddict['SOCKASL']
        print('GetConnectModeSockA')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd)
        else:
            comret = self.SendCmdByPassword(cmd)
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'+SOCKASL' in getrevdata:
                if b'SHORT' in getrevdata:
                    return 'SHORT'
                elif b'LONG' in getrevdata:
                    return 'LONG'
                else:
                    return 'ERR'
        return 'ERR'
        #else:
        #    return 'ERR'

    def SetConnectModeSockA(self,mode=1,status='LONG'):
        if status == 'SHORT' or status == 'LONG':
            pass
        else:
            return 'ERR'
        cmd=sys4gcmddict['SOCKASL']
        print('SetConnectModeSockA')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd,'='+'status')
        else:
            comret = self.SendCmdByPassword(cmd,'='+'status')
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        return 'ERR'
        #else:
        #    return 'ERR'

    def QuerySysNetInfo(self,mode=1):
        cmd=sys4gcmddict['networkinfo']
        print('QuerySysNetInfo')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd)
        else:
            comret = self.SendCmdByPassword(cmd)
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'+SYSINFO' in getrevdata:
                try:
                    getrevdata.strip()
                    devid, value = getrevdata.split(b':')
                    state,net=value.split(b',')
                    if int(state)==2:
                        return 'OK:'+value.decode(encoding='utf-8')
                    else:
                        return value.decode(encoding='utf-8')
                except:
                    print('+SYSINFO   ERR')
                    return 'ERR'
                #elif int(state)==0:
                #elif int(state)==1:
                #elif int(state)==3:
                #elif int(state)==4:
                #else:

                #return value
        return 'ERR'
        #else:
        #    return 'ERR'

    def GetUartft(self,mode=1):
        cmd=sys4gcmddict['UARTFT']
        print('GetUartft')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd)
        else:
            comret = self.SendCmdByPassword(cmd)
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'+UARTFT' in getrevdata:
                if b':' in getrevdata:
                    getrevdata.strip()
                    devid, value = getrevdata.split(b':')
                    return value.decode(encoding='utf-8')
                else:
                    return 'ERR'
        return 'ERR'
        #else:
        #    return 'ERR'

    def SetUartft(self, mode=1,ms=50):
        if ms < 50 or ms > 60000:
            ms=50
        cmd=sys4gcmddict['SOCKATO']
        print('SetReconnectionSockA')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd,'='+str(ms))
        else:
            comret = self.SendCmdByPassword(cmd,'='+str(ms))
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                return 'OK'
        return 'ERR'
        #else:
        #    return 'ERR'

    def SysActivTest(self,mode=1):
        cmd=sys4gcmddict['AT']
        print('SysActivTest')
        comret = 0
        if mode==0:
            comret = self.SendCmdByAT(cmd)
        else:
            comret = self.SendCmdByPassword(cmd)
        if comret<=0:
            return 'ERR'
        getrevdata=self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=self.readtimesout)
        print(getrevdata)
        if getrevdata == None:
            return 'ERR'
        if len(getrevdata)>0:
            if b'OK' in getrevdata:
                self.is4gsysrun = 1
                return 'OK'
            else:
                return 'ERR'
        return 'ERR'
        #else:
        #    return 'ERR'

    def SysSet4Ginit(self,mode=1, protocol='TCP', address='218.240.49.25', port=9999):
        if self.comisopen!=True:
            ret = self.usedcom_4G.OpenSerialCOM()
            print(ret)
            if ret < 0:
                return 'ERR:OpenSerialCOM'
            self.comisopen = True
        #ret = self.SysActivTest(mode=mode)
        #while ret!='OK':
        #    time.sleep(2)
        #    ret = self.SysActivTest(mode=mode)

        ret=self.GetWKMod(mode=mode)
        if 'NET' in ret:
            pass
        else:
            ret=self.SetWKMod(mode=mode,status='NET')
            if 'OK' in ret:
                pass
            else:
                return 'ERR:SetWKMod'
        ret=self.GetUartft(mode=mode)
        if 'ERR' in ret:
            return 'ERR:GetUartft'
        else:
            if int(ret)!=50:
                ret=self.SetUartft(mode=mode,ms=50)
                if 'OK' in ret:
                    pass
                else:
                    return 'ERR:SetUartft'
        ret=self.GetTransmission(mode=mode)
        if 'ON'in ret:
            pass
        else:
            ret=self.SetTransmission(mode=mode,status='ON')
            if 'OK' in ret:
                pass
            else:
                return 'ERR:SetTransmission'
        ret=self.GetConnectModeSockA(mode=mode)
        if 'LONG' in ret:
            pass
        else:
            ret=self.SetConnectModeSockA(mode=mode,status='LONG')
            if 'OK' in ret:
                pass
            else:
                return 'ERR:SetConnectModeSockA'
        ret=self.GetReconnectionSockA(mode=mode)
        if 'ERR' in ret:
            return 'ERR:GetReconnectionSockA'
        else:
            if int(ret)!=1:
                ret=self.SetReconnectionSockA(mode=mode,s=1)
                if 'ERR' in ret:
                    return 'ERR:SetReconnectionSockA'
        ret=self.SetSockA(mode=mode,protocol=protocol,address=address,port=port)
        if 'ERR' in ret:
            return 'ERR:SetSockA'
        self.pl = protocol
        self.ad = address
        self.netport = port
        ret=self.GetEnableSockA(mode=mode)
        if 'ON' in ret:
            pass
        else:
            ret=self.SetEnableSockA(mode=mode,status='ON')
            if 'ERR' in ret:
                return 'ERR:SetEnableSockA'
        ret=self.SaveTodefault(mode=mode)
        if 'ERR' in ret:
            return 'ERR:SaveTodefault'

        self.sysstate = 200
        return 'OK'

    def GetSys4GLinkStateA(self,mode=1):
        #ret = self.SysActivTest(mode=mode)
        #if 'OK' == ret:
        #    pass
        #else:
        #    return 'ERR:SysActivTest'
        ret=self.QuerySysNetInfo(mode=mode)
        if 'OK' in ret:
            pass
        else:
            return 'ERR:'+ret
        ret=self.GetLinkstatusSockA(mode=mode)
        if 'ON' in ret:
            return 'OK'
        else:
            return 'ERR:GetLinkstatusSockA,'+ret

    def SenddatafromSockA(self,mode=1,sddata=b''):
        ret = self.GetLinkstatusSockA(mode=mode)
        if 'ON' in ret:
            pass
        else:
            return 0
        return self.usedcom_4G.WriteSerialCOM(sddata)

    def SenddatafromSockArev(self,mode=1,revs=50,sddata=b''):
        ret=self.SenddatafromSockA(mode=mode,sddata=sddata)
        if ret > 0:
            tdata = self.usedcom_4G.ReadDataFromSerialCOMTimeout(TimeOut=revs)
            return tdata
        else:
            return b''



    def StartTcpUseSockA(self, mode=1, protocol='TCP', address='218.240.49.25', port=9999):
        ret = self.SetWKMod(mode=mode,status='NET')
        print('self.SetWKMod')
        print(ret)
        if ret != 'OK':
            return ret
        ret = self.SetEnableSockA(mode=mode,status='ON')
        print('self.SetEnableSockA')
        print(ret)
        if ret != 'OK':
            return ret
        ret = self.SetSockA(mode=mode, protocol=protocol, address=address, port=port)
        print('self.SetSockA')
        print(ret)
        if ret != 'OK':
            return ret
        #ret = self.RebootSoftware(mode=mode)
        #if ret != 'OK':
        #    return ret
        self.sysstate = 200

        self.pl = protocol
        self.ad = address
        self.netport = port
        time.sleep(1)
        return ret


    def Senddatasfornet(self,sddata):
        if self.sysstate!=200:
            if self.StartTcpUseSockA(mode=1,protocol=self.pl,address=self.ad,port=self.netport)!='OK':
                #time.sleep(2)
                return 0
        #comsenddata=sddata+'\r'
        #return self.usedcom_4G.WriteSerialCOM(sddata.encode(encoding='utf-8'))
        return self.usedcom_4G.WriteSerialCOM(sddata)

        #return self.usedcom_4G.SendUart(sddata)



def Test4GRunself():
    sss=b'DEVID:020001080003020900010902;BBBB0000000000000000A303+'
    rt4g=Com4GModularClass(Port='/dev/ttyAMA4',protocol='TCP',address='47.95.112.32',netport=9999)
    ret=rt4g.Get4GmodeStartFlgfortime(timeout=500)
    print (ret) #if 'OK' in ret:
    ret=rt4g.SysSet4Ginit(mode=1, protocol='TCP', address='47.95.112.32', port=9999)
    print(ret)
    if 'OK' in ret:
        pass
    else:
        while 1:
            time.sleep(2)
            ret = rt4g.SysSet4Ginit(mode=1, protocol='TCP', address='47.95.112.32', port=9999)
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
    while 1:
        ret=rt4g.SenddatafromSockArev(mode=1,revs=50,sddata=sss)
        print ('RECVdata:')
        print(ret)
        time.sleep(5)


def RunMain():
    data=b'1234567890'
    rt = Com4GModularClass(Port='/dev/ttyAMA4')



    #print(rt.OpenUart())
    state=rt.Get4GmodeStartFlg()
    if 'OK' in state:
        print(rt.GetStatus())
        #print(rt.StartTcpUseSockA())
        time.sleep(2)
        state=rt.Senddatasfornet(data)
        print (state)
    time.sleep(2)
    print(rt.SetEnableSockA(mode=1, status='OFF'))
    time.sleep(5)
    print(rt.StartTcpUseSockA())
    time.sleep(2)
    state = rt.Senddatasfornet(data)
    print(state)
    print('end')
    time.sleep(5)
    print(rt.SetEnableSockA(mode=1, status='OFF'))
    
    while True:
        time.sleep(1)


#    if rt.usedcom_4G.RunAllStart():
#        print("com ok")
#    else:
#        print('RFIDGetTagStart ERR Return')
#        return
#    while(1):
#        time.sleep(2)
#        #rt.GetCMDPW()
def RunMain1():
    rt = Com4GModularClass(Port='/dev/ttyAMA4')
    ret = rt.usedcom_4G.OpenSerialCOM()
    print(ret)
    if ret < 0:
        return 'ERR'
    rt.comisopen=True
    time.sleep(10)
    while True:
        print(rt.GetStatus())
        time.sleep(5)

if __name__ == '__main__':
    Test4GRunself()
    #RunMain()
    #RunMain1()
