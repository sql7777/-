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


#int UART_OpenCom(int fd, char* port,int speed)
#void UART_Close(int fd);
#int UART_Recv(int fd, char *rcv_buf, int data_len);
#int UART_Recv_nowait(int fd, char *rcv_buf, int data_len);
#int UART_Recv_Main(int fd, char *rcv_buf, int data_len, int s, int ms);
#int UART_Send(int fd, char *send_buf, int data_len);

class CUart(object):
    def __init__(self,Port=b'/dev/ttyAMA3',baudrate=115200,ReceiveCallBack=None,RCallarg=None,SoPath="./CUart.so"):
        self.sopath=SoPath
        self.ll = ctypes.cdll.LoadLibrary
        self.lib = self.ll(SoPath)
        self.fd=-1
        self.port = Port
        self.baudrate = baudrate

        self.dd = c_ubyte * 10240
        self.dest = self.dd()

        self.receivecallback=ReceiveCallBack
        self.rcallarg=RCallarg

##call
        self.funUART_Open=self.lib.UART_OpenCom
        #self.funUART_Open=self.lib.UART_Open
        self.funUART_Open.restype = c_int

        self.funUART_Close=self.lib.UART_Close
        #self.funUART_Close.restype = c_int

        #self.funUART_Set=self.lib.UART_Set
        #self.funUART_Set.restype = c_int

        #self.funUART_Init=self.lib.UART_Init
        #self.funUART_Init.restype = c_int

        self.funUART_Recv=self.lib.UART_Recv
        self.funUART_Recv.restype = c_int
        
        self.funUART_RecvNowait=self.lib.UART_Recv_nowait
        self.funUART_Recv.restype = c_int

        self.funUART_Recvbytime=self.lib.UART_Recv_Main
        self.funUART_Recv.restype = c_int

        self.funUART_Send=self.lib.UART_Send
        self.funUART_Send.restype = c_int

    def OpenUart(self):
        if self.fd>-1:
            self.CloseUart()
        #self.fd = self.funUART_Open(self.fd,self.port)
        #self.fd = self.funUART_Open(self.fd, self.port,self.baudrate)
        print('--',self.port)
        self.fd = self.funUART_Open(self.fd, cast(self.port, POINTER(c_byte)), self.baudrate)
        return self.fd

    def CloseUart(self):
        if self.fd>-1:
            self.funUART_Close(self.fd)
            self.fd=-1

    def RecvUart(self):
        ret=0
        retstr=b''
        if self.fd>-1:
            ret=self.funUART_Recv(self.fd,byref(self.dest),1024)
            if ret>0:
                retstr+=bytes(self.dest[:ret])
            else:
                ret=0
                retstr+=bytes(self.dest[:ret])
            return ret, retstr
        else:
            return ret, retstr
        
    def RecvUartNowait(self):
        ret=0
        retstr=b''
        if self.fd>-1:
            ret=self.funUART_RecvNowait(self.fd,byref(self.dest),1024)
            if ret>0:
                retstr+=bytes(self.dest[:ret])
            else:
                ret=0
                retstr+=bytes(self.dest[:ret])
            return ret, retstr
        else:
            return ret, retstr
        
    def RecvUartbytime(self,s=1,ms=0):
        ret=0
        retstr=b''
        if self.fd>-1:
            ret=self.funUART_Recvbytime(self.fd,byref(self.dest),1024,s,ms)
            if ret>0:
                retstr+=bytes(self.dest[:ret])
            else:
                ret=0
                retstr+=bytes(self.dest[:ret])
            return ret, retstr
        else:
            return ret, retstr

    def SendUart(self,data):#cast(data, POINTER(c_ubyte)),len(data)
        ret=0
        if self.fd>-1:
            ret=self.funUART_Send(self.fd,cast(data, POINTER(c_byte)),len(data))
        return ret

   
def maintest():
    com = CUart(Port=b'/dev/ttyAMA4')
    ret=com.OpenUart()
    print('open com : {0}'.format(ret))
    if ret>-1:
        ret=com.SendUart(b'1234567890')
        sendnum=0
        if ret:
            while 1:
                #ddd=com.RecvUart()
                #ddd=com.RecvUartNowait()
                ddd=com.RecvUartbytime(s=3,ms=0)
                print(ddd)
                #time.sleep(1)
                sendstr='send:'+str(sendnum)
                print(sendstr)
                #ret=com.SendUart(sendstr.encode(encoding='utf-8'))#(b'1234567890')
                sendnum+=1
                continue
                if ddd:
                    com.CloseUart()
                    break

if __name__ == '__main__':
    maintest()
    
