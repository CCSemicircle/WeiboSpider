import os
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


class WeiboSpider:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def get_top_100(self, date, period_type):
        top_100_path = self.data_dir + date + '_' + period_type+ "_top_100.csv"
        if os.path.exists(top_100_path):
            print('---------- load top_100 info ----------')
            top_100_df = pd.read_csv(top_100_path)
        else:
            print('---------- get top_100 info ----------')
            init_field_id = '1001'
            fields = top_100.get_field_id(init_field_id, date, period_type)
            top_100_top_100 = []
            n = len(fields)
            for i in range(n):
                field = fields[i]
                data = top_100.get_top_100(field['field_id'], field['field_name'], date, period_type)
                print('finish {} field, current progress: {} %.'.format(field['field_name'], i / n * 100))
                top_100_top_100.extend(data)
            top_100_df = pd.DataFrame(top_100_top_100)
            top_100_df.to_csv(top_100_path, encoding="utf_8_sig", index=False)

        return top_100_df

    def get_users_info(self, users):
        print('---------- get users info ----------')
        users_info_path = self.data_dir + 'users_info.csv'
        # 获取已经获取的个数
        start = helper.read_csv_line_num(users_info_path)
        users_info = []
        user_num = len(users)
        if start!=0:
            start -= 1
        for i in range(start, user_num):
            uid = users[i]
            info = user_info.get_infos(uid)
            if info==-1:
                continue
            users_info.append(info)
            if i % 20 == 0 or i==user_num-1:
                users_df = pd.DataFrame(users_info)
                users_df.to_csv(users_info_path, index=False, encoding='utf_8_sig', mode='a+', header=True if i==0 else False)
                users_info = []

    def supple_users_info(self, users):
        print('---------- supple users info ----------')
        users_info_path = self.data_dir + 'users_info.csv'
        users_info_df = pd.read_csv(users_info_path)
        users_got_info = list(users_info_df['uid'])
        users_info = []
        cnt = 1
        for uid in users:
            if uid not in users_got_info:
                users_info.append(user_info.get_infos(uid))
                cnt += 1
                if cnt % 20 == 0:
                    users_df = pd.DataFrame(users_info)
                    users_df.to_csv(users_info_path, index=False, encoding='utf_8_sig', mode='a+', header=False)
                    users_info = []

        users_df = pd.DataFrame(users_info)
        users_df.to_csv(users_info_path, index=False, encoding='utf_8_sig', mode='a+', header=False)

    def get_friends_data(self, users, friend_num):
        print('---------- get friends data ----------')
        unfinished_user = []
        fans_path = self.data_dir + 'fans.csv'
        followers_path = self.data_dir + 'followers.csv'
        user_num = len(users)
        for i in range(user_num):
            log('users current process: %.2f %%' % ((i+1)/user_num * 100), save=True)
            uid = users[i]
            # 获取粉丝列表
            res = friends_new.get_friends_data(uid, friend_num, fans_path, friend_title, friendship='fans')
            # 获取关注列表
            res = friends_new.get_friends_data(uid, friend_num, followers_path, friend_title, friendship='followers')
            if res == -1:
                unfinished_user.append(uid)

        return unfinished_user

    def get_weibo(self, users, start_date, end_date):
        print('---------- get users weibo ----------')
        weibo_path = self.data_dir + 'weibo.csv'
        user_num = len(users)
        unfinished_weibo_users = []
        finished_weibo_users = []
        if os.path.exists(self.data_dir+'finished_weibo_users'):
            with open(self.data_dir+'finished_weibo_users', 'rb') as file:
                finished_weibo_users = list(pickle.load(file))

        for i in range(user_num):
            uid = users[i]
            if uid in finished_weibo_users:
                continue
            try:
                res = weibo.get_weibo(uid, start_date, end_date, weibo_path)
                if res == -1:
                    unfinished_weibo_users.append(uid)
                    continue

                finished_weibo_users.append(uid)
                log('finish user %s, current process: %.2f %%' % (uid, (i + 1) / user_num * 100), save=True)
            except:
                with open(self.data_dir + 'finished_weibo_users', 'wb') as file:
                    pickle.dump(finished_weibo_users, file)

        with open(self.data_dir+'unfinished_weibo_users', 'wb') as file:
            pickle.dump(unfinished_weibo_users, file)

    def get_first_comment(self, weibo_mids):
        print('---------- get weibo first comment ----------')
        first_comment_path = self.data_dir + 'first_comment.csv'
        weibo_num = len(weibo_mids)
        unfinished_weibo_mids = []

        finished_weibo_mids = []
        if os.path.exists(self.data_dir+'finished_weibo_mids'):
            with open(self.data_dir+'finished_weibo_mids', 'rb') as file:
                finished_weibo_mids = list(pickle.load(file))

        for i in range(weibo_num):
            mid = weibo_mids[i]
            if mid in finished_weibo_mids:
                continue

            try:
                res = comment.get_first_comment(mid, max_id=-1, max_id_type=0, csv_path=first_comment_path)
                if res == -1:
                    unfinished_weibo_mids.append(mid)
                    continue

                finished_weibo_mids.append(mid)
                log('finish weibo %s, current process: %.2f %%' % (mid, (i + 1) / weibo_num * 100), save=True)
            except:
                with open(self.data_dir + 'finished_weibo_mids', 'wb') as file:
                    pickle.dump(finished_weibo_mids, file)

        with open(self.data_dir+'unfinished_weibo_mids', 'wb') as file:
            pickle.dump(unfinished_weibo_mids, file)


    def get_second_comment(self, first_comment_ids):
        print('---------- get weibo second comment ----------')
        second_comment_path = self.data_dir + 'second_comment.csv'
        first_comment_num = len(first_comment_ids)
        unfinished_first_comment_ids = []

        finished_first_comment_ids = []
        if os.path.exists(self.data_dir+'finished_first_comment_ids'):
            with open(self.data_dir+'finished_first_comment_ids', 'rb') as file:
                finished_first_comment_ids = list(pickle.load(file))

        for i in range(first_comment_num):
            first_comment_id = first_comment_ids[i]
            if first_comment_id in finished_first_comment_ids:
                continue

            try:
                res = comment.get_second_comment(first_comment_id, max_id=-1, max_id_type=0, csv_path=second_comment_path)
                if res == -1:
                    unfinished_first_comment_ids(first_comment_id)
                    continue

                finished_first_comment_ids.append(first_comment_id)
                log('finish first comment id: %s, current process: %.2f %%' % (first_comment_id, (i + 1) / first_comment_num * 100), save=True)
            except:
                with open(self.data_dir + 'finished_first_comment_ids', 'wb') as file:
                    pickle.dump(finished_first_comment_ids, file)

        with open(self.data_dir+'unfinished_first_comment_ids', 'wb') as file:
            pickle.dump(unfinished_first_comment_ids, file)


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


def main():
    # 创建必要文件夹
    data_dir = 'data/'
    helper.ensureDir(data_dir)

    # 爬取榜单博主
    weibo_spider = WeiboSpider(data_dir)
    period_type = args.top_100_type  # 'week' or 'month
    # 'week'-年月日，'month'-年月
    if period_type == 'week':
        top_100_date = helper.format_time(args.top_100_date, "%Y-%m-%d", "%Y%m%d")
    elif period_type == 'month':
        top_100_date = helper.format_time(args.top_100_date, "%Y-%m", "%Y%m")
    top_100 = weibo_spider.get_top_100(top_100_date, period_type)

    users = list(top_100['uid'])
    print('users num', len(users))

    # 获取榜单博主个人信息
    weibo_spider.get_users_info(users)
    weibo_spider.supple_users_info(users)

    friend_num = args.friend_num
    # friend_num = 20

    # # 第一次爬取粉丝及关注
    # threads = []
    # # 创建新线程
    # thread1 = GetFriendsThread(1, "Thread-Fans", users, friend_num, 'fans', data_dir)
    # thread2 = GetFriendsThread(2, "Thread-Followers", users, friend_num, 'followers', data_dir)
    # # 开启新线程
    # thread1.start()
    # thread2.start()
    # # 添加线程到线程列表
    # threads.append(thread1)
    # threads.append(thread2)
    # # 等待所有线程完成
    # for t in threads:
    #     t.join()
    #
    # # 补充未完成的user的粉丝及关注
    # with open(data_dir+'fans_unfinished_user', 'rb') as file:
    #     unfinished_fans_user = list(pickle.load(file))
    # with open(data_dir+'followers_unfinished_user', 'rb') as file:
    #     unfinished_followers_user = list(pickle.load(file))
    #
    # threads = []
    # # 创建新线程
    # thread1 = GetFriendsThread(1, "Thread-Supple Fans", unfinished_fans_user, friend_num, 'fans', data_dir)
    # thread2 = GetFriendsThread(2, "Thread-Supple Followers", unfinished_followers_user, friend_num, 'followers', data_dir)
    # # 开启新线程
    # thread1.start()
    # thread2.start()
    # # 添加线程到线程列表
    # threads.append(thread1)
    # threads.append(thread2)
    # # 等待所有线程完成
    # for t in threads:
    #     t.join()

    # 时间是包含左边界当天，不包含右边界当天
    start_date = args.weibo_start_date
    end_date = args.weibo_end_date
    weibo_spider.get_weibo(users, start_date, end_date)

    # 爬取一级评论
    weibo_path = data_dir+'weibo.csv'
    weibo_df = pd.read_csv(weibo_path, sep='\t', encoding='utf-8', index_col=False, low_memory=False, usecols=[0])
    weibo_mids = list(weibo_df['mid'])
    weibo_spider.get_first_comment(weibo_mids)

    # 爬取二级评论
    first_comment_path = data_dir + 'first_comment.csv'
    first_comment_df = pd.read_csv(first_comment_path, sep='\t', encoding='utf-8', index_col=False, low_memory=False, usecols=[0, 1, 2])
    first_comment_ids = list(first_comment_df['comment_id'])
    weibo_spider.get_second_comment(first_comment_ids)



if __name__ == '__main__':
    main()