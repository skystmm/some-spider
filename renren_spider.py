from selenium import webdriver
from persist_data import redis_client
import common.cookie_handle as ch
import common.phatomjs_common as ph

friend_map = {}
driver = webdriver.PhantomJS('/Users/tian/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs')
driver.set_window_size("800","600")
driver.get('http://renren.com')

print(driver.page_source)
print("---------------***************---------------------")
input1 = driver.find_element("id", "email")
input1.send_keys("****")
input2 = driver.find_element("id", "password")
input2.send_keys("*****")


driver.find_element("id", "login").click()

driver.refresh()
ch.get_cookies_redis(driver)
print(driver.page_source)

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
    # data_kind = li.find_element_by_class_name("group-name-list").text
    # print(data_kind)

    friend_map[data_id] = {'baseInfo':'','friendId':data_id,'name': data_name, 'relationGen':1}

print(friend_map)

conn = redis_client.get_connect()
for x in friend_map.keys():
    conn.rpush("friends", friend_map[x])

driver.quit()


