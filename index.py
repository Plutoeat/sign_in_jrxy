# !/usr/bin/python
# -*- coding:utf-8 -*-
# @author   : GaiusPluto
# @time     : 2022/1/24 0:46
# @version  : 1.0

# 作者君联系方式
# @email    : spaceprivate@163.com

from sign_in.login import run
def handler(*args):
    run()
    return "hello world!"

handler()