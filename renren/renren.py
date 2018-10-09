# -*- coding: utf-8 -*-
"""
   Description :
   Author :       sky
   date：          
"""
__author__ = 'sky'

import execjs
import re
import time
import json

from urllib import parse
from persist_data import mysql_client
from persist_data.redis_client import *
from common import cookie_handle
from common import http_handle


class RenrenSpider:
    """
    人人网信息获取
    """
    base_url = "http://renren.com"
    friend_page = "http://friend.renren.com/friend/api/getotherfriendsdata"
    login_url = "/ajaxLogin/login?1=1&uniqueTimestamp=%s"

    home_page = "http://www.renren.com/home"
    user_id = 0

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36',
        'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8"
    }

    def login(self, name, passwd):
        passwd, rkey = self.encrypt(passwd)
        param = {
            'email': name,
            'icode': '',
            'password': passwd,
            'rkey': rkey,
            'f': '',
            'origURL': 'http://www.renren.com/home',
            'domain': 'renren.com',
            'key_id': 1,
            'captcha_type': 'web_login'
        }
        login_url = self.login_url % time.time()
        rsp = http_handle.pool.request("post", '%s%s' % (self.base_url, login_url), param)

        # print(type(rsp))
        header = rsp.headers
        cookie = header["set-cookie"]
        cookie = cookie_handle.parse_cookie(cookie)
        cookie_handle.store_cookie(cookie)

        # print(rsp.data.decode("utf-8"))
        self.home_page = json.loads(rsp.data)['homeUrl']

    def get_friends(self, query_info=None):
        """
        获取好友列表
        :param query_info:
        :return:
        """
        start_page = -1
        base_id = self.user_id
        self.get_token()
        param = {
            'p': {"fid": self.user_id, "pz": "24", "type": "WEB_FRIEND", "pn": str(start_page)},
            "requestToken": self.token['requestToken'],
            "_rtk": self.token['_rtk']
        }
        flag = True
        f_li = []
        headers = self.headers
        headers["Cookie"] = cookie_handle.get_cookie()

        if query_info is not None:
            param['p']['fid'] = query_info['fid']
            base_id = query_info['fid']

        def parse_result(result):
            """
            解析好友结果json
            :param result:
            :return:
            """
            if result["code"] != 0:
                raise Exception(result["msg"])
            data = result["data"]
            nonlocal flag
            flag = data["more"]
            friends = data["friends"]
            for friend in friends:
                if 'fid' in friend.keys():
                    tmp = {
                        "baseId": base_id,
                        "fid": friend["fid"],
                        "name": friend["fname"],
                        "info": friend["info"],
                        "relationType": friend["relationType"],
                        "relationGen": 1 if query_info is None else query_info["relationGen"] + 1
                    }
                    f_li.append(tmp)

        def store_info(li):
            """
            保存好友结果到redis
            :param li:
            :return:
            """
            distinct_list = []
            for x in li:
                gen = x["relationGen"]
                fid = x["fid"]

                if get_bitmap(bitmap_key, fid) == 0:
                    if 1 <= gen < 3:
                        rpush("friends", json.dumps(x))
                    set_bitmap(bitmap_key, fid)
                    distinct_list.append(x)

            return distinct_list

        def store_person_mysql(li):
            base = "('%s','%s','%s',%d,%d),"
            sql = 'insert into renren_user_info (fid,name,info,relation_type,relation_gen) values '
            distinct = set()
            for data in li:
                fid = data['fid']
                if fid not in distinct:
                    sql += base % (data['fid'], data['name'], data['info'], data['relationType'], data['relationGen'])
            mysql_client.db_pool.execute_insert_sql(sql[:len(sql) - 1])

        def store_realtion_mysql(li):
            base = "('%s','%s'),"
            sql = 'insert into renren_relation (fid,tid) values '
            distinct = set()
            for data in li:
                fid = data['fid']
                base_id = data['baseId']
                if fid not in distinct:
                    sql += base % (base_id, fid)
                    distinct.add(fid)

            mysql_client.db_pool.execute_insert_sql(sql[:len(sql) - 1])

        while flag:
            start_page += 1
            param["p"]["pn"] = str(start_page)
            encode_param = parse.urlencode(param).encode("utf-8")
            rsp = http_handle.pool.request('POST', self.friend_page, body=encode_param, headers=headers)
            print(rsp.data)
            parse_result(json.loads(rsp.data))

        distinct_li = store_info(f_li)
        store_person_mysql(distinct_li)
        store_realtion_mysql(f_li)

    def encrypt(self, passwd):
        """
        获取秘钥
        :param passwd:
        :return:
        """
        rsp = http_handle.pool.request('get', 'http://login.renren.com/ajax/getEncryptKey')
        res = json.loads(rsp.data)
        with open("./renren/js/encrypt_hook.js") as f:
            line = f.readline()
            htmlstr = ''
            while line:
                htmlstr = htmlstr + line
                line = f.readline()
            ctx = execjs.compile(htmlstr)  # 加载JS文件
            passwd = ctx.call('encrypt', res['e'], res['n'], res['maxdigits'], passwd)
            return passwd, res['rkey']

    def get_token(self):
        """
        获取请求token
        :return:
        """
        self.token = client.get("token")
        if self.token is None:
            p = re.compile("requestToken : '(.*)',\n_rtk : '(.*)'\n")
            u = re.compile("ruid:\"(.*)\",\ntinyPic	: \"(.*)\",\nname : \"(.*)\"")
            headers = self.headers

            cookies = cookie_handle.get_cookie().decode('utf-8')
            headers["Cookie"] = cookies
            r = http_handle.pool.request('get', self.home_page, headers=headers)
            html = r.data

            print(html.decode('utf-8'))
            result = p.search(html.decode())
            self.token = {
                'requestToken': result.group(1),
                '_rtk': result.group(2)
            }
            client.set("token", json.dumps(self.token), 5 * 60 * 60)
            test = u.search(html.decode())
            self.user_id = test.group(1)
            name = test.group(3)
            mysql_client.db_pool.execute_insert_sql("""insert into renren_user_info 
                                                    (fid,name,info,relation_type,relation_gen) values 
                                                    ('%s','%s','',0,0)""" % (self.user_id, name))
        else:
            self.token = json.loads(self.token.decode("utf-8"))
