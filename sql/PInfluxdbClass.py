# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 21:58:41 2018

@author: root
"""

from influxdb import InfluxDBClient
import time

class PInfluxdbClass(object):
    def __init__(self,host='192.168.1.178', port=8086, username='root', password='root', database = ''):
        self.host=host
        self.port=port
        self.usrname=username
        self.pwd=password
        self.database=database

        self.client=None

    def initInfluxdb(self):
        if self.client!=None:
            return True
        self.client=InfluxDBClient(host=self.host,port=self.port, username=self.usrname, password=self.pwd, database = self.database)
        print(self.client)
        ret=self.client.create_database(self.database)
        return True

    def SaveDataToInfluxdb(self,measurement='',tags=None,fields=None):
        saveTemplate=[{
            "measurement": "",
            "tags": None,
            "fields": None
            }]
        if measurement=='' or tags==None or fields==None:
            return False
        if isinstance(tags,dict)==False or isinstance(fields,dict)==False:
            return False
        
        if self.initInfluxdb()==False:
            return False
        saveTemplate[0]["measurement"]=measurement
        saveTemplate[0]["tags"]=tags
        saveTemplate[0]["fields"]=fields
        print(saveTemplate)

        return self.client.write_points(saveTemplate)

    def GetDataFrominfluxdb(self,measurement='',tags=None,sqlstr=''):
        if sqlstr=='':
            str='select * from {0};'.format(measurement)
            return self.client.query(str)
        else:
            return self.client.query(sqlstr)


    def Test(self):
        json_body = [{
            "measurement": "cpu_load_short",
            "tags": {
                "host": "server01",
                "region": "us-west"
                },
            "fields": {
                "value": 0.64
                }
            }]
        ret=self.client.create_database(self.database)
        print('create_database:',ret)
        ret=self.client.write_points(json_body)
        print('write_points:',ret)
        ret=self.client.query('select value from cpu_load_short;')
        print("Result: {0}".format(ret))

        


if __name__ == '__main__':
    db=PInfluxdbClass(host='192.168.1.178', port=8086, username='root', password='root', database = 'testmydb')
    #db.initInfluxdb()
    #db.Test()
    db.SaveDataToInfluxdb(measurement='testtabl',tags={"save11":"savetags"},fields={"f11":"fields value"})
    print('Get:',db.GetDataFrominfluxdb(measurement='testtabl'))
