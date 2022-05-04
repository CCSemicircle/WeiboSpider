import random
from utils import config
from utils import helper
from utils.get_ip import proxy
import requests
import pandas as pd


MIN = 10  # 空文件最小size


def comment2dict(id, comment, comment_grade):
    """提取comment内容，comment_grade可选1或2"""
    # print('comment', comment)
    dic = dict()
    dic['comment_grade'] = comment_grade
    if comment_grade == 1:
        dic['mid'] = id  # 如果是一级评论，存储评论所属微博mid
    else:
        dic['first_comment_id'] = id  # 如果是二级评论，存储二级评论所属的一级评论comment_id
    dic['comment_id'] = comment['id']
    dic['date'] = helper.time2str(comment['created_at'])
    dic['floor_number'] = comment['floor_number']
    dic['content'] = helper.clear_html(comment['text'])
    dic['source'] = comment['source']
    dic['comment_badge'] = comment['comment_badge'][0]['name'] if 'comment_badge' in comment.keys() else None
    dic['reply_count'] = comment['total_number'] if 'total_number' in comment.keys() else None  # 二级评论不统计回复数
    dic['like_count'] = comment['like_count']

    # 用户信息
    dic['uid'] = comment['user']['id']
    dic['nick'] = comment['user']['screen_name']
    dic['home_url'] = comment['user']['profile_url']
    dic['gender'] = '男' if comment['user']['gender'] == 'm' else '女'
    dic['weibo_count'] = comment['user']['statuses_count']
    dic['verified'] = comment['user']['verified']
    dic['verified_type'] = comment['user']['verified_type'] if 'verified_type' in comment['user'].keys() else None
    dic['verified_type_ext'] = comment['user']['verified_type_ext'] if 'verified_type_ext' in comment['user'].keys() else None
    dic['verified_reason'] = comment['user']['verified_reason'] if 'verified_reason' in comment['user'].keys() else None
    dic['description'] = comment['user']['description']
    dic['gender'] = '男' if comment['user']['gender'] == 'm' else '女'
    dic['mbtype'] = comment['user']['mbtype']
    dic['urank'] = comment['user']['urank']
    dic['mbrank'] = comment['user']['mbrank']
    dic['followers_count'] = comment['user']['follow_count']
    dic['fans_count'] = comment['user']['followers_count']

    return dic


def get_first_comment(mid, max_id, max_id_type, csv_path):
    """获取某条微博的一级评论"""
    mid = str(mid)  # 统一使用str的mid

    # 获取已经已经存储数据大小
    csv_size = helper.get_file_size(csv_path)
    finished_comment_id = []
    if csv_size > MIN:  # 不能直接与0比较，有空符号占很小的空间
        weibo_df = pd.read_csv(csv_path, sep='\t', encoding='utf-8', index_col=False, low_memory=False,
                               usecols=[1, 2])
        finished_comment_id = list(weibo_df[weibo_df['mid'].astype(str) == mid]['comment_id'].astype(str))
        # print('finished_comment_id', finished_comment_id)

    page = 1
    while max_id != 0:
        # print(f'---------- 正在翻页 ----------')
        if page % 5 == 0:
            break  # todo
        comment_data = []

        # 构造一级评论的url
        if max_id==-1:
            # 第一页评论， max_id不作为参数，此处设置为-1以与其他页区分
            url = f'https://m.weibo.cn/comments/hotflow?id={mid}&mid={mid}&max_id_type=0'
            headers = {
                'authority': 'm.weibo.cn',
                'method': 'GET',
                'path': f'/comments/hotflow?id={mid}&mid={mid}&max_id_type=0',
                'scheme': 'https',
                'accept': 'application/json, text/plain, */*',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9',
                'cookie': config.cookie,
                'mweibo-pwa': '1',
                'referer': 'https://m.weibo.cn/status/4463322608501846',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'x-requested-with': 'XMLHttpRequest',
                'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
                # 'x-xsrf-token': token,
            }
        else:
            # 第二页及以后的评论
            url = f'https://m.weibo.cn/comments/hotflow?id={mid}&mid={mid}&max_id={max_id}&max_id_type={max_id_type}'
            headers = {
                'authority': 'm.weibo.cn',
                'method': 'GET',
                'path': f'/comments/hotflow?id={mid}&mid={mid}&max_id={max_id}&max_id_type=0',
                'scheme': 'https',
                'accept': 'application/json, text/plain, */*',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9',
                'cookie':config.cookie,
                'mweibo-pwa': '1',
                'referer': 'https://m.weibo.cn/status/4463322608501846',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'x-requested-with': 'XMLHttpRequest',
                'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
                # 'x-xsrf-token': token,
            }

        # print('url', url)
        try:
            res = requests.get(url, headers=headers, proxies=proxy.random_proxy())
        except:
            res = requests.get(url, headers=headers, proxies=proxy.random_proxy())
        # print('res', res)
        res_json = res.json()
        # print('res_json', res_json)
        if res_json['ok']==0:
            return -1

        # 获取下一页comment所需参数
        max_id = res_json['data']['max_id']
        max_id_type = res_json['data']['max_id_type']
        comment_list = res_json['data']['data']
        # print('comment_list', comment_list)

        if comment_list and comment_list[0]['id'] in finished_comment_id and comment_list[-1]['id'] in finished_comment_id:
            # 如果第一个和最后一个comment id在已经完成的id列表说明该页全部存储，直接进入下一页
            page += 1
            continue

        for comment in comment_list:
            if comment['id'] in finished_comment_id:
                # 避免重复
                continue
            dic = comment2dict(mid, comment, comment_grade=1)
            comment_data.append(dic)

        print('current weibo mid %s, finish %d page comment, current page comment number: %d' % (mid, page, len(comment_list)))
        page += 1
        # print('current page comment: {}'.format(comment_data))
        # 按page写入
        if comment_data:
            # 如果有数据再存储
            forum_df = pd.DataFrame(comment_data)
            forum_df.to_csv(csv_path, sep='\t', index=False, encoding='utf_8_sig', mode='a+',
                            header=True if helper.get_file_size(csv_path) < MIN else False)
        # break  # to do
    print('finish weibo mid %s all first comment.' % mid)
    return 0


def get_second_comment(first_comment_id, max_id, max_id_type, csv_path):
    """获取某条微博的一级评论下的二级评论"""
    first_comment_id = str(first_comment_id)  # 统一使用str的mid
    # print('first comment id', first_comment_id)

    comment_data = []

    # 获取已经已经存储数据大小
    csv_size = helper.get_file_size(csv_path)
    finished_second_comment_id = []
    if csv_size > MIN:  # 不能直接与0比较，有空符号占很小的空间
        weibo_df = pd.read_csv(csv_path, sep='\t', encoding='utf-8', index_col=False, low_memory=False,
                               usecols=[1, 2])
        finished_second_comment_id = list(weibo_df[weibo_df['first_comment_id'].astype(str) == first_comment_id]['comment_id'].astype(str))
        # print('finished_second_comment_id', finished_second_comment_id)

    page = 1
    while max_id != 0:
        # print(f'---------- 正在翻页 ----------')
        # print(f'---------- 一级评论id：{first_comment_id} ----------')

        # 构造二级评论的url
        if max_id==-1:
            url = f'https://m.weibo.cn/comments/hotFlowChild?cid={first_comment_id}&max_id=0&max_id_type=0'
            headers = {
                'authority': 'm.weibo.cn',
                'method': 'GET',
                'path': f'/comments/hotFlowChild?cid={first_comment_id}&max_id=0&max_id_type=0',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                # 'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9',
                'cookie': config.cookie,
                'mweibo-pwa': '1',
                'referer': 'https://weibo.com/1787569845/LdUgMtnNj?filter=hot&root_comment_id=0&type=comment#_rnd1651565674303',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'x-requested-with': 'XMLHttpRequest',
                'user-agent': random.choice(config.user_agent),
                # 'x-xsrf-token': config.token,
            }
        else:
            url = f'https://m.weibo.cn/comments/hotFlowChild?cid={first_comment_id}&max_id={max_id}&max_id_type={max_id_type}'
            headers = {
                'authority': 'm.weibo.cn',
                'method': 'GET',
                'path': f'/comments/hotFlowChild?cid={first_comment_id}&max_id={max_id}&max_id_type={max_id_type}',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                # 'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9',
                'cookie': config.cookie,
                'mweibo-pwa': '1',
                'referer': 'https://weibo.com/1787569845/LdUgMtnNj?filter=hot&root_comment_id=0&type=comment#_rnd1651565674303',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'x-requested-with': 'XMLHttpRequest',
                'user-agent': random.choice(config.user_agent),
                # 'x-xsrf-token': config.token,
            }
        # print('url', url)
        try:
            res = requests.get(url, headers=headers, proxies=proxy.random_proxy())
        except:
            res = requests.get(url, headers=headers, proxies=proxy.random_proxy())
            # res = requests.get(url, proxies=proxy.random_proxy())

        # 418说明采集频率过快, 需要暂停一段时间
        if res.status_code==418:
            return -1

        res_json = res.json()
        # print('res json', res_json)
        if res_json['ok']==0 and res_json['msg']=='暂无数据':
            print('finish first comment mid %s all second comment.' % first_comment_id)
            return 0
        if res_json['ok']==0 and res_json['msg']!='暂无数据':
            return -1

        max_id = res_json['max_id']
        max_id_type = res_json['max_id_type']
        comment_list = res_json['data']

        if comment_list and comment_list[0]['id'] in finished_second_comment_id and comment_list[-1]['id'] in finished_second_comment_id:
            # 如果第一个和最后一个comment id在已经完成的id列表说明该页全部存储，直接进入下一页
            page += 1
            continue

        for comment in comment_list:
            dic = comment2dict(first_comment_id, comment, comment_grade=2)
            comment_data.append(dic)

        print('current first comment id %s, finish %d page second comment, current page comment number: %d' % (first_comment_id, page, len(comment_list)))
        page += 1
        # print('current page comment: {}'.format(comment_data))
        # 按page写入
        if comment_data:
            # 如果有数据再存储
            forum_df = pd.DataFrame(comment_data)
            forum_df.to_csv(csv_path, sep='\t', index=False, encoding='utf_8_sig', mode='a+',
                            header=True if helper.get_file_size(csv_path) < MIN else False)
        # break  # to do
    print('finish first comment mid %s all second comment.' % first_comment_id)
    return 0


if __name__ == '__main__':
    res1 = get_first_comment('4763588521364858', max_id=-1, max_id_type=0, csv_path='first_comment.csv')
    res2 = get_second_comment('4763589019961289', max_id=-1, max_id_type=0, csv_path='seconde_comment.csv')