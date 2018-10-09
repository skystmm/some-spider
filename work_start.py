# -*- coding: utf-8 -*-
"""
   Description :
   Author :       sky
   date：          
"""
__author__ = 'sky'


import logging
from common.common import config
from base import core

if __name__ == '__main__':
    user_info = config.load_login_config()
    worker_info = config.load_worker_config()

    logging.debug("worker pool start ")
    core.start_linster(worker_info["threadCount"], worker_info["coroutineCount"])

    logging.debug("app start")