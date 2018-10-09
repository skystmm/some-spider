# -*- coding: utf-8 -*-
"""
   Description :
   Author :       sky
   date：          
"""
__author__ = 'sky'
from pyecharts import Graph

from persist_data.mysql_client import db_pool


def fetch_user_data(results):
    """
    :param results:
    :return:
    """
    res = []
    cat = []
    for row in results:
        tmp = dict()
        tmp['name'] = row[0]
        tmp['category'] = row[0]
        tmp['fid'] = row[0]
        tmp['symbolSize'] = 30 - 5 * row[2]
        tmp['draggable'] = 'False'
        tmp['value'] = 10 - (row[2] * 3)
        tmp['label'] = {"normal:": {"show": True}}
        res.append(tmp)
        tmp = dict()
        tmp["name"] = row[0]
        cat.append(tmp)
    return res, cat


def fetch_relation_data(results):
    res = []
    for row in results:
        tmp = dict()
        tmp['source'] = row[0]
        tmp['target'] = row[1]
        res.append(tmp)
    return res


def draw_relation_2():
    sql = "select distinct(fid),`name`,relation_gen from renren_user_info where relation_gen < 2"
    nodes, categories = db_pool.execute_query_sql(sql, fetch_user_data)

    r_sql = """select r.fid,r.tid from renren.renren_relation r where tid in (%s)"""
    s = ''
    for node in nodes:
        s += "'" + node['fid'] + "',"

    links = db_pool.execute_query_sql(r_sql % s[0:len(s) - 1], fetch_relation_data)
    graph = Graph("人人好友关系", width=1200, height=600)
    graph.add(
        "",
        nodes,
        links,
        categories,
        label_pos="right",
        graph_repulsion=50,
        is_legend_show=False,
        line_curve=0.2,
        label_text_color=None,
    )
    graph.render()
