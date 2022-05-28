import pickle

import pandas as pd

from spiders import top_100
from spiders import user_info
from spiders import friends_new
from utils import helper
import threading
from utils.TimeLogger import log
from spiders import weibo
from spiders import comment
from utils.parser import args
from utils.mysql import db

def finish_record(start_date, end_date, info_type, uid):
    sql = f'insert into finish_record (start_date, end_date, info_type, uid) values (%s, %s, %s, %s);'
    db.insertOne(sql, (start_date, end_date, info_type, uid))

def delet_finish_uid(users, info_type, start_date, end_date):
    sql = f'select uid from finish_record where info_type="{info_type}" and date(start_date) = "{start_date}" and date(end_date) = "{end_date}"'
    res = db.getAll(sql)
    if res:
        finish_uid = [dic['uid'] for dic in res]
    else:
        finish_uid = []
    users = list(set(users) - set(finish_uid))
    return users

def get_top_100(date, period_type, sql_table_name='top100'):
    log('---------- get top_100 info ----------', save=True)
    init_field_id = '1001'
    # to do 测试时，不必重复验证
    fields = top_100.get_field_id(init_field_id, date, period_type)
    n = len(fields)
    for i in range(n):
        field = fields[i]
        top_100.get_top_100(field['field_id'], field['field_name'], date, period_type, sql_table_name)
        log('finish %s field, current progress: %.2f %%.' % (field['field_name'], (i+1) / n * 100), save=True)
    sql = f'select uid from {sql_table_name} where date="{date}" and period_type ="{period_type}"'  # 必须加引号
    res = db.getAll(sql)
    if res:
        users = [dic['uid'] for dic in res]
    users = list(set(users))  # 博主可能同时在不同的榜单，所以要去重
    return users

def get_users():
    """自定义获取users函数"""
    # todo 此处需要返回users
    df = pd.read_csv('data/20220418_week_top_100.csv')
    users = list(df['uid'])
    # print('users', users)
    return users

def get_users_info(users):
    log('---------- get users info ----------', save=True)
    user_num = len(users)
    for i in range(user_num):
        uid = users[i]
        try:
            user_info.get_user_info(uid)
            log('finish get user %s info, current progress: %.2f %%.' % (uid, (i + 1) / user_num * 100), save=True)
        except:
            with open('log/unfinish_info_user.txt', 'a+') as file:
                file.write(str(uid)+'\n')
            log('can not spider user %s info' % uid, save=True)


def get_friends_data(users, friend_num):
    log('---------- get friends data ----------', save=True)
    user_num = len(users)
    for i in range(user_num):
        uid = users[i]  # int
        try:
            # 获取粉丝列表
            friends_new.get_friends_data(uid, friend_num, friendship='fans')
            # 获取关注列表
            friends_new.get_friends_data(uid, friend_num, friendship='followers')
            log('finish get user %s friends, current process: %.2f %%' % (uid, ((i + 1) / user_num * 100)), save=True)
        except:
            with open('log/unfinish_friend_user.txt', 'a+') as file:
                file.write(str(uid)+'\n')
            log('can not spider user %s friend' % uid, save=True)

def get_weibo(users, start_date, end_date):
    log('---------- get users weibo ----------', save=True)
    users = delet_finish_uid(users,  'weibo', start_date, end_date)
    user_num = len(users)
    # print('user_num', user_num)
    for i in range(user_num):
        uid = users[i]
        try:
            weibo.get_weibo(uid, start_date, end_date)
            finish_record(start_date, end_date, 'weibo', uid)
            log('finish get user %s weibo, current progress: %.2f %%.' % (uid, (i + 1) / user_num * 100), save=True)
        except:
            with open('log/unfinish_weibo_user.txt', 'a+') as file:
                file.write(str(uid)+'\n')
            log('can not spider user %s weibo' % uid, save=True)

def get_first_comment(users, start_date, end_date, weibo_sql_table_name='weibo'):
    log('---------- get weibo first comment ----------', save=True)
    users = delet_finish_uid(users, 'first_comment', start_date, end_date)
    user_num = len(users)
    for i in range(user_num):
        uid = users[i]
        sql = f'select mid from {weibo_sql_table_name} where uid={uid} and date(created_at) >= "{start_date}" and date(created_at) <= "{end_date}"'
        res = db.getAll(sql)
        weibo_mids = [dic['mid'] for dic in res] if res else []
        # print('weibo mids', weibo_mids)
        try:
            for mid in weibo_mids:
                comment.get_first_comment(mid, max_id=-1, max_id_type=0)
            finish_record(start_date, end_date, 'first_comment', uid)
            log('finish get user %s weibo first comment, current process: %.2f %%' % (uid, (i + 1) / user_num * 100), save=True)
        except:
            with open('log/unfinish_first_comment_user.txt', 'a+') as file:
                file.write(str(uid)+'\n')
            log('can not spider user %s first comment' % uid, save=True)


def get_second_comment(users, start_date, end_date, weibo_sql_table_name='weibo', first_comment_sql_table_name='first_comment'):
    log('---------- get weibo second comment ----------', save=True)
    users = delet_finish_uid(users, 'second_comment', start_date, end_date)
    user_num = len(users)
    for i in range(user_num):
        uid = users[i]
        weibo_sql = f'select mid from {weibo_sql_table_name} where uid={uid} and date(created_at) >= "{start_date}" and date(created_at) <= "{end_date}"'
        first_comment_sql = f'select comment_id from {first_comment_sql_table_name} where mid in ({weibo_sql})'
        res = db.getAll(first_comment_sql)
        first_comment_ids = [dic['comment_id'] for dic in res] if res else []
        try:
            for first_comment_id in first_comment_ids:
                comment.get_second_comment(first_comment_id, max_id=-1, max_id_type=0)
            finish_record(start_date, end_date, 'second', uid)
            log('finish get user %s weibo second comment, current process: %.2f %%' % (uid, (i + 1) / user_num * 100),
                save=True)
        except:
            with open('log/unfinish_second_comment_user.txt', 'a+') as file:
                file.write(str(uid)+'\n')
            log('can not spider user %s second comment' % uid, save=True)


class GetFriendsThread(threading.Thread):
    def __init__(self, thread_id, thread_name, users, friend_num, friendship, data_dir):
        threading.Thread.__init__(self)
        self.id = thread_id
        self.name = thread_name
        self.users = users
        self.friend_num = friend_num
        self.friendship = friendship
        self.data_dir = data_dir
        self.unfinished_user = []

    def run(self):
        print("---------- 开始%s线程 ----------" % self.name)
        csv_path = self.data_dir + self.friendship+'.csv'
        # print(self.users[0], self.friend_num, csv_path, [self.friendship+'_id', *friend_title],self.friendship)
        user_num = len(self.users)
        print('user_num', user_num)
        for i in range(user_num):
            uid = self.users[i]
            res = friends_new.get_friends_data(uid, self.friend_num, csv_path, friendship=self.friendship)
            if res == -1:
                self.unfinished_user.append(uid)
            log('finish user %s %s, current process: %.2f %%' % (uid, self.friendship, (i + 1) / user_num*100), save=True)

    def __del__(self):
        with open(self.data_dir+self.data_dir + self.friendship+'_unfinished_user', 'wb') as file:
            pickle.dump(self.unfinished_user, file)
        print("---------- %s线程结束 ----------" % self.name)


class SpiderThread(threading.Thread):
    def __init__(self, thread_id, users, friend_num, start_date, end_date):
        threading.Thread.__init__(self)
        self.id = thread_id
        self.users = users
        self.friend_num = friend_num
        self.start_date = start_date
        self.end_date = end_date

    def run(self):
        log("---------- start %d thread ----------" % self.id, save=True)
        ### 在这里注释对应的部分就可以取消某一部分的爬虫

        # user info
        # log('start %d thread user info' % self.id, save=True)
        # get_users_info(self.users)
        # log('end %d thread user info' % self.id, save=True)

        # fans / followers
        # log('start %d thread friends_data' % self.id, save=True)
        # get_friends_data(self.users, self.friend_num)
        # log('end %d thread friends_data' % self.id, save=True)

        # weibo
        log('start %d thread weibo' % self.id, save=True)
        get_weibo(self.users, self.start_date, self.end_date)
        log('end %d thread weibo' % self.id, save=True)

        # first comment
        log('start %d thread first_comment' % self.id, save=True)
        get_first_comment(self.users, self.start_date, self.end_date)
        log('end %d thread first_comment' % self.id, save=True)

        # second comment
        log('start %d thread second_comment' % self.id, save=True)
        get_second_comment(self.users, self.start_date, self.end_date)
        log('end %d thread second_comment' % self.id, save=True)

    def __del__(self):
        log("---------- end %d thread ----------" % self.id, save=True)


def main():
    # 初始化
    period_type = args.top_100_type  # 'week' or 'month
    # 'week'-年月日，'month'-年月
    if period_type == 'week':
        top_100_date = helper.format_time(args.top_100_date, "%Y-%m-%d", "%Y%m%d")
    elif period_type == 'month':
        top_100_date = helper.format_time(args.top_100_date, "%Y-%m", "%Y%m")

    start_date = args.weibo_start_date
    end_date = args.weibo_end_date

    friend_num = args.friend_num
    thread_num = args.thread_num

    # 爬取榜单博主
    # users = get_top_100(top_100_date, period_type)

    ###  自定义获取users函数  ###
    users = get_users()

    # # 取一部分users进行后续测试 to do
    # users = users[:5]
    # friend_num = 20  # 测试数据 to do

    ### 创建多线程，把user分成多个部分，分别进行统一的 信息->粉丝->微博->评论 爬取 ###

    # 分割users以便多线程进行
    users_num = len(users)
    step = users_num//thread_num

    # 创建线程爬取后续信息
    threads = []
    for i in range(thread_num):
        step_users = users[i*step: (i+1)*step] if i!=thread_num-1 else users[i*step: ]
        # print(f'{i}, {step_users}')
        thread = SpiderThread(i, step_users, friend_num, start_date, end_date)
        threads.append(thread)

    # 开启线程
    [thread.start() for thread in threads]

    # 等待所有线程完成
    [thread.join() for thread in threads]


if __name__ == '__main__':
    main()
    # finish_record('2022-04-29', '2022-05-01', 'second_comment', 3929704484)
    # get_second_comment([3929704484],'2022-04-29', '2022-05-01')