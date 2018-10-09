# -*- coding: utf-8 -*-
"""
   Description :
   Author :       sky
   date：          
"""
__author__ = 'sky'

import logging
from renren import renren
from common.common import config
from base import core

if __name__ == '__main__':
    user_info = config.load_login_config()
    worker_info = config.load_worker_config()

    logging.debug("renren spider start")
    start_point = renren.RenrenSpider()
    start_point.login(user_info['userName'], user_info["passwd"])
    start_point.get_token()
    start_point.get_friends()

    logging.debug("worker pool start ")
    core.start_linster(worker_info["threadCount"], worker_info["coroutineCount"])

    logging.debug("app start")
