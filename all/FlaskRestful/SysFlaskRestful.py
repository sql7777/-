# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 21:58:41 2018

@author: root
"""

from flask import Flask, jsonify
from flask import make_response
from flask import request
from flask import abort
import uuid
import operator
import socket


frontuuid={'last':''}
def GetUUID():
    while(1):
        uid=uuid.uuid1()
        uids=str(uid).replace('-','')
        #print(uids)
        if operator.eq(uids, frontuuid['last']):
            continue
        frontuuid['last']=uids
        return uids

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])

def api_root():
    if request.method == 'GET':
        #return "ECHO: GET\n"
        return GetUUID()+"\n"

    elif request.method == 'POST':
        return "ECHO: POST\n"

    elif request.method == 'PUT':
        return "ECHO: PUT\n"

    elif request.method == 'DELETE':
        return "ECHO: DELETE"

@app.route('/UUID', methods=['GET'])
def api_getuuid():
    ret='UUID:{0}'.format(GetUUID())
    return ret
    #return GetUUID()+"\n"


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 80))
ip = s.getsockname()[0]

if __name__ == '__main__':
    #app.run(host='127.0.0.1', port=6666, threaded = True)
    app.run(host=ip, port=6666, threaded = True)
