# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 10:58:50 2018

@author: root
"""
import sys
import ctypes
from ctypes import *
import time

import RfidCommandAnalysis

#from CUart import ComCOMThread
from ComCOMThread import ComCOMThread


class RfidManageClass(object):
    def __init__(self,Port=b'/dev/ttyAMA3',baudrate=115200,ReceiveCallBack=None,RCallarg=None):
        self.port=Port
        self.baudrate=baudrate
        self.CallBack=ReceiveCallBack
        self.RCakkarg=RCallarg

        self.rfidcallbackdata=b''
        self.rfidcallbackProssdata=b''
        self.RfidCMD = RfidCommandAnalysis.RfidCMDAnalysis()
        self.com=ComCOMThread(Port=Port,baudrate=baudrate,ReceiveCallBack=self.comrecvcallbackpross,RCallarg=self.rfidcallbackdata)

        self.issysset=0
        self.recountflg=0
        self.sysInventoryruningflg=0
        self.pause=False
        
        self.devID=b''
        self.RfidAnt={'a1':1,'a2':0,'a3':0,'a4':0,'power':3000}

        
        self.isusesubcommand=0
        self.tag22rev = 0
        self.tag29rev = 0

    def SetRfidAnt(slef,antdict={'a1':1,'a2':2,'a3':3,'a4':4,'power':3000}):
        if isinstance(antdict,dict):
            try:
                self.RfidAnt['a1']=antdict['a1']
                self.RfidAnt['a2']=antdict['a2']
                self.RfidAnt['a3']=antdict['a3']
                self.RfidAnt['a4']=antdict['a4']
                self.RfidAnt['power']=antdict['power']
                return True
            except:
                return False
        else:
            return False
        
    def GetDevID(self):
        return self.devID

    def Rev_cmd0C(self,data):
        if self.issysset < 5:
            if len(data) >= 3:
                sys, value = data[2].split(b':')
                if b'SYS' != sys:
                    return False
                if b'BOOTLOADER' == value:  #
                    self.issysset = 1
                    self.recountflg=2
                    return True
                elif b'APP' == value:
                    self.issysset = 1 #self.issysset = 2
                    self.recountflg=2
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def Rev_cmd10(self,data):
        if len(data) >= 3:
            sn, value = data[2].split(b':')
            if b'SN' == sn:
                self.devID = value
                if self.isusesubcommand == 0:
                    self.issysset = 6
                    self.recountflg=2
                else:
                    self.issysset = 8
                    self.recountflg=2
                return True
            else:
                return False
        else:
            return False

    def Rev_cmd22(self,data):
        if len(data) >= 3:
            nums, value = data[2].split(b':')
            if b'NUMS' == nums:
                self.tag22rev = int(value, base=16)
                self.tag29rev = 0
                print('22recvnum:{0},{1}'.format(self.tag22rev, self.tag29rev))
            else:
                pass
        self.issysset = 7
        self.recountflg=2
        print('22start:',int(round(time.time()*1000)))
        return True

    def Rev_cmd29(self,data):
        if len(data) >= 3:
            nums, value = data[2].split(b':')
            if b'NUMS' == nums:
                getnums = int(value, base=16)
                self.tag29rev += getnums  # int(value,base=16)
                print('29recvnum:{0},{1}'.format(self.tag22rev, self.tag29rev))
                if self.tag29rev <= 0:#if getnums <= 0:
                    self.tag22rev = 0
                    self.tag29rev = 0
                    self.issysset = 7
                    self.recountflg=2
                    print('29finish 0:',int(round(time.time()*1000)))
                    print('29finish is zero')
                    return True
                else:
                    savestr=''
                    for vdata in data:
                        savestr += (vdata.decode(encoding='utf-8') + ',')
                    usavestr=savestr.rstrip(',')
                    
                    if self.CallBack!=None:
                        print(usavestr)
                        self.RCakkarg=usavestr
                        self.CallBack(self.RCakkarg)
                    else:
                        print('no used data:',usavestr)
            else:
                print('reciev data err')
        if self.tag29rev >= self.tag22rev:
            self.tag22rev = 0
            self.tag29rev = 0
            self.issysset = 6
            self.recountflg=2
            print('29finish')
        else:
            self.issysset = 7
            self.recountflg=2
            #self.Send_cmd29()
        return True
        
    def ProssCommand(self,data):
        #print('ProssCommand:',data)
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
        #print('here')
        #print(cmvalue)
        if b'0C' == cmvalue:
            return self.Rev_cmd0C(data)
        elif b'09' == cmvalue:
            self.issysset = 1
            self.recountflg=2
            return True
        elif b'04' == cmvalue:
            self.issysset = 10
            self.recountflg=2
            return True
        elif b'10' == cmvalue:
            return self.Rev_cmd10(data)
        elif b'22' == cmvalue:
            return self.Rev_cmd22(data)
        elif b'29' == cmvalue:
            return self.Rev_cmd29(data)
        elif b'91' == cmvalue:
            self.issysset = 2
            self.recountflg=2
            return True
        elif b'92' == cmvalue:
            self.issysset = 2
            self.recountflg=2
            return True
        else:
            return False


    def ProssAll(self,data):
        #print('prossall:',data)
        ret=False
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
            ret=self.ProssCommand(t)
            if end == -1:
                break
        return ret

    def comrecvcallbackpross(self,data):
        tempdata = b''
        tempuseddata = b''
        s = -1
        end = 0
        #print('comrecvcallbackpross:',data)
        #print('next data:',self.rfidcallbackProssdata)
        if len(self.rfidcallbackProssdata) == 0:
            self.rfidcallbackProssdata = data
        else:
            self.rfidcallbackProssdata += data

        while True:
            if end == -1:
                break

            s = self.rfidcallbackProssdata.find(b'\xff', end)
            #print('s:',s)
            if s == -1:
                return
            end = self.rfidcallbackProssdata.find(b'\xff', s + 1)
            #print('end:',end)
            if end == -1:
                tempdata = self.rfidcallbackProssdata[s:]
            else:
                tempdata = self.rfidcallbackProssdata[s:end]
            ##tempuseddata += tempdata
            #print('tempuseddata',tempuseddata)
            #print('tempdata',tempdata)
            ret = self.RfidCMD.ProcessorData(tempdata)
            #print(ret)

            if ret[0] > 0:
                #print('prossall:',ret[1])
                self.ProssAll(ret[1])
                tempuseddata += tempdata
                #print('tempuseddata 4',tempuseddata)
                #print('tempdata 4',tempdata)
                continue
            else:
                if end == -1:
                    pass
                while end != -1:
                    end = self.rfidcallbackProssdata.find(b'\xff', end + 1)
                    if end == -1:
                        tempdata = self.rfidcallbackProssdata[s:]
                    else:
                        tempdata = self.rfidcallbackProssdata[s:end]
                    ##tempuseddata += tempdata
                    #print('tempuseddata 3',tempuseddata)
                    #print('tempdata 3',tempdata)
                    ret = self.RfidCMD.ProcessorData(tempdata)

                    if ret[0] > 0:
                        ##print('prossall1:',ret[1])
                        self.ProssAll(ret[1])
                        tempuseddata += tempdata
                        #print('tempuseddata 5',tempuseddata)
                        #print('tempdata 5',tempdata)
                        continue
                        #break
                    else:
                        pass

            #print('tempuseddata 1',tempuseddata)
            #print('tempdata 1',tempdata)
        #print('tempuseddata 2',tempuseddata)
        #print('tempdata 2',tempdata)
        self.rfidcallbackProssdata = self.rfidcallbackProssdata[len(tempuseddata):]
        return

    def SendCmdByDelayed(self,data=b'',delayed=0):
        tdelayed=0
        isdelayed=delayed*10000
        if data==b'':
            return False
        #print('senddata:',data,type(data))
        send = self.com.WriteSerialCOM(data)
        #print(send, tdelayed)
        self.recountflg=0
         
        while 1:
            tdelayed+=1
            
            if self.recountflg==1:
                tdelayed=0
                self.recountflg=0
            elif self.recountflg==2:
                self.recountflg=0
                return True
            if tdelayed > isdelayed:#delayed:
                return False
        return False

    
    def Send_cmd0C(self):
        sendcmd = self.RfidCMD.IsAppoBootLoad()
        print('IsAppoBootLoad:{0},{1}'.format(sendcmd[0], sendcmd[1]))
        ret=self.SendCmdByDelayed(data=sendcmd[1],delayed=100)
        print('send_cmd0c:',ret)

    def Send_cmd04(self):
        sendcmd = self.RfidCMD.BtoApp()
        print('BtoApp:{0},{1}'.format(sendcmd[0], sendcmd[1]))
        self.SendCmdByDelayed(data=sendcmd[1],delayed=100)

    def Send_cmd10(self):
        sendcmd = self.RfidCMD.GetDNum()
        print('GetDNum:{0},{1}'.format(sendcmd[0], sendcmd[1]))
        self.SendCmdByDelayed(data=sendcmd[1],delayed=100)

    def Send_cmd22(self):
        sendcmd = self.RfidCMD.GetTagMultiple()
        print('GetTagMultiple:{0},{1}'.format(sendcmd[0], sendcmd[1]))
        self.SendCmdByDelayed(data=sendcmd[1],delayed=1000)

    def Send_cmd29(self):
        sendcmd = self.RfidCMD.GetTagMultipleCommand()
        print('GetTagMultipleCommand:{0},{1}'.format(sendcmd[0], sendcmd[1]))
        self.SendCmdByDelayed(data=sendcmd[1],delayed=1000)

    def Send_cmdAA48(self):
        sendcmd = self.RfidCMD.SubSetGetTagData()
        print('GetTagMultiple:{0},{1}'.format(sendcmd[0], sendcmd[1]))
        self.SendCmdByDelayed(data=sendcmd[1],delayed=100)

    def Send_cmd91(self,ant1=1,ant2=2,ant3=3,ant4=4):
        sendcmd = self.RfidCMD.SetAntEnable(ant1=ant1, ant2=ant2, ant3=ant3,ant4=ant4)
        print('SetAntEnable:{0},{1}'.format(sendcmd[0], sendcmd[1]))
        ret=self.SendCmdByDelayed(data=sendcmd[1],delayed=100)
        if ret==True:
            self.RfidAnt['a1']=ant1
            self.RfidAnt['a2']=ant2
            self.RfidAnt['a3']=ant3
            self.RfidAnt['a4']=ant4
            #self.RfidAnt['power']=rpower

    def Send_cmd92(self,ant1=1,ant2=2,ant3=3,ant4=4,rpower=1024,wpower=3000,stime=0):
        sendcmd = self.RfidCMD.SetAntPower(ant1=ant1, ant2=ant2, ant3=ant3,ant4=ant4,rpower=rpower,wpower=wpower)#,stime=time)
        print('SetAntPower:{0},{1}'.format(sendcmd[0], sendcmd[1]))
        ret=self.SendCmdByDelayed(data=sendcmd[1],delayed=100)
        if ret==True:
            self.RfidAnt['a1']=ant1
            self.RfidAnt['a2']=ant2
            self.RfidAnt['a3']=ant3
            self.RfidAnt['a4']=ant4
            self.RfidAnt['power']=rpower

    def EndInventory(self):
        self.sysInventoryruningflg=0

    def PauseInventory(self):
        self.pause=True

    def ReInventory(self):
        self.pause=False
        
    def Inventory(self):
        if self.com.RunAllStart():
            pass
        else:
            print('Inventory run com ERR Return')
            return

        self.sysInventoryruningflg=1
        while self.sysInventoryruningflg:
            if self.pause:
                continue
            
            if self.issysset == 0:
                self.Send_cmd0C()
                continue
            elif self.issysset == 1:
                self.Send_cmd04()
                continue
            elif self.issysset == 2:
                self.Send_cmd10()
                continue
            elif self.issysset == 6:
                self.Send_cmd22()
                continue
            elif self.issysset == 7:
                self.Send_cmd29()
                continue
            elif self.issysset == 8:
                self.Send_cmdAA48()
                continue
            elif self.issysset == 9:
                self.Send_cmd91(ant1=int(self.RfidAnt['a1']),ant2=int(self.RfidAnt['a2']),ant3=int(self.RfidAnt['a3']),ant4=int(self.RfidAnt['a4']))
                continue
            elif self.issysset == 10:
                self.Send_cmd92(ant1=int(self.RfidAnt['a1']),ant2=int(self.RfidAnt['a2']),ant3=int(self.RfidAnt['a3']),ant4=int(self.RfidAnt['a4']),
                                rpower=int(self.RfidAnt['power']),wpower=int(self.RfidAnt['power']),stime=int(0))
                continue
            else:
                continue
            
        self.sysInventoryruningflg=0
        self.issysset=0


def testmain():
    t=RfidManageClass()
    t.Inventory()
    
if __name__ == '__main__':
    testmain()
