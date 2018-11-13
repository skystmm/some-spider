# -*- coding: utf-8 -*-
"""
   Description :  利用redis的队列进行分布式数据爬取
   Author :       sky
   date：          
"""
__author__ = 'sky'
import json
from persist_data.redis_client import client
from gevent import pool
from common import phatomjs_common
from common import cookie_handle
from renren import renren
from concurrent.futures import ThreadPoolExecutor


def start_linster(thread_count, coroutine_count):
    """
    线程池进行Redis任务监听和处理
    :return:
    """
    if thread_count < 1:
        raise Exception(" init thread count must gather then 0")
    with ThreadPoolExecutor(thread_count) as executor:
        for i in range(thread_count):
            executor.submit(task_linster, coroutine_count)


def task_linster(coroutine_count):
    """
    监听任务队列，并获取任务
    :return:
    """
    worker_pool = pool.Pool(coroutine_count)
    while True:
        #change use blpop
        #info = client.blpop("friends")
        info = client.lpop("friends")
        if info is not  None:
            rs = renren.RenrenSpider()
            queryInfo = info.decode("utf-8")
            queryInfo = json.loads(queryInfo)
            worker_pool.spawn(rs.get_friends, queryInfo)
            worker_pool.join()


def friend_handler(info):
    """
    获取好友信息handler
    :param info:
    :return:
    """
    driver = phatomjs_common.get_driver()
    driver.get("http://renren.com")
    cookie_handle.set_cookies_by_redis(driver)
    driver.refresh()
    spider = renren.RenrenSpider()
    fid = info['friendId']
    relation = info['relationGen'] + 1
    driver.get(spider.url % fid)
    if relation < 3:
        spider.get_friends(driver, relation)
    driver.quit()
