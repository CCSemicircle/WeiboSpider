from bs4 import BeautifulSoup
import json
from urllib import request
import urllib.parse
from utils.mysql import db

headers_ajax = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://v6.bang.weibo.com',
    'Connection': 'keep-alive',
    'Referer': 'https://v6.bang.weibo.com/czv/domainlist?date=202204&period_type=month',
}


def rankData2dic(date, period_type, field_id, field_name, rank_data):
    dic = dict()
    dic['date'] = date
    dic['period_type'] = period_type
    dic['field_id'] = field_id
    dic['field_name'] = field_name
    dic['uid'] = rank_data['uid']
    dic['screen_name'] = rank_data['screen_name']
    dic['score'] = rank_data['score']
    dic['curr_rank'] = rank_data['rank']
    dic['last_rank'] = rank_data['last_rank']
    dic['rank_up_down'] = rank_data['rank_up_down']
    return dic


def get_top_100(field_id, field_name, date, period_type, sql_table_name='top100'):
    """按照时间范围与时间类型爬取指定榜单博主"""
    finished_uid = []
    sql = f'select uid from {sql_table_name} where date="{date}" and period_type="{period_type}" and field_id={field_id}'
    # print('sql', sql)
    res = db.getAll(sql)
    if res:
        if len(res) >= 100:
            # 代表该榜单已经爬取结束
            return 0
        else:
            finished_uid = [dic['uid'] for dic in res]

    # 获得前20个
    url = "https://v6.bang.weibo.com/czv/%s?date=%s&period_type=%s" % (field_id, date, period_type)
    r = urllib.request.urlopen(url)
    soup = BeautifulSoup(r.read(), 'html.parser')

    items = soup.select("button.top-follow-btn")
    for item in items:
        rank_data = json.loads(item.attrs["share-data"])
        if 'rank_up_down' not in rank_data.keys():
            # 代表是“上榜新秀类”，为避免数据重复，删除
            continue
        if int(rank_data['uid']) in finished_uid:
            # 如果已经爬取该博主，直接跳过
            continue
        dic = rankData2dic(date, period_type, field_id, field_name, rank_data)
        db.insert_dict(dic, sql_table_name)

    # 获得后80个
    url = "https://v6.bang.weibo.com/aj/newczv/rank"
    for j in range(2, 6):
        data = {}
        data['page'] = str(j)
        data['show_rank'] = str(j * 20 - 20)
        data['period_type'] = period_type
        data['field_id'] = field_id
        data['dt'] = date

        datas = urllib.parse.urlencode(data).encode('utf-8')
        a = request.Request(url, data=datas, headers=headers_ajax)  # 一定要弄对header才能正确请求
        r = request.urlopen(a).read().decode('utf-8')
        r = json.loads(r)


        rank_list = r["data"]["rankData"]  # 数据格式 {'rank': data}
        for i in rank_list:
            rank_data = rank_list[i]
            if int(rank_data['uid']) in finished_uid:
                # 如果已经爬取该博主，直接跳过
                continue
            dic = rankData2dic(date, period_type, field_id, field_name, rank_data)
            db.insert_dict(dic, sql_table_name)

    return 0


def get_field_id(init_field_id, date, period_type):
    fields = []
    url = "https://v6.bang.weibo.com/czv/%s?date=%s&period_type=%s" % (init_field_id, date, period_type)
    r = urllib.request.urlopen(url)
    soup = BeautifulSoup(r.read(), 'html.parser')
    items = soup.select('div.m-tag-box.click-field')
    # print(items)
    for item in items:
        # print(item)
        field_id = item.attrs['data-field-id']
        field_name = item.find('b').string
        fields.append({'field_id': field_id, 'field_name': field_name})

    return fields


if __name__ == '__main__':
    init_field_id = '1001'
    date = "20220418"
    period_type = 'week'
    fields = get_field_id(init_field_id, date, period_type)
    top_100 = []
    n = len(fields)
    for i in range(n):
        field = fields[i]
        res = get_top_100(field['field_id'], field['field_name'], date, period_type, 'top100')
        print('finish {} field, current progress: {} %'.format(field['field_name'], (i+1)/n*100))
        break
