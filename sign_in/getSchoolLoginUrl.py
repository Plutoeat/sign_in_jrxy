# !/usr/bin/python
# -*- coding:utf-8 -*-
# @author   : GaiusPluto
# @time     : 2022/1/23 1:19
# @version  : 1.0
from urllib.parse import urlparse

import requests

from Config import logger


def getlogin(__school_id):
    try:
        data = {}
        res = requests.get('https://mobile.campushoy.com/v6/config/guest/tenant/info?ids={}'.format(__school_id))
        if res == "":
            # TODO send_email
            logger.debug("获取学校登录链接: 学校并没有申请入驻今日校园平台")
            exit(-1)
        data['ampUrl'] = res.json()['data'][0]['ampUrl']
        data['host'] = urlparse(data['ampUrl']).hostname
        if res.json()['data'][0]['joinType'] == 'NOTCLOUD':
            # TODO 完善不开放云端系统登录 and send_email
            logger.debug('获取学校登录链接: 暂不支持不开放云端系统的学校使用，请自行尝试或联系作者尽快更新')
            exit(-1)
        if 'campusphere' in data['ampUrl'] or 'cpdaily' in data['ampUrl']:
            logger.info({
                'id': res.json()['data'][0]['id'],
                'name': res.json()['data'][0]['name'],
                'joinType': res.json()['data'][0]['joinType'],
                'idsUrl': res.json()['data'][0]['idsUrl'],
                'ampUrl': res.json()['data'][0]['ampUrl'],
            })
            return data
        else:
            # TODO 完善使用ampUrl2登录 and send_email
            logger.debug('获取学校登录链接: 暂不支持暂不支持ampUrl2登录方式，请自行尝试或联系作者尽快更新')
            exit(-1)
    except requests.ConnectionError or requests.HTTPError:
        # TODO 完善使用ampUrl2登录 and send_email
        logger.debug('获取学校登录链接: 调用接口过多或已失效')
        exit(-1)


def run02():
    # 今日校园获取id的接口有连接限制，这里直接写上学校id
    from sign_in.getSchoolId import run01
    school_id = run01()
    # 大连大学id
    # school_id = 'dbbbb15d-e6ed-423b-8631-3b899640d1f8'
    logger.info('获取学校登录链接: 正在获取学校登录链接')
    _data = getlogin(school_id)
    logger.info('获取学校登录链接: 成功获取学校登录链接列表-' + str(_data))
    return _data


if __name__ == '__main__':
    # 用于调试，请勿调用
    __data = run02()
