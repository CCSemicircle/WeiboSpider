import json
import re
from urllib import request
import urllib

import chardet
import pandas as pd
from utils import helper
from utils.TimeLogger import log

from utils.config import cookie
import time
from utils import request
from utils.get_ip import proxy

INF = 10000000  # 无限大数
MIN = 10  # 空文件最小值

def get_weibo(uid, start_date, end_date, csv_path):
    """按照时间范围获取微博，时间格式：YY-mm-dd，包括左边界当天，不包括右边界当天"""
    start_date = time.strptime(start_date, "%Y-%m-%d")
    end_date = time.strptime(end_date, "%Y-%m-%d")
    if start_date >= end_date:
        print('开始时间不能早于结束时间！')
        return -1
    # print(start_time < end_time) # True

    # print(start_time, end_time)
    dic = {}
    list_forum = []

    headers = {
        'authority': 'weibo.com',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'cache-control': 'max-age=0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'sec-ch-ua-mobile': '?0',
        'Accept - Encoding': 'utf-8',
        'upgrade-insecure-requests': '1',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://weibo.com',
        'referer': 'https://weibo.com/p/1005057006403277/home?from=page_100505&mod=TAB',
        'Connection': 'keep-alive',
        'Host': 'weibo.com',
        'accept-language': 'zh-CN,zh;q=0.9',
        'Cookie': cookie
    }

    # 获取已经已经存储数据大小
    csv_size = helper.get_file_size(csv_path)
    # print(type(uid))
    finished_mid = []
    if csv_size > MIN:  # 不能直接与0比较，有空符号占很小的空间
        weibo_df = pd.read_csv(csv_path, sep='\t', encoding='utf-8', index_col=False, low_memory=False, usecols=[0,1])
        finished_mid = list(weibo_df[weibo_df['uid']==uid]['mid'].astype(str))  # 因为后续爬取的mid为str类型，所以此处需要设置为str类型
        # print(finished_mid)

    forum_data = []  # 用户的帖子列表
    page_num = INF
    for page in range(1, page_num):
        add = urllib.request.Request(url="https://weibo.com/%s?is_all=1&page=%d" % (uid, page),
                                     headers=headers)  # 设置page
        try:
            r = request.urlib(add, 10)
        except:
            r = request.urlib(add, 10)

        try:
            page_id = re.findall(r'\$CONFIG\[\'page_id\']=\'(\d+)\'', r)[0]
            domain = re.findall(r'\$CONFIG\[\'domain\']=\'(\d+)\'', r)[0]
        except:
            print('page_id error', r)
            return -1
        forums = re.findall(r'<div action-data=\\"cur_visible=0\\"   (.*?)<div node-type=\\"feed_list_repeat\\"', r)  # 每一页的微博帖子
        part_num = 3  # 每个page的最大part数
        last_forum_mid = -1
        for i in range(0, part_num):
            print('user id: %s, start %d page, part %d.' % (uid, page, i))
            forums_num = len(forums)
            # print('forums num', forums_num)
            for j in range(forums_num):
                dic_forum = {}
                forum = forums[j]
                if ('feedtype=\\"top\\"' in forum):
                    # 如果是置顶微博，直接跳过
                    continue

                # 获取帖子mid值
                mid = re.findall(r'.*?mid=\\"(.*?)\\"', forum)
                dic_forum["mid"] = mid[0] if mid else None
                # print('mid', dic_forum['mid'])
                # print(type(dic_forum["mid"]))  # str

                if dic_forum["mid"] is None or dic_forum["mid"] in finished_mid:
                    # 如果没有mid或者已经完成爬取直接爬取下一个
                    continue

                # print(forum)

                if j == 0 and dic_forum["mid"] == last_forum_mid:
                    # 已经开始重复，结束爬取返回
                    print('page max parts', i)
                    if forum_date:
                        # 如果有数据再存储
                        forum_df = pd.DataFrame(forum_data)
                        forum_df.to_csv(csv_path, sep='\t', index=False, encoding='utf_8_sig', mode='a+',
                                        header=True if helper.get_file_size(csv_path) < MIN else False)
                    return 0
                elif j == 0:
                    last_forum_mid = dic_forum['mid']  # 设置为每个part的第一个mid

                # 记录帖子的用户uid
                dic_forum["uid"] = uid

                # 记录帖子的用户nick
                nick = re.findall(r'.*?nick-name=\\"(.*?)\\"', forum)
                dic_forum['nick'] = eval(repr(nick[0]).replace('\\\\', '\\')).encode("utf-8").decode("utf-8") if nick else None
                # print('nick', dic_forum['nick'])

                # 获取发帖日期
                date = re.findall(r'<div class=\\"WB_from S_txt2\\">.*?title=\\"(.*?)\\"', forum)
                dic_forum["date"] = date[0] if date else None
                forum_date = time.strptime(dic_forum['date'], "%Y-%m-%d %H:%M")
                if forum_date >= end_date:
                    # 大于规定时间就继续continue
                    # print('weibo time', dic_forum["date"])
                    continue
                if forum_date < start_date:
                    # 小于规定时间就直接返回，代表已经爬取结束
                    if forum_date:
                        # 如果有数据再存储
                        forum_df = pd.DataFrame(forum_data)
                        forum_df.to_csv(csv_path, sep='\t', index=False, encoding='utf_8_sig', mode='a+',
                                        header=True if helper.get_file_size(csv_path) < MIN else False)
                    return 0

                # 获取帖子的小尾巴（来自****）
                app_source = re.findall(r'app_source.*?>(.*?)<\\/a>', forum)
                dic_forum['app_source'] = eval(repr(app_source[0]).replace('\\\\', '\\')).encode("utf-8").decode("utf-8") if app_source else None
                # print('app_source', app_source)

                # 获取帖子中照片链接
                picture = re.findall(r'<img.*?src=\\"(.*?)\\"', forum)
                # print('picture', picture)
                dic_forum["pictures"] = ", ".join(picture[1:]) if len(picture) > 1 else None  # 去掉头像
                # print('picture', dic_forum["num_picture"])

                # 获取贴文正文
                # 正文链接
                dic_forum['content_link'] = "https://weibo.com/p/aj/mblog/getlongtext?mid=%s" % dic_forum['mid']
                # print('content link', dic_forum['content_link'])

                # 正文内容，包含主题标签
                add = urllib.request.Request(url="https://weibo.com/p/aj/mblog/getlongtext?mid=%s" % dic_forum['mid'],
                                             headers=headers)
                try:
                    r = request.urlib(add, 10)
                except:
                    r = request.urlib(add, 10)

                try:
                    r = json.loads(r)
                except:
                    print('json data', r)
                    if "200 OK" in r:
                        # 代表已经结束微博
                        return 0
                    return -1
                try:
                    content = r["data"]["html"].replace(" ", "").replace("\\r\\n", "")
                except:
                    log('content error: {}'.format(r), save=True)
                    return -1
                content = helper.clear_html(content)  # 去掉html标签
                # print('content', content)
                # print(content)
                dic_forum['content'] = content if content else None
                # print('content', dic_forum['content'])

                # 提取正文中的话题标签
                content_topics = re.findall(r'(#.*?#)', content)
                dic_forum['content_topics'] = ', '.join(content_topics) if content_topics else None
                # print('content tags', dic_forum['content_tags'])

                # 获取帖子中视频链接，需要动态获取，后续再添加 todo
                # video = re.findall(r'<video.*?src=\\"(.*?)\\"', forum)
                # dic_forum["video"] = video[0] if video else None
                # print('video', dic_forum['video'])

                # 获取帖子中其他链接
                urls = re.findall(r'<a.*?href="(.*?)".*?>(<i.*?i>)(.*?)</a>', content, re.DOTALL)
                dic_forum['urls'] = ', '.join(urls) if urls else None
                # print('urls', dic_forum['urls'])

                # 获取帖子中的转发、评论、点赞数
                forward_count = re.findall(
                    r'node-type=\\"forward_btn_text\\".*?<em>(\d*\.?\d+?.?)<\\/em>.*?node-type=\\"comment_btn_text\\',
                    forum)  # 利用特别符号分割，避免将后面的计数匹配到前面
                comment_count = re.findall(
                    r'node-type=\\"comment_btn_text\\".*?<em>(\d*\.?\d+?.?)<\\/em>.*?node-type=\\"like_status\\"',
                    forum)  # 利用特别符号分割，避免将后面的计数匹配到前面
                like_count = re.findall(r'node-type=\\"like_status\\".*?<em>(\d*\.?\d+?.?)<\\/em>', forum)
                dic_forum['forward_count'] = forward_count[0] if forward_count else 0
                dic_forum['comment_count'] = comment_count[0] if comment_count else 0
                dic_forum['like_count'] = like_count[0] if like_count else 0
                # print(dic_forum['forward_count'], dic_forum['comment_count'], dic_forum['like_count'])

                # print(dic_forum)
                forum_data.append(dic_forum)
                # break  # to do

            # 每个part存储一次
            # print(forum_data)
            # print('forum data', len(forum_data))
            if forum_data:
                # 如果有数据再存储
                forum_df = pd.DataFrame(forum_data)
                forum_df.to_csv(csv_path, sep='\t', index=False, encoding='utf_8_sig', mode='a+',
                                header=True if helper.get_file_size(csv_path) < MIN else False)

            # 再次动态加载网页
            url = "https://weibo.com/p/aj/v6/mblog/mbloglist?domain=%s&id=%s&page=%d&pre_page=%d&pagebar=%d&is_all=1" \
                  % (domain, page_id, page, page, i)  # 此处的pre_page应该与page一致才能load本页剩余数据，pagebar代表本页剩余数据的数据块0或1
            # print('url', url)
            add = urllib.request.Request(url=url, headers=headers)
            try:
                r = request.urlib(add, 10)
            except:
                r = request.urlib(add, 10)
            # print('r', r)
            forums = re.findall(r'<div action-data=\\"cur_visible=0\\"   (.*?)<div node-type=\\"feed_list_repeat\\"', r)
            # break # to do
        # break # to do

    return 0


if __name__ == '__main__':
    start_date = "2022-04-29"
    end_date = "2022-05-04"
    # dic = get_user_action("5184087910", start_date, end_date)  # 1906123125
    dic = get_weibo(1906123125, start_date, end_date, 'weibo.csv')
    # df = pd.DataFrame(dic)
    # df.to_csv('weibo.csv', sep='\t', index=False, encoding='utf_8_sig')
    # json_f = open("data/data_九州亿品.json", "w")
    # json.dump(dic, json_f, indent=4)
