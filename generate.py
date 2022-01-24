# !/usr/bin/python
# -*- coding:utf-8 -*-
# @author   : GaiusPluto
# @time     : 2022/1/24 1:56
# @version  : 1.0
import json
import os
if not os.path.exists(os.getcwd()+'\\config'):
    os.mkdir(os.getcwd()+'\\config')
if not os.path.exists(os.getcwd()+'\\log'):
    os.mkdir(os.getcwd()+'\\log')
if not os.path.isfile(os.getcwd()+'\\log\\jrxy.log'):
    with open(os.getcwd()+'\\log\\jrxy.log', 'w', encoding='utf-8') as f:
        f.write('# @author   : GaiusPluto')


if __name__ == '__main__':
    fs = input('请输入你大学的首字母: ').upper()
    print(fs)
    school_name = input('请输入你大学名字: ')
    print(school_name)
    username = input('请输入你的学号(仅支持学号): ')
    password = input('请输入你的密码: ')
    address = input('请输入你的地址: ')
    form_list = []
    flag = 1
    while True:
        title = input("输入问题"+str(flag)+"标题(建议直接复制粘贴,输入-1结束): ")
        if title == '-1':
            break
        type = input('输入问题'+str(flag)+'类型,一般回答问题为1,单选为2,多选为3,拍摄照片为4: ')
        value = input('输入问题'+str(flag)+'的默认回答: ')
        form_list.append({
          "default": {
            "title": title,
            "type": eval(type),
            "value": value
          }
        })
        flag+=1
    config = {
        "data": {
            "getSchoolId": {
                "url": "https://static.campushoy.com/apicache/tenantListSort",
                "sectionName": "{}".format(fs),
                "name": "{}".format(school_name)
            },
            "getSchoolLoginUrl": {
                "url": "https://mobile.campushoy.com/v6/config/guest/tenant/list"
            },
            "login": {
                "username": "{}".format(username),
                "password": "{}".format(password),
                "address": "{}".format(address)
            },
            "rem_form": False,
            "form": {
                "defaults": form_list
            }
        }
    }
    json.dump(config, open(os.getcwd()+'\\conf\\config.json', 'w', encoding='utf-8'))
