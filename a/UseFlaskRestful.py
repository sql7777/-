# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 21:58:41 2018

@author: root
"""

import json
import requests
from requests.auth import HTTPBasicAuth

def GetUUID(host='127.0.0.1', port=6666,username='',pwd=''):
    #url='http://'+host+':'+port
    url='http://{0}:{1}/UUID'.format(host,port)
    try:
        response=requests.get(url=url,auth=HTTPBasicAuth(username,pwd))
        return response
    except:
        return None
    

if __name__ == '__main__':
    uuid=GetUUID(host='192.168.1.155')
    print(uuid.text)
