# !/usr/bin/python
# -*- coding:utf-8 -*-
# @author   : GaiusPluto
# @time     : 2022/1/22 16:33
# @version  : 1.0
import json
import time
import logging
import requests

logging.basicConfig(level=logging.INFO)

def getJson(url):
    headers = {
        'Host': 'static.campushoy.com',
        'User-Agent': '%E4%BB%8A%E6%97%A5%E6%A0%A1%E5%9B%AD/2 CFNetwork/1327.0.4 Darwin/21.2.0',
        'Cookie': 'clientType=cpdaily_student; standAlone=0'
    }
    params = {'t': "{:.6f}".format(time.time())}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=5)
        r.encoding = r.apparent_encoding
        return r.json()['data']
    except:
        raise

def cleanData(data: dict, school_list: list):
    for item in school_list:
        if item['sectionName'] == data['sectionName']:
            for item_school in item['datas']:
                if item_school['name'] == data['name']:
                    return item_school['id']
    logging.log(level=logging.INFO, msg=r'你getSchoolId的配置有误')
    exit(-1)


def main():
    data = json.load(open("Data.json", "r", encoding="utf-8"))['data']['getSchoolId']
    school_list = getJson(data['url'])
    id = cleanData(data, school_list)
    return id

main()