# -*- coding: utf-8 -*-
"""
   Description :
   Author :       sky
   date：          
"""
__author__ = 'sky'
from selenium import webdriver


def scroll_foot(driver):
    """
    滚动条拉到底部
    :param driver:
    :return:
    """
    js = ""
    # 如何利用chrome驱动或phantomjs抓取
    if driver.name == "chrome" or driver.name == 'phantomjs':
        js = "var q=document.body.scrollTop=100000"
    # 如何利用IE驱动抓取
    elif driver.name == 'internet explorer':
        js = "var q=document.documentElement.scrollTop=100000"
    driver.execute_script(js)


def get_driver():
    """
    :return:
    """
    return webdriver.PhantomJS('/Users/tian/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs')