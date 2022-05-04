import json
import random

import pandas as pd
import requests
import time
import math
from utils import config
from utils import helper
from utils.get_ip import proxy


MIN = 10  # 文件最小值


def user2dic(uid, user, friendship='fans'):
    dic = dict()
    curr_id = "followers_id" if friendship == 'fans' else 'fans_id'
    dic[curr_id] = uid
    first_layer_title = ['id', 'idstr', 'class', 'name', 'province', 'city', 'location', 'description', 'url',
                         'profile_image_url', 'cover_image_phone', 'profile_url', 'domain', 'gender', 'followers_count',
                         'followers_count_str', 'friends_count', 'pagefriends_count', 'statuses_count',
                         'video_status_count', 'video_play_count', 'favourites_count', 'created_at', 'following',
                         'allow_all_act_msg', 'geo_enabled', 'verified', 'verified_type', 'status_id', 'status_idstr',
                         'ptype', 'allow_all_comment', 'verified_reason', 'verified_trade', 'verified_reason_url',
                         'verified_source', 'verified_source_url', 'bi_followers_count', 'lang',
                         'star', 'mbtype', 'mbrank', 'svip', 'block_word', 'block_app', 'chaohua_ability',
                         'brand_ability', 'nft_ability', 'credit_score', 'user_ability', 'urank', 'story_read_state',
                         'vclub_member', 'is_teenager', 'is_guardian', 'is_teenager_list', 'pc_new',
                         'special_follow', 'planet_video', 'video_mark', 'live_status', 'user_ability_extend',
                         'brand_account', 'hongbaofei']

    for title in first_layer_title:
        dic[title] = user[title] if title in user.keys() else None

    # 二级表头
    dic['sexual_content'] = user['insecurity']['sexual_content'] \
        if 'insecurity' in user.keys() and 'sexual_content' in user['insecurity'].keys() else None

    dic['status_total_cnt'] = user['status_total_counter']['total_cnt'] \
        if 'status_total_counter' in user.keys() and 'total_cnt' in user['status_total_counter'].keys() else None
    dic['status_repost_cnt'] = user['status_total_counter']['repost_cnt'] \
        if 'status_total_counter' in user.keys() and 'repost_cnt' in user['status_total_counter'].keys() else None
    dic['status_comment_cnt'] = user['status_total_counter']['comment_cnt'] \
        if 'status_total_counter' in user.keys() and 'comment_cnt' in user['status_total_counter'].keys() else None
    dic['status_like_cnt'] = user['status_total_counter']['like_cnt'] \
        if 'status_total_counter' in user.keys() and 'like_cnt' in user['status_total_counter'].keys() else None
    dic['status_comment_like_cnt'] = user['status_total_counter']['comment_like_cnt'] \
        if 'status_total_counter' in user.keys() and 'comment_like_cnt' in user['status_total_counter'].keys() else None

    return dic


def get_json_data(url):
    headers = {
        'authority': 'weibo.com',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'cache-control': 'max-age=0',
        'User-Agent': random.choice(config.user_agent),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'sec-ch-ua-mobile': '?0',
        'upgrade-insecure-requests': '1',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://weibo.com',
        'referer': 'https://weibo.com/p/1005057006403277/home?from=page_100505&mod=TAB',
        # 'Connection': 'keep-alive',
        'Connection': 'close',
        'Host': 'weibo.com',
        'accept-language': 'zh-CN,zh;q=0.9',
        "Referer": "https://weibo.com",
        'Cookie': config.cookie
    }

    # random_proxy = proxy.random_proxy()

    # # 代理成功了，但是headers需要改变
    # targetUrl = "https://www.baidu.com"
    # resp = requests.get(targetUrl, proxies=random_proxy)
    #
    # print(resp.status_code)
    #
    # while resp and resp.status_code != 200:
    #     random_proxy = proxy.random_proxy()
    #     resp = requests.get(targetUrl, proxies=random_proxy)
    #     print(resp.status_code)

    # r = requests.get("http://httpbin.org/ip", proxies=random_proxy)
    # print(r.text)
    # print('random_proxy', random_proxy)

    try:
        response = requests.get(url, headers=headers, timeout=10, proxies=proxy.random_proxy())
    except:
        response = requests.get(url, headers=headers, timeout=10, proxies=proxy.random_proxy())

    # response = requests.get(url, headers=headers, timeout=20)
    # time.sleep(2)  # 加上2s 的延时防止被反爬
    # print('response', response.text)
    return response.text

def get_friends_data(uid, total_number, csv_path, friendship='fans'):
    curr_id = 'fans_id' if friendship == 'followers' else 'followers_id'

    # 获取已经获取的个数
    start = helper.get_file_size(csv_path)
    # print('start', start)
    if start > MIN:
        df = pd.read_csv(csv_path, sep='\t', encoding='utf-8', index_col=False, low_memory=False,
                         usecols=[0])  # 此处必须设置为False，否则会将第一列设置为索引，导致第一二列数据合并
        # print('curr_id', df[curr_id])
        start = len(df[df[curr_id] == uid])
        # print('df length', len(df))
    # print('start', start)

    # 先获取总的粉丝数量
    url = "https://www.weibo.com/ajax/friendships/friends?relate=fans&page={}&uid={}&type=all&newFollowerCount=0" if friendship == 'fans' \
        else "https://www.weibo.com/ajax/friendships/friends?page={}&uid={}"
    json_data = get_json_data(url.format(1, uid))
    try:
        response = json.loads(json_data)
        # print('response', response)
    except:
        print('json data', json_data)
        if "200 OK" in json_data:
            return 0
        return -1

    total_number = total_number if response['total_number'] > total_number else response['total_number']
    # print(friendship + ' total number', total_number)
    start_page = math.ceil(start / 20) + 1
    num_page = math.ceil(total_number / 20) + 1
    # 然后依次爬取每一页的数据
    for page in range(start_page, num_page):
        json_data = get_json_data(url.format(page, uid))
        try:
            response = json.loads(json_data)
        except:
            print('json data', json_data)
            return -1
        if 'users' not in response.keys() or len(response['users']) == 0:
            print('{} {} max page: {}'.format(uid, friendship, page))
            return -1

        users = response['users']

        friends = []
        for user in users:
            dic = user2dic(uid, user, friendship)
            friends.append(dic)

        # 按page存储
        if friends:
            # 如果有数据再存储
            friends_df = pd.DataFrame(friends)
            friends_df.to_csv(csv_path, sep='\t', index=False, encoding='utf_8_sig', mode='a+', header=True if helper.get_file_size(csv_path) < MIN else False)

        print('user id: %s, %s data start %d page, current process: %.2f %%' % (uid, friendship, page, page / (num_page - 1) * 100))

    return 0


if __name__ == '__main__':
    uids = [1669879400]  # 如果想获取多个人的粉丝关注信息，就在后面依次加上uid
    total_number = 2000
    title = ['id', 'idstr', 'class', 'screen_name', 'name', 'province', 'city', 'location', 'description', 'url',
             'profile_image_url', 'cover_image_phone', 'profile_url', 'domain', 'weihao', 'gender', 'followers_count',
             'followers_count_str', 'friends_count', 'pagefriends_count', 'statuses_count', 'video_status_count',
             'video_play_count', 'favourites_count', 'created_at', 'following', 'allow_all_act_msg', 'geo_enabled',
             'verified', 'verified_type', 'remark', 'insecurity', 'status_id', 'status_idstr', 'ptype',
             'allow_all_comment', 'avatar_large', 'avatar_hd', 'verified_reason', 'verified_trade',
             'verified_reason_url', 'verified_source', 'verified_source_url', 'follow_me', 'like', 'like_me',
             'online_status', 'bi_followers_count', 'lang', 'star', 'mbtype', 'mbrank', 'svip', 'block_word',
             'block_app', 'chaohua_ability', 'brand_ability', 'nft_ability', 'credit_score', 'user_ability', 'urank',
             'story_read_state', 'vclub_member', 'is_teenager', 'is_guardian', 'is_teenager_list', 'pc_new',
             'special_follow', 'planet_video', 'video_mark', 'live_status', 'user_ability_extend',
             'status_total_counter', 'video_total_counter', 'brand_account', 'hongbaofei']
    followers_path = "followers.csv"
    fans_path = "fans.csv"
    for uid in uids:
        print(get_friends_data(uid, 40, fans_path, friendship='fans'))
        print(get_friends_data(uid, 40, followers_path, friendship='followers'))
