import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

def validate_datetime(date_text, type):
    """时间校验"""
    try:
        if date_text != datetime.strptime(date_text, type).strftime(type):
            raise ValueError
        return True
    except ValueError:
        return False

def change_datetime_type(date_text, raw_type, new_type):
    data_time = datetime.strptime(date_text, raw_type).strftime(new_type)
    return data_time


def textNumber2int(init_number):
    """将带有文字的数字转为纯数字"""
    init_number = str(init_number)  #  先统一化成str
    if init_number=='True':
        return True
    if init_number=='False':
        return False
    if len(init_number) == 0:
        return -1
    if '千' in init_number:
        number = int(float(init_number[:-1]) * 1000)
    elif '万' in init_number:
        number = int(float(init_number[:-1])*10000)
    elif '亿' in init_number:
        number = int(float(init_number[:-1])*100000000)
    elif '.' in init_number:
        number = int(float(init_number))
    else:
        try:
            number = int(init_number)
        except:
            print('init number', init_number)
            return -1

    return number

def format_users_info(path):
    # path = 'last data/users_info.csv'
    df = pd.read_csv(path, sep=',', low_memory=False)


    # 替换nan值
    df.fillna(value='', inplace=True)

    # 替换列名
    df.columns=['uid', 'authentication_grade', 'screen_name', 'location', 'sex',
       'sexual_orientation', 'marriage', 'birthday', 'blood_type', 'blog',
       'style_domain', 'intro', 'regist_time', 'ip_region', 'authentication',
       'company', 'university', 'tags', 'growth_value', 'vip_rank',
       'follower_num', 'fans_num', 'post_num']  # 只能通过全部命名来修改unnamed列名
    # df.rename({'nick': 'screen_name', 'Unnamed: 20': 'follower_num', 'Unnamed: 21': 'fans_num', 'Unnamed: 22':'post_num'}, inplace=True)
    # print(df.columns)
    # 替换列的int类型
    num_columns = ['follower_num', 'fans_num', 'post_num', 'growth_value', 'vip_rank']
    for column in num_columns:
        df[column] = df[column].apply(lambda x: textNumber2int(x))

    # 去除uid为-1的数据
    df.drop(df[df['uid']==-1].index, inplace=True)

    # 添加爬取时间列
    spider_time = path[path.find('-') + 1:path.find('.')]
    spider_time  = change_datetime_type(spider_time , '%Y%m%d', '%Y-%m-%d')
    df['spider_time'] = spider_time

    print(df.head())
    # print(df.columns)

    # df.to_csv('format_data/users_info.csv', sep='\t', index=False)
    return df

def format_friend(path, friendship='fans'):
    # path = 'last data/'+friendship+'.csv'
    df = pd.read_csv(path, sep='\t', low_memory=False)

    # 删除following列
    df.drop(columns=['following'], inplace=True)

    # 替换nan值
    df.fillna(value='', inplace=True)

    # 插入friendship列
    df.insert(0, 'friendship', friendship)
    # 修改uid列名
    uid_title = 'followers_id' if friendship=='fans' else 'fans_id'
    df.rename(columns={uid_title: 'uid'}, inplace=True)

    # 替换列的int类型
    num_columns = ['followers_count', 'friends_count', 'pagefriends_count', 'statuses_count', 'video_status_count',
                   'video_play_count', 'favourites_count', 'verified_type', 'status_id', 'ptype', 'bi_followers_count',
                   'star', 'mbtype', 'mbrank','svip','block_word','block_app','chaohua_ability','brand_ability',
                   'nft_ability','credit_score','user_ability','urank','story_read_state','vclub_member','is_teenager',
                   'is_guardian','is_teenager_list','pc_new','planet_video','video_mark','live_status','user_ability_extend',
                   'brand_account','hongbaofei','sexual_content','status_total_cnt','status_repost_cnt','status_comment_cnt',
                   'status_like_cnt','status_comment_like_cnt', 'geo_enabled', 'verified', 'status_total_cnt', 'special_follow', 'uid']
    for column in num_columns:
        df[column] = df[column].apply(lambda x: textNumber2int(x))

    # 删除uid为-1（不是正确uid）的数据
    df.drop(df[df['uid']==-1].index, inplace=True)

    # 添加爬取时间列
    spider_time = path[path.find('-') + 1:path.find('.')]
    spider_time = change_datetime_type(spider_time, '%Y%m%d', '%Y-%m-%d')
    df['spider_time'] = spider_time

    print(df.head())
    # print(df.columns)
    # df.to_csv('format_data/'+friendship+'.csv', sep='\t', index=False)
    return df

def format_weibo(path):
    # path = 'last data/weibo.csv'
    df = pd.read_csv(path, sep='\t', low_memory=False)
    # 去掉content link列
    df.drop(columns=['content_link'], inplace=True)

    # 替换列名
    df.rename(columns={'nick':'screen_name', 'date':'created_at'}, inplace=True)

    # 替换列的int类型
    num_columns = ['forward_count', 'comment_count', 'like_count']
    for column in num_columns:
        df[column] = df[column].apply(lambda x: textNumber2int(x))


    # 添加爬取时间列
    spider_time = path[path.find('-') + 1:path.find('.')]
    spider_time = change_datetime_type(spider_time, '%Y%m%d', '%Y-%m-%d')
    df['spider_time'] = spider_time

    print(df.head())
    # print(df.columns)

    return df


def format_first_comment(path):
    # path = 'last data/first_comment.csv'
    df = pd.read_csv(path, sep='\t', low_memory=False)
    # 确保没有二级评论
    # print(df[df['comment_grade']==2])  #  empty
    # 删除评论级别列
    df.drop(columns=['comment_grade'], inplace=True)
    # 替换nan值
    df.fillna(value='', inplace=True)
    # 修改mid和comment_id为str
    df[['mid', 'comment_id']] = df[['mid', 'comment_id']].astype(str)
    # 将comment_id替换成整数id的str类型
    df['comment_id'] = df['comment_id'].apply(lambda x: x[:x.find('.')] if '.' in x else x)
    # 修改列名
    df.rename(columns={'date':'created_at', 'nick':'screen_name', }, inplace=True)
    # 删除创建时间格式不正确的数据
    df.drop(df[df['created_at'].apply(lambda x: validate_datetime(x, "%Y-%m-%d %H:%M:%S"))==False].index, inplace=True)
    # 将数据值替换成int
    df['floor_number'] = df['floor_number'].apply(lambda x: textNumber2int(x))
    df['reply_count'] = df['reply_count'].apply(lambda x: textNumber2int(x))
    df['like_count'] = df['like_count'].apply(lambda x: textNumber2int(x))
    df['weibo_count'] = df['weibo_count'].apply(lambda x: textNumber2int(x))
    df['verified_type'] = df['verified_type'].apply(lambda x: textNumber2int(x))
    df['verified_type_ext'] = df['verified_type_ext'].apply(lambda x: textNumber2int(x))
    df['mbtype'] = df['mbtype'].apply(lambda x: textNumber2int(x))
    df['urank'] = df['urank'].apply(lambda x: textNumber2int(x))
    df['mbrank'] = df['mbrank'].apply(lambda x: textNumber2int(x))
    df['followers_count'] = df['followers_count'].apply(lambda x: textNumber2int(x))
    df['fans_count'] = df['fans_count'].apply(lambda x: textNumber2int(x))


    # 添加爬取时间列
    spider_time = path[path.find('-') + 1:path.find('.')]
    spider_time = change_datetime_type(spider_time, '%Y%m%d', '%Y-%m-%d')
    df['spider_time'] = spider_time


    print(df.head())
    # print(df.columns)
    # df.to_csv('format_data/first_comment.csv', sep='\t', index=False)
    return df

def write2sql(user, passwd, df, table_name):
    engine = create_engine(f"mysql+pymysql://{user}:{passwd}@localhost/weibo?charset=utf8mb4")
    df.to_sql(table_name, engine, index=False, if_exists='append')

if __name__ == '__main__':
    # 数据库信息
    user = 'root'
    passwd = '123456'

    df = format_users_info('last data/users_info-20220502.csv')
    write2sql(user, passwd, df, 'user_info')
    print('finish users_info-20220502.csv')
    df = format_users_info('last data/users_info-20220514.csv')
    write2sql(user, passwd, df, 'user_info')
    print('finish users_info-20220514.csv')
    df = format_friend('last data/fans-20220504.csv', friendship='fans')
    write2sql(user, passwd, df, 'friend')
    print('finish fans-20220504.csv')
    df = format_friend('last data/followers-20220504.csv', friendship='followers')
    write2sql(user, passwd, df, 'friend')
    print('finish followers-20220504.csv')
    df = format_weibo('last data/weibo-20220510.csv')
    write2sql(user, passwd, df, 'weibo')
    print('finish weibo-20220510.csv')
    df = format_first_comment('last data/first_comment-20220515.csv')
    write2sql(user, passwd, df, 'first_comment')
    print('finish first_comment-20220515.csv')

