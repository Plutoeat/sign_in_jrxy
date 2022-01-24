# !/usr/bin/python
# -*- coding:utf-8 -*-
# @author   : GaiusPluto
# @time     : 2022/1/22 16:33
# @version  : 1.0
import json
import time
import requests
from Config import logger


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
        logger.debug('获取学校ID: 当前接口不可用, 请稍后重试或联系作者')
        # TODO send_email()
        exit(-1)
    except requests.ConnectionError:
        logger.debug('获取学校ID: 当前接口不可用, 请稍后重试或联系作者')
        # TODO send_email()
        exit(-1)


def clean_data(data: dict, school_list: list):
    try:
        for item in school_list:
            if item['sectionName'] == data['sectionName']:
                for item_school in item['datas']:
                    if item_school['name'] == data['name']:
                        return item_school['id']
        logger.debug('获取学校ID: 请仔细检查Data.json文件的getSchoolId下的sectionName和name是否配置正确，或者你的学校未加入今日校园')
        # TODO send_email()
        exit(-1)
    except IndexError:
        # TODO send_email()
        logger.debug('获取学校ID: 当前接口不可用, 请稍后重试或联系作者')
        exit(-1)


def run01():
    logger.info("获取学校ID: 正在获取配置信息")
    data = json.load(open("config/config.json", "r", encoding="utf-8"))['data']['getSchoolId']
    logger.info("获取学校ID: 成功获取配置信息")
    logger.info("获取学校ID: 正在获取学校列表")
    school_list = get_json(data['url'])
    logger.info("获取学校ID: 成功获取学校列表")
    logger.info("获取学校ID: 获取学校ID中")
    __schoolid = clean_data(data, school_list)
    logger.info("获取学校ID: 成功获取学校ID-{}".format(__schoolid))
    return __schoolid


if __name__ == '__main__':
    # 用于调试，请勿调用
    schoolid = run01()
