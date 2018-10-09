# -*- coding: utf-8 -*-
"""
   Description :
   Author :       sky
   date：          
"""
__author__ = 'sky'
import common.phatomjs_common as ph

from persist_data import redis_client


class RenrenSeleium():
    def login(self, name, passwd):
        """
        人人网登陆
        :param name:
        :param passwd:
        :return:
        """
        driver = ph.get_driver()
        driver.set_window_size("800", "600")
        driver.get('http://renren.com')
        print("---------------***************---------------------")
        input1 = driver.find_element("id", "email")
        input1.send_keys(name)
        input2 = driver.find_element("id", "password")
        input2.send_keys(passwd)

        driver.find_element("id", "login").click()

    def get_friends(self, driver, relation_no=0):
        """
        获取好友列表
        :param driver:
        :param relation_no:
        :return:
        """
        friend_map = {}
        tag_div = driver.find_element_by_id("nxSlidebar")
        tag_friend = tag_div.find_element_by_class_name("app-friends")
        link = tag_friend.find_element_by_class_name("app-link").get_attribute("href")
        driver.get(link)
        print(driver.page_source)

        for i in range(1000):
            ph.scroll_foot(driver)

        tag_ul = driver.find_element_by_id("friends-list-con")
        lis = tag_ul.find_elements_by_class_name("friend-detail")
        for li in lis:
            data_id = li.get_attribute("data-id")
            data_name = li.get_attribute("data-name")
            friend_map[data_id] = {"from": self.user_id, "friendId": data_id, "friendName": data_name,
                                   "relationNo": relation_no}  # data_id, data_name, relationNo)
            # 落盘操作

        print(friend_map)

        conn = redis_client.get_connect()
        for x in friend_map.keys():
            conn.rpush("friends", friend_map[x])