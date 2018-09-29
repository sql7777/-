# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 21:58:41 2018

@author: root
"""

import paho.mqtt.client as mqtt
import time

#HOST = "192.168.1.112"
#HOST = "127.0.0.1"
#PORT = 1883#61613
class EMQRevClass(object):
    def __init__(self,host='192.168.1.112',port=1883,username='admin',pwd='shuiJing1',client_id='',callbackMessage=None,callbackEvent=None):
        self.host=host
        self.port=port
        self.usrname=username
        self.pwd=pwd
        self.client_id=client_id
        self.topic=[]
        self.callbackMessage=callbackMessage
        self.callbackEvent=callbackEvent

        self.client=None
        self.isrun=False

    def on_connect(self,client, userdata, flags, rc):
        #print("Connected with result code "+str(rc))
        result={'connect':str(rc)}
        print(result)
        self.client.subscribe(self.topic)
        if self.callbackEvent!=None:
            self.callbackEvent(result)
            #self.callbackEvent("Connected:"+str(rc))

    def on_disconnect(self,client, userdata, rc):
        #print("Connected with result code "+str(rc))
        result={'disconnect':str(rc)}
        print(result)
        if self.callbackEvent!=None:
            self.callbackEvent(result)
            #self.callbackEvent("DisConnected:"+str(rc))

    def on_message(self,client, userdata, message):
        #print(message.topic+" "+message.payload.decode("utf-8"))
        #print(client)
        result={'topic':message.topic,'payload':message.payload.decode("utf-8")}
        print(result)
        #print("Received message '" + str(message.payload) + "' on topic '"
        #+ message.topic + "' with QoS " + str(message.qos))
        if self.callbackMessage!=None:
            self.callbackMessage(result)
            #self.callbackMessage(message.topic+":"+message.payload.decode("utf-8"))

    def on_publish(self,client, userdata, mid):
        #print("publis:"+str(mid))
        result={'publish':str(mid)}
        print(result)
        if self.callbackEvent!=None:
            self.callbackEvent(result)
            #self.callbackEvent("publis:"+str(mid))

    def on_subscribe(self,client, userdata, mid, granted_qos):
        #print("subscribe:"+str(mid)+",qos:"+str(granted_qos))
        result={'subscribe':str(mid),'qos':str(granted_qos)}
        print(result)
        if self.callbackEvent!=None:
            self.callbackEvent(result)
            #self.callbackEvent("subscribe:"+str(mid)+",qos:"+str(granted_qos))

    def on_unsubscribe(self,client, userdata, mid):
        #print("unsubscribe:"+str(mid))
        result={'unsubscribe':str(mid)}
        print(result)
        if self.callbackEvent!=None:
            self.callbackEvent(result)
            #self.callbackEvent("unsubscribe:"+str(mid))

    def on_log(self,client, userdata, level, buf):
        #print("log:"+str(level))
        result={'log':str(level),'buf':buf}
        #print(result)
        if self.callbackEvent!=None:
            self.callbackEvent(result)
            #self.callbackEvent("log:"+str(level)+":"+buf)
        
    
    def client_loop(self):
        if self.client_id=="":
            self.client_id = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        if self.client:
            self.client.reinitialise(self.client_id,clean_session=True, userdata=None)#, protocol=MQTTv311, transport="tcp")
        else:
            self.client = mqtt.Client(self.client_id,clean_session=True, userdata=None)#, protocol=MQTTv311, transport="tcp")
        self.client.username_pw_set(self.usrname,self.pwd)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect=self.on_disconnect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.on_subscribe = self.on_subscribe
        self.client.on_unsubscribe = self.on_unsubscribe
        self.client.on_log = self.on_log

        self.client.reconnect_delay_set(min_delay=1, max_delay=120)
        try:
            self.client.connect(self.host, self.port, 60)
        except:
            return False
        self.isrun=True
        self.client.loop_forever()

    def Subscribe(self,topic,qos):
        if self.client:
            self.AddTopic_(topic,qos)
            return self.client.subscribe(topic,qos)
        else:
            return 'ERR'

    def SubscribeS(self,topicS):
        if self.client:
            self.AddTopic(topicS)
            return self.client.subscribe(topicS)
        else:
            return 'ERR'

    def UnSubscribe(self,topic):
        if self.client:
            self.DelTopic(topic)
            return self.client.unsubscribe(topic)
        else:
            return 'ERR'

    def GetTopic(self):
        return self.topic

    def isTopic(self,topic):
        if isinstance(topic,tuple):
            if len(topic)!=2:
                return False
            if isinstance(topic[0],str):
                if isinstance(topic[1],int):
                    if topic[1]>=0 and topic[1]<3:
                        for v in self.topic:
                            if topic[0]==v[0]:
                                return False
                        return True
        else:
            return False

    def AddTopic_(self,topic,qos):
        return self.AddTopic((topic,qos))
        
    def AddTopic(self,topic):
        if isinstance(topic,tuple):
            if self.isTopic(topic):
                self.topic.append(topic)
        if isinstance(topic,list):
            for v in topic:
                if self.isTopic(v):
                    self.topic.append(v)
        return self.topic

    def DelTopic(self,toic):
        for v in self.topic:
            if v[0]==topic:
                try:
                    self.topic.remove(v)
                except:
                    return False
        return True
    def Reconnect(self):
        if self.isrun==True:
            return self.client.reconnect()
        
    def Close(self):
        if self.client:
            if self.isrun==True:
                self.client.disconnect()
                self.client=None
                self.isrun=False
                return True
            
if __name__ == '__main__':
    t=EMQRevClass(host='192.168.1.112',port=1883,username='admin',pwd='shuiJing1',client_id='12345678',callbackMessage=None,callbackEvent=None)
    print(t.GetTopic())
    print(t.AddTopic(('test12',1)))
    #print(t.topic)
    t.client_loop()

