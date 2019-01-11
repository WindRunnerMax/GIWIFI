#!/usr/bin/python 
# -*- coding: utf-8 -*-

import requests
import re
import threading
import os
import random
import socket
import struct
import time
from lxml import etree
import json
import random

###############################
phone = "12312312311"     #账号
password = "123123123"    #密码
###############################


class Giwifi(object):
    """docstring for Giwifi"""
    def __init__(self,phone,password):
        super(Giwifi, self).__init__()
        self.phone = phone
        self.password = password

    HEADERS = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36',
    'Referer': 'http://10.13.0.1',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh-TW;q=0.8,zh;q=0.6,en;q=0.4,ja;q=0.2',
    'cache-control': 'max-age=0'
    }
    
    def GetInfo(self,session):
        reqUrl = "http://login.gwifi.com.cn/cmps/admin.php/api/login/"
        req = session.get(reqUrl,headers=self.HEADERS)
        s = req.url.split("?")
        if s[0] != "http://down.gwifi.com.cn" :
            print("未连接GIWIFI或已登陆GIWIFI")
            exit(0)
        reUrl = reqUrl + "?" + s[1]
        reqReq = session.get(reUrl,headers=self.HEADERS)
        return req.url,reqReq.text

    def DitEn(self, url = "",session = ""):
        url = url.split("?")[1]
        urlList = url.split("&")
        dit = {}
        for x in urlList:
            path = x.split("=")
            dit[path[0]] = path[1]
        return dit

    def GetStatus(self,dit,html,session):
        url = re.search(r"http://"+dit['gw_address']+":"+dit['gw_port']+"/wifidog/get_auth_state.*", html)
        url = url.group(0)[:-3]
        url = url + "&callback=''"
        res = session.get(url,headers = self.HEADERS)
        resp = json.loads(res.text[3:-1])
        return json.loads(resp['data'])

    def ReqLogin(self,dit,html,session):
        s = etree.HTML(html)
        sign = s.xpath('//*[@id="frmLogin"]/ul/input[20]')
        pageTime = s.xpath('//*[@id="page_time"]')
        authStatus = self.GetStatus(dit,html,session)
        params = {
        'name' : self.phone,
        'password' : self.password,
        'gw_id' : dit['gw_id'],
        'gw_address' : dit['gw_address'],
        'gw_port' : dit['gw_port'],
        'mac' : dit['mac'],
        'page_time' : pageTime[0].get("value"),
        'client_mac' : authStatus['client_mac'],
        'url' : dit['url'],
        'station_sn' : authStatus['station_sn'],
        'acsign' : authStatus['sign'],
        'sign' : sign[0].get("value"),
        'station_cloud' : 'login.gwifi.com.cn',
        'apmac' : dit['apmac'],
        'btype' : 'pc',
        'suggest_phone' : '400-038-5858',
        'contact_phone' : '400-038-5858',
        'logout_reason' : '0',
        'online_time' : '0',
        'access_type' : authStatus['access_type'],
        'devicemode' : '',
        'user_agent' : '',
        'lastaccessurl' : ''
        }
        return params

    def PostLogin(self,data,session):
        # print(data)
        ran = random.randint(100,999)
        url = 'http://login.gwifi.com.cn/cmps/admin.php/api/loginaction?round=' + str(ran)
        status = session.post(url , data=data, timeout=5 ,headers = self.HEADERS)
        s = json.loads(status.text)
        print(s['info'])
        if s['status'] == 1:
            status = session.get(s['info'],headers=self.HEADERS,allow_redirects=False)
            url = s['info'].split("?")[1].split("&")[0]
            url =  "http://login.gwifi.com.cn/cmps/admin.php/api/portal/?gw_id="+data['gw_id']+"&"+url+"&apmac="+data['apmac']+"&ssid="
            portal = session.get(url,headers = self.HEADERS)
            url =  "http://login.gwifi.com.cn/cmps/admin.php/api/gw_message?message=denied&apmac="+data['apmac']+"&ssid="
            message = session.get(url,headers = self.HEADERS)
            print("登录成功")
        elif s['status'] == 0:
            print("登录失败")
        else :
            print("未知错误")
        
    def login(self):
        session = requests.Session()
        url,html = self.GetInfo(session)
        dit = self.DitEn(url = url , session = session)
        params = self.ReqLogin(dit, html, session)
        loginStatus = self.PostLogin(params ,session)


if __name__ == '__main__':
    G = Giwifi(phone,password)
    G.login()
