import json
import requests
from requests.auth import HTTPBasicAuth

'''
返回错误码
错误码	备注
0	成功
101	badrpc
102	未知错误
103	用户名密码错误
104	用户名密码不能为空
105	删除的用户不存在
106	admin用户不能删除
107	请求参数缺失
108	请求参数类型错误
109	请求参数不是json类型
110	插件已经加载，不能重复加载
111	插件已经卸载，不能重复卸载
112	用户不在线
113	用户已经存在
114	旧密码错误
115     认证错误
116     运行错误
'''
class EMQAPIClass(object):
    def __init__(self,host='192.168.1.112',username='admin',pwd='shuiJing1'):
        self.host=host
        self.usrname=username
        self.pwd=pwd

        self.port_ver=':8080/api/v2/'
        self.isauth=False

        self.errAuth={"code":115,"message":"Auth error"}
        self.err={"code":116,"message":"run error"}

    def UsedAuth(self):
        if self.isauth:
            return self.isauth
        ret=self.AuthUser(username='testname',psw='567890')
        #print(ret.text)
        #print('[[[[[[[')
        data=json.loads(ret.text)
        if data["code"]==0:
            self.isauth=True
        else:
            return False
        return self.isauth
        
    def GetAllNodesInfo(self):#获取全部节点的基本信息
        if self.UsedAuth() == False:
            return self.errAuth
        gcurl='http://'+self.host+self.port_ver+'management/nodes'
        try:
            response=requests.get(url=gcurl,auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def GetNodeInfo(self,nodename=''):#获取指定节点的基本信息
        if self.UsedAuth() == False:
            return self.errAuth
        gcurl='http://'+self.host+self.port_ver+'management/nodes/'+nodename
        try:
            response=requests.get(url=gcurl,auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def GetNodeClientsList(self,nodename=''):#获取指定节点的客户端连接列表
        if self.UsedAuth() == False:
            return self.errAuth
        gcurl='http://'+self.host+self.port_ver+'nodes/'+nodename+'/clients?curr_page=1&page_size=20'
        try:
            response=requests.get(url=gcurl,auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def GetNodeClientInfo(self,nodename='',client_id=''):#获取节点指定客户端连接的信息
        if self.UsedAuth() == False:
            return self.errAuth
        gcurl='http://'+self.host+self.port_ver+'nodes/'+nodename+'/clients/'+client_id
        try:
            response=requests.get(url=gcurl,auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def GetNodeSessionsList(self,nodename=''):#获取指定节点的会话列表
        if self.UsedAuth() == False:
            return self.errAuth
        gcurl='http://'+self.host+self.port_ver+'nodes/'+nodename+'/sessions?curr_page=1&page_size=20'
        try:
            response=requests.get(url=gcurl,auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def GetNodeClientSessionsInfo(self,nodename='',client_id=''):#获取节点上指定客户端的会话信息
        if self.UsedAuth() == False:
            return self.errAuth
        gcurl='http://'+self.host+self.port_ver+'nodes/'+nodename+'/sessions/'+client_id
        try:
            response=requests.get(url=gcurl,auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def GetNodeSubscriptionsList(self,nodename=''):#获取某个节点上的订阅列表
        if self.UsedAuth() == False:
            return self.errAuth
        gcurl='http://'+self.host+self.port_ver+'nodes/'+nodename+'/subscriptions?curr_page=1&page_size=20'
        try:
            response=requests.get(url=gcurl,auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def GetNodeClientSubscriptionInfo(self,nodename='',client_id=''):#获取节点上指定客户端的订阅信息
        if self.UsedAuth() == False:
            return self.errAuth
        gcurl='http://'+self.host+self.port_ver+'nodes/'+nodename+'/subscriptions/'+client_id
        try:
            response=requests.get(url=gcurl,auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def Publish(self,topic='',payload='',qos=0,retain=False,client_id=''):#发布消息
        if self.UsedAuth() == False:
            return self.errAuth
        postpublish=gcurl='http://'+self.host+self.port_ver+'mqtt/publish'
        postpublish_src={'topic':topic,'payload':payload,'qos':qos,'retain':retain,'client_id':client_id}
        try:
            response=requests.post(url=postpublish,data=json.dumps(postpublish_src),auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def Subscribe(self,topic='',qos=0,client_id=''):#创建订阅
        if self.UsedAuth() == False:
            return self.errAuth
        postpublish=gcurl='http://'+self.host+self.port_ver+'mqtt/subscribe'
        postpublish_src={'topic':topic,'qos':qos,'client_id':client_id}
        try:
            response=requests.post(url=postpublish,data=json.dumps(postpublish_src),auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def Unsubscribe(self,topic='',client_id=''):#取消订阅
        if self.UsedAuth() == False:
            return self.errAuth
        postpublish=gcurl='http://'+self.host+self.port_ver+'mqtt/unsubscribe'
        postpublish_src={'topic':topic,'client_id':client_id}
        try:
            response=requests.post(url=postpublish,data=json.dumps(postpublish_src),auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def GetUsersList(self):#获取管理用户列表
        if self.UsedAuth() == False:
            return self.errAuth
        gcurl='http://'+self.host+self.port_ver+'users'#':8080/api/v2/users'
        try:
            response=requests.get(url=gcurl,auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def AddUser(self,username='admin',psw='',tags='user'):#添加管理用户
        if self.UsedAuth() == False:
            return self.errAuth
        postpublish=gcurl='http://'+self.host+self.port_ver+'users'#':8080/api/v2/users'
        postpublish_src={'username':username,'password':psw,'tags':tags}
        try:
            response=requests.post(url=postpublish,data=json.dumps(postpublish_src),auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def ModifyUser(self,username='admin',tags='user'):#修改管理用户信息
        if self.UsedAuth() == False:
            return self.errAuth
        postpublish=gcurl='http://'+self.host+self.port_ver+'users/'+username#':8080/api/v2/users/'+username
        postpublish_src={'tags':tags}
        try:
            response=requests.put(url=postpublish,data=json.dumps(postpublish_src),auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def DeleteUser(self,username=''):#删除管理用户
        if self.UsedAuth() == False:
            return self.errAuth
        postpublish=gcurl='http://'+self.host+self.port_ver+'users/'+username#':8080/api/v2/users/'+username
        try:
            response=requests.delete(url=postpublish,auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def AuthUser(self,username='admin',psw=''):#认证管理用户
        postpublish=gcurl='http://'+self.host+self.port_ver+'auth'#':8080/api/v2/auth'
        postpublish_src={'username':username,'password':psw}
        try:
            response=requests.post(url=postpublish,data=json.dumps(postpublish_src),auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def ChangeUserPwd(self,username='admin',new_pwd='',old_pwd=''):#修改管理用户密码
        if self.UsedAuth() == False:
            return self.errAuth
        #postpublish=gcurl='http://'+self.host+':8080/api/v2/change_pwd/'+username
        postpublish=gcurl='http://'+self.host+self.port_ver+'change_pwd/'+username
        postpublish_src={'new_pwd':new_pwd,'old_pwd':old_pwd}
        try:
            response=requests.put(url=postpublish,data=json.dumps(postpublish_src),auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def GetClusteringClientInfo(self,client_id=''):#获取集群内指定客户端的信息
        if self.UsedAuth() == False:
            return self.errAuth
        #gcurl='http://'+self.host+':8080/api/v2/clients/'+client_id
        gcurl='http://'+self.host+self.port_ver+'clients/'+client_id
        try:
            response=requests.get(url=gcurl,auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def DeleteClusteringClientInfo(self,client_id=''):#断开集群内指定客户端连接
        if self.UsedAuth() == False:
            return self.errAuth
        #gcurl='http://'+self.host+':8080/api/v2/clients/'+client_id
        gcurl='http://'+self.host+self.port_ver+'clients/'+client_id
        try:
            response=requests.delete(url=gcurl,auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def CleanAclCacheClusteringClient(self,client_id='',topic=''):#清除集群内指定客户端的ACL缓存
        if self.UsedAuth() == False:
            return self.errAuth
        #gcurl='http://'+self.host+':8080/api/v2/clients/'+client_id+'/clean_acl_cache'
        gcurl='http://'+self.host+self.port_ver+'clients/'+client_id+'/clean_acl_cache'
        postpublish_src={'topic':topic}
        try:
            response=requests.put(url=gcurl,auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def GetClusteringClientSubscriptionsInfo(self,client_id=''):#获取集群内指定客户端的订阅信息
        if self.UsedAuth() == False:
            return self.errAuth
        #gcurl='http://'+self.host+':8080/api/v2/subscriptions/'+client_id
        gcurl='http://'+self.host+self.port_ver+'subscriptions/'+client_id
        try:
            response=requests.get(url=gcurl,auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def GetClusteringRoutes(self):#获取集群路由表
        if self.UsedAuth() == False:
            return self.errAuth
        gcurl='http://'+self.host+self.port_ver+'routes?curr_page=1&page_size=20'
        try:
            response=requests.get(url=gcurl,auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def GetClusteringTopicRoutes(self,topic=''):#获取集群内指定主题的路由信息
        if self.UsedAuth() == False:
            return self.errAuth
        #gcurl='http://'+self.host+':8080/api/v2/routes/'+topic
        gcurl='http://'+self.host+self.port_ver+'routes/'+topic
        try:
            response=requests.get(url=gcurl,auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

    def GetClusteringClientsessionsInfo(self,client_id=''):#获取集群内指定客户端的会话信息
        if self.UsedAuth() == False:
            return self.errAuth
        #gcurl='http://'+self.host+':8080/api/v2/sessions/'+client_id
        gcurl='http://'+self.host+self.port_ver+'sessions/'+client_id
        try:
            response=requests.get(url=gcurl,auth=HTTPBasicAuth(self.usrname,self.pwd))
            return response
        except:
            return self.err

        

def testuser():
    e1=EMQAPIClass(host='192.168.1.112',username='admin',pwd='shuiJing1')
    ret0=e1.GetUsersList()
    print(ret0.text)
    #ret1=e1.AddUser(username='testname',psw='123456',tags='user')
    #print(ret1.text)
    #ret2=e1.ModifyUser(username='testname',tags='admin')
    #print(ret2.text)
    #ret3=e1.DeleteUser(username='testname')
    #print(ret3.text)
    ret4=e1.AuthUser(username='testname',psw='567890')
    print(ret4.text)
    ret5=e1.ChangeUserPwd(username='testname',new_pwd='567890',old_pwd='123456')
    print(ret5.text)
    
def testnodeapi():
    e=EMQAPIClass(host='192.168.1.112',username='admin',pwd='shuiJing1')
    #r=e.UsedAuth()
    #print(r)
    result=e.GetAllNodesInfo()#host='192.168.1.112',username='admin',pwd='shuiJing1')
    print(result.text)
    print('---------------------------------------------------------------------')
    
    data=json.loads(result.text)
    print(data['code'])
    for v in data['result']:
        print('nodename:', v['name'])
        ret0=e.GetNodeInfo(nodename=v['name'])
        print(ret0.text)
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++')
        ret1=e.GetNodeClientsList(nodename=v['name'])
        print(ret1.text)
        data0=json.loads(ret1.text)
        for v1 in data0['result']["objects"]:
            print ('client-id:', v1['client_id'])
            ret2=e.GetNodeClientInfo(nodename=v['name'],client_id=v1['client_id'])
            print (ret2.text)
            print('----------------------------------------------')
            ret4=e.GetNodeClientSessionsInfo(nodename=v['name'],client_id=v1['client_id'])
            print(ret4.text)
            print('================================================')
            ret5=e.GetNodeSubscriptionsList(nodename=v['name'])
            print(ret5.text)
            print('--------------------------------------------')
            ret6=e.GetNodeClientSubscriptionInfo(nodename=v['name'],client_id=v1['client_id'])
            print(ret6.text)
            print('++++++++===========================================++++')

            ret7=e.Publish(topic='test',payload='www',qos=1,retain=False,client_id=v1['client_id'])
            print(ret7.text)
            #ret8=e.Subscribe(topic='testApi',qos=1,client_id=v1['client_id'])
            #print(ret8.text)
            #ret9=e.Unsubscribe(topic='testApi',client_id=v1['client_id'])
            #print(ret9.text)
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++')
        ret3=e.GetNodeSessionsList(nodename=v['name'])
        print (ret3.text)
    
if __name__ == '__main__':
    testnodeapi()
    testuser()
