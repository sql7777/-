# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 21:58:41 2018

@author: root
"""

import redis
import json
import uuid
from copy import deepcopy

import requests
from requests.auth import HTTPBasicAuth


class DataObjectJSRedisClass(object):
    def __init__(self,host='127.0.0.1',psw='123456',port=6379,db=0,uuidname='',indexkey=''):

        self.host=host
        self.psw=psw
        self.port=port
        self.db=db
        self.uuid=uuidname
        
        self.uuidlistname=None

        self.TemplateKeyvalue=None

        self.tempid=0

        self.objectindex=0
        self.indexkey=indexkey
        
    def GetUUIDforRestful(self,host='127.0.0.1', port=6666,username='',pwd=''):
        url='http://{0}:{1}/UUID'.format(host,port)
        try:
            response=requests.get(url=url,auth=HTTPBasicAuth(username,pwd))
            return response
        except:
            return None

    def GetUUID(self):
        ret=self.GetUUIDforRestful()
        if ret!=None:
            getuuid=ret.text
            print('restfulid:',getuuid)
        else:
            getuuid=uuid.uuid1()
            print('uuid:',getuuid)
        uids=str(getuuid).replace('-','')
        self.uuid=uids
        self.uuidlistname=self.uuid+'.hlist'
        return self.uuid
            
#        uid=uuid.uuid1()
#        uids=str(uid).replace('-','')
#        print(uids)
#        id='12345678901234567890123456789012'
#        self.uuid=id
#        self.uuidlistname=self.uuid+'.hlist'
#        return id

    def GetSelfUUID(self):
        return self.uuid

    def GetkvDict(self,jsdata1=None,jsdata2=None):
        retdict={}
        for key,value in jsdata1.items():
            if isinstance(value,dict):
                if isinstance(jsdata2[key],dict):
                    ret=self.GetkvDict(jsdata1=value,jsdata2=jsdata2[key])
                    if ret!=False:
                        retdict.update(ret)
                    else:
                        return False
                else:
                    return False
            elif isinstance(value,list):
                if isinstance(jsdata2[key],list):
                    ret=self.GetkvList(jsdata1=value,jsdata2=jsdata2[key])
                    if ret!=False:
                        retdict.update(ret)
                    else:
                        return False
                else:
                    return False
            else:
                usekey, usetype=value.split(':')
                retdict.setdefault(usekey,jsdata2[key])
        return retdict

    def GetkvList(self,jsdata1=None,jsdata2=None):
        index=-1
        retdict={}
        for v in jsdata1:
            index+=1
            if isinstance(v,dict):
                if isinstance(jsdata2[index],dict):
                    ret=self.GetkvDict(jsdata1=v,jsdata2=jsdata2[index])
                    if ret!=False:
                        retdict.update(ret)
                    else:
                        return False
                else:
                    return False
            elif isinstance(v,list):
                if isinstance(jsdata2[index],list):
                    ret=self.GetkvList(jsdata1=value,jsdata2=jsdata2[index])
                    if ret!=False:
                        retdict.update(ret)
                    else:
                        return False
                else:
                    return False
            else:
                usekey, usetype=v.split(':')
                retdict.setdefault(usekey,jsdata2[index])
        return retdict

   
    def MakeUseIDdict(self,id='',jsdata=None,layer=-1):
        tlayer=layer+1
        num=0
        for key,value in jsdata.items():
            if isinstance(value,dict):
                retid=self.MakeUseIDdict(id=id,jsdata=value,layer=tlayer)
            elif isinstance(value,list):
                retid=self.MakeUseIDlist(id=id,jsdata=value,layer=tlayer)
            else:
                if isinstance(value,int):
                    vtype='int'
                elif isinstance(value,float):
                    vtype='float'
                else:
                    vtype='string'
                tvalue=id+'.'+str(self.tempid)
                #tvalue=id+'.'+str(layer*100+num)
                jsdata[key]=tvalue+':'+vtype
                self.tempid+=1
                num=num+1
    
    def MakeUseIDlist(self,id='',jsdata=None,layer=-1):
        tlayer=layer+1
        num=0
        for v in jsdata:
            if isinstance(v,dict):
                retid=self.MakeUseIDdict(id=id,jsdata=v,layer=tlayer)
            elif isinstance(v,list):
                retid=self.MakeUseIDlist(id=id,jsdata=v,layer=tlayer)
            else:
                if isinstance(v,int):
                    vtype='int'
                elif isinstance(v,float):
                    vtype='float'
                else:
                    vtype='string'
                tvalue=id+'.'+str(self.tempid)
                #tvalue=id+'.'+str(layer*100+num)
                jsdata[num]=tvalue+':'+vtype
                self.tempid+=1
                num=num+1

  
    def MakeTemplateuseID(self,jsdata=None):
        if jsdata==None:
            return False
        self.tempid=0
        
        if isinstance(jsdata,dict):
            retid=self.MakeUseIDdict(id='key',jsdata=jsdata)
        elif isinstance(jsdata,list):
            retid=self.MakeUseIDlist(id='key',jsdata=jsdata)
        else:
            return False
        print('TemplateKeyvalue:',self.TemplateKeyvalue)
        return True
        
    def InitTemplate(self,Template=None,dictdata=None):#初始对象模板
        if self.TemplateKeyvalue!=None:
            return False
        istosaveflg=0
        if Template!=None:
            jsdata=Template
        elif dictdata!=None:
            jsdata=dictdata
        else:
            return False
        
        if isinstance(jsdata,str):
            jsd=jsdata.replace('\'','"')
            c_data=json.loads(jsd)
            print(c_data)
        else:
            c_data=jsdata
            
        if Template!=None:
            self.TemplateKeyvalue=deepcopy(c_data)
        else:
            if dictdata!=None:
                self.TemplateKeyvalue=deepcopy(c_data)
                istosaveflg=1
            else:
                return False
        #self.MakeTemplateuseID(jsdata=self.TemplateKeyvalue)
        #return True
        #return self.MakeTemplateuseID(jsdata=self.TemplateKeyvalue)
        ret=self.MakeTemplateuseID(jsdata=self.TemplateKeyvalue)
        if ret==False:
            self.TemplateKeyvalue.clear()
            self.TemplateKeyvalue=None
            return False
        if istosaveflg==1:
            return self.datatoredis(dictdata=c_data)
        return True

    def makehashkeyvalue(self,dictdata=''):
        if dictdata=='':
            return False
        if isinstance(dictdata,str):
            jsd=dictdata.replace('\'','"')
            c_data=json.loads(jsd)
            print(c_data)
        else:
            c_data=dictdata
        #print('TemplateKeyvalue',type(self.TemplateKeyvalue))
        try:
            if isinstance(self.TemplateKeyvalue,dict):
                retid=self.GetkvDict(jsdata1=self.TemplateKeyvalue,jsdata2=c_data)
            elif isinstance(self.TemplateKeyvalue,list):
                retid=self.GetkvList(jsdata1=self.TemplateKeyvalue,jsdata2=c_data)
            else:
                return False
        except:
            print('makehashkeyvalue err')
            return False
        #print('temp:',retid)
        return retid
                                    
    def datatoredis(self,dictdata=''):
        if dictdata=='':
            return False
        if self.TemplateKeyvalue==None:
            return False
        if self.uuid=='':
            self.GetUUID()
        #print (dictdata)
        if isinstance(dictdata,str):
            jsd=dictdata.replace('\'','"')
            c_data=json.loads(jsd)
            print(c_data)
        else:
            c_data=dictdata
        ret=self.makehashkeyvalue(dictdata=c_data)
        if ret == False:
            return False
        print(ret)

        if self.indexkey!='':
            try:
                hashkeylist=c_data[self.indexkey]
                if isinstance(hashkeylist, dict) or isinstance(hashkeylist, list):
                    print(hashkeylist,type(hashkeylist))
                    return False
            except:
                return False
        else:
            hashkeylist=str(self.objectindex)
            #self.objectindex+=1
        print(hashkeylist)

        retaddset=self.AddSetRedis(hashkeylist=hashkeylist,data=ret)
        print('datatoredis:',retaddset)
        return retaddset

    def AddSetRedis(self,hashkeylist='',data=None):
        if hashkeylist=='' or data==None:
            return False
        if self.uuidlistname==None:
            self.uuidlistname=self.uuid+'.hlist'
        #hashname=self.uuid+'.hlist'
        #print('hashname:',hashname)
        print('hashkeylist:',hashkeylist)
        print('data:',data)
        existflg=0
        try:
            conn = redis.Redis(host=self.host,password=self.psw,port=self.port,db=self.db)
            if conn.ping():
                pass#print('conn ok')
            else:
                print('shawanyi')
                return None
            ret=conn.hget(name=self.uuidlistname,key=hashkeylist)
            if ret != None:
                #print('has ret uuid:',ret)
                setname=ret
                existflg=0
            else:
                setname=self.uuid+'.'+str(self.objectindex)
                self.objectindex += 1
                existflg=1
                
            pipe = conn.pipeline()
            pipe.multi()
            ##if pipe.hexists(name=hashname,key=indexkey):
            #ret=pipe.hget(name=hashname,key=hashkeylist)
            #if ret != None:
            #    print('has ret uuid:',ret)
            #    setname=ret
            #else:
            #    setname=self.uuid+'.'+str(self.objectindex)
            #    self.objectindex += 1

            ret=pipe.hmset(setname,data)
            ret=pipe.hset(name=self.uuidlistname,key=hashkeylist,value=setname)

            ret=pipe.execute()
            #print('execute',ret)
            #print('setname',setname)
#            self.uuid=''
            #return ret
            if isinstance(setname,bytes):
                retsetname=setname.decode(encoding='utf-8')
            else:
                retsetname=setname
            print('setname',retsetname)
            return retsetname, existflg #return setname  如果existflg是1，添加新的成功，0修改成功
        except :#redis.exceptions.ResponseError:#redis.ConnectionError:
            print('Error conn')
            return False



        
    def AddObject(self,data=None):#添加一个对象
        if data==None:
            return False
        if self.TemplateKeyvalue==None:
            return self.InitTemplate(Template=None,dictdata=data)
        return self.datatoredis(dictdata=data)

    def GetObjectSize(self):#获得存储对象个数
        try:
            conn = redis.Redis(host=self.host,password=self.psw,port=self.port,db=self.db)
            if conn.ping():
                pass#print('conn ok')
            else:
                print('shawanyi')
                return False
            if self.uuidlistname==None:
                self.uuidlistname=self.uuid+'.hlist'
            ret=conn.hlen(name=self.uuidlistname)
            print('GetObjectSize:',ret)
            return ret
        except :#redis.exceptions.ResponseError:#redis.ConnectionError:
            print('Error conn')
            return False

    def DeleteObjectAll(self):#清空
        try:
            conn = redis.Redis(host=self.host,password=self.psw,port=self.port,db=self.db)
            if conn.ping():
                pass#print('conn ok')
            else:
                print('shawanyi')
                return False
            if self.uuidlistname==None:
                self.uuidlistname=self.uuid+'.hlist'
            retdlist=conn.hgetall(name=self.uuidlistname)
            print('DeleteObjectAll:',retdlist)
            pipe = conn.pipeline()
            pipe.multi()
            for v in retdlist:
                print(v)
                print(retdlist[v])
                pipe.delete(retdlist[v].decode(encoding='utf-8'))
            pipe.delete(self.uuidlistname)
            ret=pipe.execute()
            return ret
        except :#redis.exceptions.ResponseError:#redis.ConnectionError:
            print('Error conn')
            return False

    def DeleteObjectByid(self,id=''):#使用对象hash id删除对象
        if id=='':
            return False
        try:
            conn = redis.Redis(host=self.host,password=self.psw,port=self.port,db=self.db)
            if conn.ping():
                pass#print('conn ok')
            else:
                print('shawanyi')
                return False
            if self.uuidlistname==None:
                self.uuidlistname=self.uuid+'.hlist'

            delkey=''
            retdlist=conn.hgetall(name=self.uuidlistname)
            for v in retdlist:
                if retdlist[v].decode(encoding='utf-8')==id:
                    delkey=v
                    print('delkey:',delkey)
                    break
                
            pipe = conn.pipeline()
            pipe.multi()
            pipe.hdel(self.uuidlistname,delkey)
            pipe.delete(id)
            ret=pipe.execute()
            return ret
        except :#redis.exceptions.ResponseError:#redis.ConnectionError:
            print('Error conn')
            return False

    def DeleteObjectByindexKey(self,indexKey=''):#使用索引键值删除对象
        if indexKey=='':
            return False
        try:
            conn = redis.Redis(host=self.host,password=self.psw,port=self.port,db=self.db)
            if conn.ping():
                pass#print('conn ok')
            else:
                print('shawanyi')
                return False
            if self.uuidlistname==None:
                self.uuidlistname=self.uuid+'.hlist'

            delhashname=conn.hget(self.uuidlistname,indexKey)
            if delhashname==None:
                return False
            
            pipe = conn.pipeline()
            pipe.multi()
            pipe.hdel(self.uuidlistname,indexKey)
            pipe.delete(delhashname)
            ret=pipe.execute()
            return ret
        except :#redis.exceptions.ResponseError:#redis.ConnectionError:
            print('Error conn')
            return False

    def GetObjectKVlist(self):#获得索引hash里 索引key+对象id列表
        try:
            conn = redis.Redis(host=self.host,password=self.psw,port=self.port,db=self.db)
            if conn.ping():
                pass#print('conn ok')
            else:
                print('shawanyi')
                return False
            if self.uuidlistname==None:
                self.uuidlistname=self.uuid+'.hlist'
            retkvl={}
            retdlist=conn.hgetall(name=self.uuidlistname)
            for v in retdlist:
                retkvl.setdefault(v.decode(encoding='utf-8'),retdlist[v].decode(encoding='utf-8'))
            return retkvl
        except :#redis.exceptions.ResponseError:#redis.ConnectionError:
            print('Error conn')
            return False

    def GetObjectindexKeylist(self):#获得索引键列表
        try:
            conn = redis.Redis(host=self.host,password=self.psw,port=self.port,db=self.db)
            if conn.ping():
                pass#print('conn ok')
            else:
                print('shawanyi')
                return False
            if self.uuidlistname==None:
                self.uuidlistname=self.uuid+'.hlist'
            retkl=[]
            retdlist=conn.hgetall(name=self.uuidlistname)
            for v in retdlist:
                retkl.append(v.decode(encoding='utf-8'))
            return retkl
        except :#redis.exceptions.ResponseError:#redis.ConnectionError:
            print('Error conn')
            return False
            
    def GetObjectObjectlist(self):#获得对象hash name 列表
        try:
            conn = redis.Redis(host=self.host,password=self.psw,port=self.port,db=self.db)
            if conn.ping():
                pass#print('conn ok')
            else:
                print('shawanyi')
                return False
            if self.uuidlistname==None:
                self.uuidlistname=self.uuid+'.hlist'
            retkl=[]
            retdlist=conn.hgetall(name=self.uuidlistname)
            for v in retdlist:
                retkl.append(retdlist[v].decode(encoding='utf-8'))
            return retkl
        except :#redis.exceptions.ResponseError:#redis.ConnectionError:
            print('Error conn')
            return False

    def Getfordict(self,jsdata=None,jskeyvalue=None):
        if jsdata==None or jskeyvalue==None:
            return False
        retdict={}
        for key,value in jsdata.items():
            if isinstance(value,dict):
                retvalue=self.Getfordict(jsdata=value,jskeyvalue=jskeyvalue)
            elif isinstance(value,list):
                retvalue=self.Getforlist(jsdata=value,jskeyvalue=jskeyvalue)
            else:
                
                usekey, usetype=value.split(':')
                if usetype=='int':
                    retvalue=int(jskeyvalue[usekey.encode(encoding='utf-8')])
                elif usetype=='float':
                    retvalue=float(jskeyvalue[usekey.encode(encoding='utf-8')])
                elif usetype=='string':
                    retvalue=jskeyvalue[usekey.encode(encoding='utf-8')].decode(encoding='utf-8')
                else:
                    retvalue=jskeyvalue[usekey.encode(encoding='utf-8')].decode(encoding='utf-8')
                #jsdata[usekey]=setvalue
            retdict.setdefault(key,retvalue)
        return retdict

    def Getforlist(self,jsdata=None,jskeyvalue=None):
        if jsdata==None or jskeyvalue==None:
            return False
        retlist=[]
        for v in jsdata:
            if isinstance(v,dict):
                retvalue=self.Getfordict(jsdata=v,jskeyvalue=jskeyvalue)
            elif isinstance(v,list):
                retvalue=self.Getforlist(jsdata=v,jskeyvalue=jskeyvalue)
            else:
                usekey, usetype=v.split(':')
                if usetype=='int':
                    retvalue=int(jskeyvalue[usekey.encode(encoding='utf-8')])
                elif usetype=='float':
                    retvalue=float(jskeyvalue[usekey.encode(encoding='utf-8')])
                elif usetype=='string':
                    retvalue=jskeyvalue[usekey.encode(encoding='utf-8')].decode(encoding='utf-8')
                else:
                    retvalue=jskeyvalue[usekey.encode(encoding='utf-8')].decode(encoding='utf-8')
                #jsdata[index]=setvalue
            retlist.append(retvalue)
        return retlist
        
    def GetObjectContentByName(self,name=''):#使用对象hash name值返回对象
        if name=='':
            return False
        if self.TemplateKeyvalue==None:
            return False
        #retTemplate=deepcopy(self.TemplateKeyvalue)
        #retdlist={}
        try:
            conn = redis.Redis(host=self.host,password=self.psw,port=self.port,db=self.db)
            if conn.ping():
                pass#print('conn ok')
            else:
                print('shawanyi')
                return False
            retdlist=conn.hgetall(name=name)
        except :#redis.exceptions.ResponseError:#redis.ConnectionError:
            print('Error conn')
            return False
        if len(retdlist)<=0:
            return False
        #print('get:',retdlist)
        #print('getusr:',retTemplate)
        
        if isinstance(self.TemplateKeyvalue,dict):
            retid=self.Getfordict(jsdata=self.TemplateKeyvalue,jskeyvalue=retdlist)
        elif isinstance(self.TemplateKeyvalue,list):
            retid=self.Getforlist(jsdata=self.TemplateKeyvalue,jskeyvalue=retdlist)
        else:
            return False
        #print('GetObjectContentByName:',retTemplate)
        #return retTemplate
        print(name,'GetObjectContentByName:',retid)
        return retid

    def GetObjectContentByIndexValue(self,indexvalue=''):#使用对象索引键值返回对象内容
        if indexvalue=='':
            return False
        if self.TemplateKeyvalue==None:
            return False
        try:
            conn = redis.Redis(host=self.host,password=self.psw,port=self.port,db=self.db)
            if conn.ping():
                pass#print('conn ok')
            else:
                print('shawanyi')
                return False
            if self.uuidlistname==None:
                self.uuidlistname=self.uuid+'.hlist'

            gethashname=conn.hget(self.uuidlistname,indexvalue)
            if gethashname==None:
                return False
            return self.GetObjectContentByName(name=gethashname)
        except :#redis.exceptions.ResponseError:#redis.ConnectionError:
            print('Error conn')
            return False
       

def testmain():
    tc=DataObjectJSRedisClass(host='127.0.0.1',psw='123456',port=6379,indexkey='5')
    jsstr='''{"我": [1, 2], "2": {"1": 21, "2": 33}, "3": "这样","4":[{"t":123,"d":234},{"t":567,"d":789}],"5":"ok1"}'''
    jsstr1='''{"1": [1, 2], "2": {"1": 21, "2": 33}, "3": 123,"4":[{"t":123,"d":234},{"t":567,"d":789}],"5":"ok2"}'''
    jsstr2='''{"1": [1, 2], "2": {"1": 21, "2": 33}, "3": 123,"4":[{"t":123,"d":234},{"t":567,"d":789}],"5":"ok3"}'''
    jsstr3='''{"1": [1, 2], "2": {"1": 21, "2": 33}, "3": 123,"4":[{"t":123,"d":234},{"t":567,"d":789}],"5":"ok4"}'''

    #tc.InitTemplate(Template=None,dictdata=jsstr)
    tc.AddObject(data=jsstr)
    tc.GetObjectSize()
    #tc.InitTemplate(Template=None,dictdata=jsstr1)
    tc.AddObject(data=jsstr1)
    tc.GetObjectSize()
    #tc.InitTemplate(Template=None,dictdata=jsstr2)
    tc.AddObject(data=jsstr2)
    tc.GetObjectSize()
    #tc.InitTemplate(Template=None,dictdata=jsstr3)
    tc.AddObject(data=jsstr3)
    tc.GetObjectSize()

    print('GetObjectObjectlist:',tc.GetObjectObjectlist())#获得对象hash name 列表
    print('GetObjectindexKeylist:',tc.GetObjectindexKeylist())#获得索引键列表
    print('GetObjectKVlist:',tc.GetObjectKVlist())#获得索引hash里 索引key+对象id列表

    #tc.GetObjectContentByName(name='12345678901234567890123456789012.0')
    #tc.GetObjectContentByName(name='12345678901234567890123456789012.5')
    #tc.GetObjectContentByName(name='12345678901234567890123456789012.3')
    #tc.GetObjectContentByName(name='12345678901234567890123456789012.2')
    #tc.GetObjectContentByName(name='12345678901234567890123456789012.1')


    tc.GetObjectContentByIndexValue(indexvalue="ok3")
    #tc.DeleteObjectByid(id='12345678901234567890123456789012.0')
    print(tc.DeleteObjectByindexKey(indexKey="ok3"))

    tc.DeleteObjectAll()


    return
if __name__ == '__main__':
    testmain()
