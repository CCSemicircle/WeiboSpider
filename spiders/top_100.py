from bs4 import BeautifulSoup
import json
import pandas as pd
from urllib import request
import urllib.parse

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


def get_top_100(field_id, field_name, date, period_type):
    data_top_100 = []
    # 获得前20个
    url = "https://v6.bang.weibo.com/czv/%s?date=%s&period_type=%s" % (field_id, date, period_type)
    r = urllib.request.urlopen(url)
    soup = BeautifulSoup(r.read())

    # r = requests.get("https://v6.bang.weibo.com/czv/domainlist?date=%s&period_type=month" % date)
    # soup = BeautifulSoup(r.text)

    items = soup.select("button.top-follow-btn.following-btn")
    for item in items:
        # print(item)
        try:
            item.attrs["data-type"]
        except:
            dic = {}
            data_json = json.loads(item.attrs["share-data"])
            dic['field_id'] = field_id
            dic['field_name'] = field_name
            dic["rank"] = data_json["rank"]
            dic["uid"] = data_json["uid"]
            dic["screen_name"] = data_json["screen_name"]
            data_top_100.append(dic)
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

        # r = requests.post(url, headers=headers_ajax, data=data).json()

        rankData = r["data"]["rankData"]
        for i in rankData:
            dic = {}
            dic['field_id'] = field_id
            dic['field_name'] = field_name
            dic["rank"] = rankData[i]["rank"]
            dic["uid"] = rankData[i]["uid"]
            dic["screen_name"] = rankData[i]["screen_name"]
            data_top_100.append(dic)
    # print(data_top_100)
    return data_top_100


def get_field_id(init_field_id, date, period_type):
    fields = []
    url = "https://v6.bang.weibo.com/czv/%s?date=%s&period_type=%s" % (init_field_id, date, period_type)
    r = urllib.request.urlopen(url)
    soup = BeautifulSoup(r.read())
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
        data = get_top_100(field['field_id'], field['field_name'], date, period_type)
        print('finish {} field, current progress: {} %'.format(field['field_name'], i/n*100))
        top_100.extend(data)
    # data = get_top_100(field_id, date, period_type )
    df = pd.DataFrame(top_100)
    df.to_csv('top_100.csv', encoding="utf_8_sig", index=False)
