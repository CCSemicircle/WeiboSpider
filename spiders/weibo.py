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
from utils import api
from utils.mysql import db

INF = 10000000  # 无限大数

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

def get_weibo(uid, start_date, end_date, sql_table_name='weibo'):
    """按照时间范围获取微博，时间格式：YY-mm-dd，包括左边界与右边界当天"""
    start_time = time.strptime(start_date, "%Y-%m-%d")
    end_time = time.strptime(end_date, "%Y-%m-%d")
    if start_time > end_time:
        print('开始时间不能早于结束时间！')
        return -1

    # 获取已经爬取的mid
    finished_mid = []
    sql = f'select mid from {sql_table_name} where uid={uid} and date(created_at) >= "{start_date}" and date(created_at) <= "{end_date}"'
    # print('weibo sql', sql)
    res = db.getAll(sql)
    # print('weibo res', res)
    if res:
        finished_mid = [dic['mid'] for dic in res]

    # 获取domain与page_id
    home_url = "https://weibo.com/%s?is_all=1&page=%d"
    add = urllib.request.Request(url=home_url % (uid, 1),
                                 headers=headers)  # 设置page

    try:
        r = api.urlib(add, 10)
    except:
        r = api.urlib(add, 10)

    try:
        page_id = re.findall(r'\$CONFIG\[\'page_id\']=\'(\d+)\'', r)[0]
        domain = re.findall(r'\$CONFIG\[\'domain\']=\'(\d+)\'', r)[0]
    except:
        log('page_id error, {}'.format(r), save=True)
        return -1

    # 按页爬取用户微博
    page_num = INF
    for page in range(1, page_num):
        url = "https://weibo.com/p/%s/home?is_ori=1&is_forward=1&is_text=1&is_pic=1&is_video=1&is_music=1&is_article=1&key_word=&start_time=%s&end_time=%s&is_search=1&is_searchadv=1&page=%s" % (page_id, start_date, end_date, page)
        add = urllib.request.Request(url=url, headers=headers)
        try:
            r = api.urlib(add, 10)
        except:
            r = api.urlib(add, 10)

        # print('r', r)

        forums = re.findall(r'<div action-data=\\"cur_visible=0\\"   (.*?)<div node-type=\\"feed_list_repeat\\"', r)  # 每一页的微博帖子
        part_num = 3  # 每个page的最大part数
        last_forum_mid = -1
        for i in range(0, part_num):
            print('user id: %s, start %d page, part %d.' % (uid, page, i))
            forums_num = len(forums)
            if forums_num == 0:
                # 代表爬取结束
                return 0
            for j in range(forums_num):
                dic_forum = {}
                forum = forums[j]
                # print('forum', forum)
                if ('feedtype=\\"top\\"' in forum):
                    # 如果是置顶微博，直接跳过
                    continue

                # 获取帖子mid值
                mid = re.findall(r'.*?mid=\\"(.*?)\\"', forum)
                dic_forum["mid"] = mid[0] if mid else None  # str
                # print('mid', dic_forum['mid'])

                if dic_forum["mid"] is None or dic_forum["mid"] in finished_mid:
                    # 如果没有mid或者已经完成爬取直接爬取下一个
                    continue

                # print(forum)

                if j == 0 and dic_forum["mid"] == last_forum_mid:
                    # 已经开始重复，结束爬取返回
                    print('page max parts', i)
                    return 0
                elif j == 0:
                    last_forum_mid = dic_forum['mid']  # 设置为每个part的第一个mid

                # 记录帖子的用户uid
                dic_forum["uid"] = uid

                # 记录帖子的用户nick
                nick = re.findall(r'.*?nick-name=\\"(.*?)\\"', forum)
                dic_forum['screen_name'] = eval(repr(nick[0]).replace('\\\\', '\\')).encode("utf-8").decode("utf-8") if nick else None

                # 获取发帖日期
                created_at = re.findall(r'<div class=\\"WB_from S_txt2\\">.*?title=\\"(.*?)\\"', forum)
                dic_forum["created_at"] = created_at[0] if created_at else None
                # print('weibo time', dic_forum["created_at"])

                # 直接规定了时间，不需要判断
                # forum_date = time.strptime(dic_forum['created_at'], "%Y-%m-%d %H:%M")
                # if forum_date > end_time:
                #     # 大于规定时间就继续continue
                #     print('weibo time', dic_forum["created_at"])
                #     continue
                # if forum_date < start_time:
                #     # 小于规定时间就直接返回，代表已经爬取结束
                #     # 设置period，以便后续判定已经爬取该区间结束
                #     sql = f'update {sql_table_name} set period={period} where uid={uid} and date(created_at) >= start_date date(created_at) < {end_date}'  # 左包括，右不包括
                #     print('sql', sql)
                #     db.update(sql)
                #     return 0

                # 获取帖子的小尾巴（来自****）
                app_source = re.findall(r'app_source.*?>(.*?)<\\/a>', forum)
                dic_forum['app_source'] = eval(repr(app_source[0]).replace('\\\\', '\\')).encode("utf-8").decode("utf-8") if app_source else None
                # print('app_source', app_source)

                # 获取帖子中照片链接
                picture = re.findall(r'<img.*?src=\\"(.*?)\\"', forum)
                # print('picture', picture)
                picture = [pic.replace('\/', '/') for pic in picture] if picture else None
                dic_forum["pictures"] = ",".join(picture[1:]) if len(picture) > 1 else None  # 去掉头像
                # print('picture', dic_forum["num_picture"])

                # 获取贴文正文
                # 正文内容，包含主题标签
                add = urllib.request.Request(url="https://weibo.com/p/aj/mblog/getlongtext?mid=%s" % dic_forum['mid'],
                                             headers=headers)
                try:
                    content_r = api.urlib(add, 10)
                except:
                    content_r = api.urlib(add, 10)

                try:
                    content_json = json.loads(content_r)
                except:
                    log('load content_r error, {}'.format(content_r), save=True)
                    continue

                try:
                    content = content_json["data"]["html"].replace(" ", "").replace("\\r\\n", "")
                except:
                    log('get content error, {}'.format(content_json), save=True)
                    continue

                content = helper.clear_html(content)  # 去掉html标签
                dic_forum['content'] = content if content else None
                # print('content', dic_forum['content'])

                # 提取正文中的话题标签
                content_topics = re.findall(r'(#.*?#)', content)
                dic_forum['content_topics'] = ','.join(content_topics) if content_topics else None
                # print('content tags', dic_forum['content_tags'])

                # 获取帖子中视频链接，需要动态获取，后续再添加 todo
                # video = re.findall(r'<video.*?src=\\"(.*?)\\"', forum)
                # dic_forum["video"] = video[0] if video else None
                # print('video', dic_forum['video'])

                # 获取帖子中其他链接
                urls = re.findall(r'<a.*?href="(.*?)".*?>(<i.*?i>)(.*?)</a>', content, re.DOTALL)
                urls = [url.replace('\/', '/') for url in urls] if urls else None
                dic_forum['urls'] = ','.join(urls) if urls else None
                # print('urls', dic_forum['urls'])

                # 获取帖子中的转发、评论、点赞数
                forward_count = re.findall(
                    r'node-type=\\"forward_btn_text\\".*?<em>(\d*\.?\d+?.?)<\\/em>.*?node-type=\\"comment_btn_text\\',
                    forum)  # 利用特别符号分割，避免将后面的计数匹配到前面
                comment_count = re.findall(
                    r'node-type=\\"comment_btn_text\\".*?<em>(\d*\.?\d+?.?)<\\/em>.*?node-type=\\"like_status\\"',
                    forum)  # 利用特别符号分割，避免将后面的计数匹配到前面
                like_count = re.findall(r'node-type=\\"like_status\\".*?<em>(\d*\.?\d+?.?)<\\/em>', forum)

                dic_forum['forward_count'] = helper.textNumber2int(forward_count[0]) if forward_count else 0
                dic_forum['comment_count'] = helper.textNumber2int(comment_count[0]) if comment_count else 0
                dic_forum['like_count'] = helper.textNumber2int(like_count[0]) if like_count else 0
                # print(dic_forum['forward_count'], dic_forum['comment_count'], dic_forum['like_count'])

                # print(dic_forum)

                db.insert_dict(dic_forum, sql_table_name)
                # break  # to do

            # 再次动态加载网页
            url = f"https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain={domain}&is_ori=1&is_forward=1&is_text=1&is_pic=1&is_video=1&is_music=1&is_article=1&start_time={start_date}&end_time={end_date}&is_search=1&is_searchadv=1&pagebar={i}&id={page_id}&page={page}&pre_page={page}"
            # print('next url', url)

            # 原来的url，从上往下获取微博（获取最新微博）
            # url = "https://weibo.com/p/aj/v6/mblog/mbloglist?domain=%s&id=%s&page=%d&pre_page=%d&pagebar=%d&is_all=1" \
            #       % (domain, page_id, page, page, i)  # 此处的pre_page应该与page一致才能load本页剩余数据，pagebar代表本页剩余数据的数据块0或1
            # print('url', url)

            add = urllib.request.Request(url=url, headers=headers)
            try:
                r = api.urlib(add, 10)
            except:
                r = api.urlib(add, 10)

            # print('r', r)
            forums = re.findall(r'<div action-data=\\"cur_visible=0\\"   (.*?)<div node-type=\\"feed_list_repeat\\"', r)
            # break # to do
        # break # to do

    return 0


if __name__ == '__main__':
    start_date = "2022-05-09"
    end_date = "2022-05-09"
    # dic = get_user_action("5184087910", start_date, end_date)  # 1906123125
    dic = get_weibo(1906123125, start_date, end_date)
    # df = pd.DataFrame(dic)
    # df.to_csv('weibo.csv', sep='\t', index=False, encoding='utf_8_sig')
    # json_f = open("data/data_九州亿品.json", "w")
    # json.dump(dic, json_f, indent=4)
