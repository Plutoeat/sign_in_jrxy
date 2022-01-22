# !/usr/bin/python
# -*- coding:utf-8 -*-
# @author   : GaiusPluto
# @time     : 2022/1/23 1:19
# @version  : 1.0
import json

import requests

from config import logger


def get_schoollist(url):
    r = requests.get(url, timeout=5)
    r.encoding = r.apparent_encoding
    return r.json()


def get_url(data: dict, school_id: str):
    items = data['data']
    for item in items:
        if item['id'] == school_id:
            if item['joinType'] == 'NONE':
                logger.info(item['name'] + '未加入今日校园')
                exit(-1)
            return {'id': school_id, 'name': item['name'], 'tenantCode': item['tenantCode'], 'idsUrl': item['idsUrl'],
                    'appId': item['appId']}
        logger.info({'name': item['name'], 'joinType': item['joinType']})
    logger.debug('未找到该校信息，请检查学校名称是否错误')


def run02():
    with open('Data.json', 'r', encoding='utf-8') as f:
        url = json.load(f)['data']['getSchoolLoginUrl']['url']
    from getSchoolId import run01
    school_id = run01()
    data = get_url(get_schoollist(url), school_id)
    return data
