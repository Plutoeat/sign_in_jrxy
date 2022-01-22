# !/usr/bin/python
# -*- coding:utf-8 -*-
# @author   : GaiusPluto
# @time     : 2022/1/22 16:33
# @version  : 1.0
import json
import time
import requests
from config import logger


def get_json(url):
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
    except requests.HTTPError:
        logger.debug('获取学校列表的网址有误,请自行修改或联系作者')
        exit(-1)
    except requests.ConnectionError:
        logger.debug('获取学校列表的网址有误,请自行修改或联系作者')
        exit(-1)


def clean_data(data: dict, school_list: list):
    for item in school_list:
        if item['sectionName'] == data['sectionName']:
            for item_school in item['datas']:
                if item_school['name'] == data['name']:
                    return item_school['id']
    logger.debug('请仔细检查Data.json文件的getSchoolId下的sectionName和name是否配置正确，或者你的学校未加入今日校园')
    exit(-1)


def run01():
    data = json.load(open("Data.json", "r", encoding="utf-8"))['data']['getSchoolId']
    school_list = get_json(data['url'])
    schoolid = clean_data(data, school_list)
    return schoolid

# main()
