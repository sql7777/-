# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 21:02:58 2018

@author: root
"""

import sqlite3
from copy import deepcopy

class SqliteKVClass(object):
    def __init__(self, db='Rfidsys.db',DatasheetName='',fieldTemplate=None):
        self.db=db
        #self.conn=None
        self.DatasheetName=DatasheetName
        self.fieldTemplate=fieldTemplate
        
    def Sqlite3conndb(self):
        try:
            conn = sqlite3.connect(self.db)
            #print(conn)
            return conn
        except:
            print('conn erro')
            return None

    def Sqlite3creattabl(self,DatasheetName='',fieldTemplate=None):
        connn=self.Sqlite3conndb()
        if connn == None:
            print('Sqlite3creattabl False')
            return False
        
        if DatasheetName!='':
            tname=DatasheetName
        else:
            if self.DatasheetName!='':
                tname=self.DatasheetName
            else:
                return False
        if fieldTemplate!=None:
            field=fieldTemplate
        else:
            if self.fieldTemplate!=None:
                field=self.fieldTemplate
            else:
                return False

        if isinstance(field,dict):
            pass
        else:
            return False
        #sqlstr="create table {0} (ID INT PRIMARY KEY NOT NULL,".format(tname)
        sqlstr="create table {0} (".format(tname)
        print(sqlstr)
        for k,v in field.items():
            stemp=k+' '+v
            sqlstr+=(stemp+',')
        sqlstr=sqlstr.rstrip(',')
        sqlstr+=')'
        print(sqlstr)

        try:        
            cursor = connn.cursor()
            cursor.execute(sqlstr)
            connn.commit()
            cursor.close()
            connn.close()

            self.fieldTemplate=field
            return True
        except:
            print('----')
            return False

    def Sqlite3InsertData(self,data=None):
        connn=self.Sqlite3conndb()
        if connn == None:
            print('Sqlite3creattabl False')
            return False

        if data==None:
            return False
        if self.DatasheetName=='' or self.fieldTemplate==None:
            return False
        
        if isinstance(data,dict):
            pass
        else:
            return False
        sqlstrIn="INSERT INTO {0} (".format(self.DatasheetName)
        sqlstrV="VALUES ("
        for k,v in self.fieldTemplate.items():
            sqlstrIn+=(k+",")
            tv=data[k]
            if isinstance(tv,str):
                sqlstrV+=("\""+tv+"\""+",")
            else:
                sqlstrV+=(str(tv)+",")

        sqlstrIn=sqlstrIn.rstrip(',')
        sqlstrIn+=')'
        sqlstrV=sqlstrV.rstrip(',')
        sqlstrV+=')'

        sqlstr=sqlstrIn+sqlstrV
        try:        
            cursor = connn.cursor()
            cursor.execute(sqlstr)
            connn.commit()
            cursor.close()
            connn.close()
            return True
        except:
            print('----')
            return False

    def Sqlite3Updatedata(self,kvindex=None,data=None):
        connn=self.Sqlite3conndb()
        if connn == None:
            print('Sqlite3creattabl False')
            return False

        if data==None:
            return False
        if kvindex==None:
            return False
        if self.DatasheetName=='' or self.fieldTemplate==None:
            return False
        
        if isinstance(data,dict):
            pass
        else:
            return False
        if isinstance(kvindex,dict):
            pass
        else:
            return False
        sqlstrIn="UPDATE {0} SET ".format(self.DatasheetName)
        for k,v in self.fieldTemplate.items():
            tv=data[k]
            if isinstance(tv,str):
                sqlstrIn+=(k+" = "+"\""+tv+"\""+",")
            else:
                sqlstrIn+=(k+" = "+str(tv)+",")
                
        sqlstrIn=sqlstrIn.rstrip(',')
        sqlstrIn+=' '

        sqlstrV="WHERE "
        for ki,vi in kvindex.items():
            if isinstance(vi,str):
                sqlstrV="{0} = \"{1}\"".format(ki,vi)
            else:
                sqlstrV="{0} = {1}".format(ki,str(vi))
        sqlstr=sqlstrIn+"WHERE "+sqlstrV
            
        try:        
            cursor = connn.cursor()
            cursor.execute(sqlstr)
            connn.commit()
            cursor.close()
            connn.close()
            return True
        except:
            print('----')
            return False

    def Sqlite3Getdata(self,kvindex=None,data=None):
        connn=self.Sqlite3conndb()
        if connn == None:
            print('Sqlite3creattabl False')
            return False

        if kvindex==None:
            return False
        if self.DatasheetName=='' or self.fieldTemplate==None:
            return False
        
        if isinstance(kvindex,dict):
            pass
        else:
            return False
        sqlstrIn="SELECT "
        if data==None:
            sqlstrIn="SELECT * FROM {0} ".format(self.DatasheetName)
        else:
            if isinstance(data,dict):
                for k,v in data.items():
                    sqlstrIn+=k+","
                sqlstrIn=sqlstrIn.rstrip(',')
                sqlstrIn+=(" FROM {0} ".format(self.DatasheetName))
            else:
                return False
        sqlstrV="WHERE "
        for ki,vi in kvindex.items():
            if isinstance(vi,str):
                sqlstrV="{0} = \"{1}\"".format(ki,vi)
            else:
                sqlstrV="{0} = {1}".format(ki,str(vi))
        sqlstr=sqlstrIn+"WHERE "+sqlstrV
            
        try:        
            cursor = connn.cursor()
            cursor.execute(sqlstr)
            getdata = cursor.fetchall()
            #connn.commit()
            cursor.close()
            connn.close()

            retdata=[]

            for tablevalue in getdata:
                if data!=None:
                    tempd=deepcopy(data)
                else:
                    tempd=deepcopy(self.fieldTemplate)
                index=0
                for tk,tv in tempd.items():
                    tempd[tk]=tablevalue[index]
                    index+=1
            retdata.append(tempd)
            return retdata
        except:
            print('----')
            return False



def TestMain():
    field={'ID':'int','name':'text','old':'int'}
    data={'ID':0,'name':'hao','old':30}
    dataup={'ID':0,'name':'P','old':60}
    data1={'ID':1,'name':'haoA','old':30}
    tt=SqliteKVClass(db='Rfidsys.db',DatasheetName='testtable',fieldTemplate=field)
    print(tt.Sqlite3creattabl())
    print(tt.Sqlite3InsertData(data=data))
    print(tt.Sqlite3Getdata(kvindex={'ID':0},data=None))

    print(tt.Sqlite3InsertData(data=data1))
    print(tt.Sqlite3Updatedata(kvindex={'ID':0},data=dataup))
    print(tt.Sqlite3Getdata(kvindex={'ID':0},data=None))
    print(tt.Sqlite3Getdata(kvindex={'ID':1},data=None))

if __name__ == '__main__':
    TestMain()
