# !/usr/bin/python
# -*- coding:utf-8 -*-
# @author   : GaiusPluto
# @time     : 2022/1/26 14:59
# @version  : 1.0

import json
import urllib.parse

import requests

headers = {'Content-type': 'application/x-www-form-urlencoded'}
data = json.load(open('config/config.json','r', encoding='utf-8'))['data']
def send(title, desp):
    if data['send_msg']:
        if len(data['SendKey'])!=0:
            base_url = 'https://sctapi.ftqq.com/'+data['SendKey']+'.send?'
            params = {'title':title, 'desp':desp}
            url = base_url + urllib.parse.urlencode(params)
            requests.get(url, headers=headers)
        else:
            print('your sendkey is not right')
