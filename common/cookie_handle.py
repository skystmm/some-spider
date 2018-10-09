# -*- coding: utf-8 -*-
"""
   Description :
   Author :       sky
   date：          
"""
__author__ = 'sky'

from persist_data.redis_client import *
import json

cookie_key = "cur_cookie"


def get_cookies_local(driver):
    """
    get login cookies
    :param driver:
    :return:
    """
    cookies = driver.get_cookies()
    return cookies


def get_cookies_redis(driver):
    """
    get cookies and store to redis
    :param driver:
    :return:
    """
    cookies = driver.get_cookies()
    client.set("cur_cookie", json.dumps(cookies), 60 * 30)


def set_cookies(driver, cookies):
    """
    set  cookies to a new driver
    :param driver:
    :param cookies:
    :return:
    """
    driver.delete_all_cookies()
    for cookie in cookies:
        driver.add_cookie(cookie)


def set_cookies_by_redis(driver):
    """
    get cookie from redis ,then set it to driver
    :param driver:
    :return:
    """
    cookies = client.get("cur_cookie")
    if cookies is None:
        raise Exception("login info expired,please re-login")
    cookies = json.loads(cookies)
    for cookie in cookies:
        driver.add_cookie(cookie)


def store_cookie(cookie):
    client.set(cookie_key,json.dumps(cookie), 60 * 30)


def get_cookie():
    cookie = client.get(cookie_key)
    client.set(cookie_key, cookie, 60 * 30)
    return cookie


def parse_cookie(cookie_str):
    """
    cookie 转换方法
    :param cookie_str:
    :return:
    """
    result = ""
    if type(cookie_str) == str:
        li = cookie_str.split(";")
        for s in li:
            if "," in s:
                target = s[s.rfind(",")+1:]
                value = str(target).strip()
                result += value + ";"
            else:
                result += s + ";"
    return result
