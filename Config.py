# !/usr/bin/python
# -*- coding:utf-8 -*-
# @author   : GaiusPluto
# @time     : 2022/1/23 0:59
# @version  : 1.0
import logging
from logging import config

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("jrxy")
