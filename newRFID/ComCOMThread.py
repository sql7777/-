# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 10:09:19 2018

@author: root
"""

import sys
import ctypes
from ctypes import *
import time

import threading
import queue

from CUartClass import CUartClass

class ComCOMThread(object):
    def __init__(self, Port=b'/dev/ttyAMA4',baudrate=115200,timeout=0.5,ReceiveCallBack=None,RCallarg=None,SoPath="./CUart.so"):
        
        self.l_serial=CUartClass(Port=Port,baudrate=baudrate,ReceiveCallBack=ReceiveCallBack,RCallarg=RCallarg,SoPath="./CUart.so")
        self.fd=-1
        self.port=Port
        self.baudrate=baudrate
        self.timeout=timeout
        self.receivecallback=ReceiveCallBack
        self.rcallarg=RCallarg
        
        print(self.port)
        self.threadalive=False

        self.thread_read=None
        self.thread_read_flg=False
        self.thread_process=None
        self.thread_process_flg=False

        self.threadLock=threading.Lock()
        self.qworkqueue=queue.Queue(10)

    def ReadSerialCOM(self):
        if self.fd>-1:
            #print('ReadSerialCOM')
            while self.threadalive:
                comReadBuf=self.l_serial.RecvUart()
                #print('ReadSerial:',comReadBuf)#print(comReadBuf)
                if comReadBuf[0]>0:
                    self.threadLock.acquire()
                    if self.qworkqueue.full():
                        print("qworkqueue00000000")
                    self.qworkqueue.put(comReadBuf[1])
                    print ('qworkqueue size : {0},tounum: {1}'.format(self.qworkqueue.qsize(), len(comReadBuf[1])))
                    self.threadLock.release()
                else:
                    continue

        
    def CloseSerialCOM(self):
        if self.fd<0:
            return False
        self.StopThread()
        self.l_serial.CloseUart()
        self.fd=-1
        return True
    
    def OpenSerialCOM(self):
        ret=-1
        if self.fd>-1:
            self.CloseSerialCOM()
        ret=self.l_serial.OpenUart()
        print('open',ret)
        self.fd=ret
        if ret<0:
            return ret
        return ret

    def WriteSerialCOM(self,data):
        #print('write',data)
        #print(type(data))
        if self.fd<0:
            if not self.OpenSerialCOM():
                return 0
        if isinstance(data,bytes):
            #ret=self.l_serial.SendUart(data)
            #print('send cmd data:',ret)
            #return ret
            return self.l_serial.SendUart(data)
        elif isinstance(data,str):
            return self.l_serial.SendUart(data.encode(encoding='utf-8'))
        elif isinstance(data,int):
            return self.l_serial.SendUart(bytes(data,))
        else:
            return 0

    def StopThread(self):
        self.threadalive=False
        if self.thread_read_flg:
            self.thread_read.join()
            self.thread_read=None
        else:
            pass
        if self.thread_process_flg:
            self.thread_process.join()
            self.thread_process=None
        else:
            pass

    def ComThreadReceiveCallBack(self):
        if self.receivecallback!=None:
            return self.receivecallback(self.rcallarg)

    def AllProcess(self):
        
        if self.fd>-1:
            #print('AllProcess')
            while self.threadalive:
                self.threadLock.acquire()
                if not self.qworkqueue.empty():
                    if self.receivecallback!=None:
                        self.rcallarg=self.qworkqueue.get()
                    else:
                        data=self.qworkqueue.get()
                    self.threadLock.release()
                    
                    if self.receivecallback!=None:
                        self.ComThreadReceiveCallBack()
                    else:
                        print(data)
                else:
                    self.threadLock.release()

    def ProcessThread(self):
        if self.thread_process==None:
            self.thread_process_flg=True
            self.threadalive=True
            self.thread_process=threading.Thread(target=self.AllProcess,name='AllProcess'+str(self.port))
            self.thread_process.setDaemon(True)
            self.thread_process.start()
            return True
        
    def StartReadThread(self):
        if self.fd<0:
            if self.OpenSerialCOM()<0:
                return False
        if self.thread_read==None:
            self.threadalive=True
            self.thread_read_flg=True
            self.thread_read=threading.Thread(target=self.ReadSerialCOM,name='ReadSerialCOM'+str(self.port))
            self.thread_read.setDaemon(True)
            self.thread_read.start()
            return True

    def RunAllStart(self):
        if self.OpenSerialCOM() > 0:
            #print('RunAllStart')
            try:
                if self.StartReadThread():
                    print ("StartReadThread")
                else:
                    print ("StartReadThread err")
                    return False
                if self.ProcessThread():
                    print ("ProcessThread")
                else:
                    self.StopThread()
                    print ("ProcessThread err")
                    return False
            except Exception as se:
                print(str(se))
                return False
        else:
            print ("OpenSerialCOM err")
            return False
        return True


def maincom():
    com=ComCOMThread(Port=b'/dev/ttyAMA3')
    if com.RunAllStart():
        sendnum=0
        while 1:
            sendstr='send:'+str(sendnum)
            sendstr=b'\xff\x00\x0c\x1d\x03'
            print(sendstr)
            print('ret:',com.WriteSerialCOM(sendstr))
            sendnum+=1
            time.sleep(2)
    

if __name__ == '__main__':
    maincom()
