import requests
import re
from urllib import request
import urllib
import pandas as pd


def get_follow_fan(uid):
    # 通过Fiddler抓包获取
    Cookie = "SINAGLOBAL=7375786211741.83.1627383159125; SCF=Ajo_ET5PNFfYaqVN4Ypt3SlEk4X91WkP_jV4xT9JwG2HILuP9hZMWl67-04e4O0fvFEqWFjJ71YUWJqnADMALgM.; XSRF-TOKEN=SheIKNCFe1iECSvqmLhyu8fW; _s_tentry=-; Apache=2006908061472.752.1651368643720; ULV=1651368643745:9:2:2:2006908061472.752.1651368643720:1651368240270; SSOLoginState=1651368709; SUB=_2A25PaZNVDeRhGeBL7FAQ8SjIyTqIHXVslT0drDV8PUJbkNAfLVTskW1NRvZWX51PzV0vtEX_bJMq3CBr618Q-gfY; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFMW7Aw6AkqLeq9RKFpEjcS5NHD95QcSKMEeK2cShzcWs4DqcjNi--Xi-zRiKn7i--fi-20i-zci--ci-zRiKnfi--RiKyhi-zci--4iKnfiK.EKbH8Sb-4xFHWxntt; UOR=www.google.com,s.weibo.com,passport.weibo.cn; WBPSESS=Dt2hbAUaXfkVprjyrAZT_NvXmU4UgGwqug9qoWC9A6HLzNP1-GvaPKGlY84SmGQeHsFRKfnJYppp8BAjKXonH5BfEt_v3junpfBijgpAOGg9Utbo83VmRdjHh9jHuknrcieEVE72tSKGaji92VbsFWcSLp2bAtWQqoHXQmARsA0kb2FGjuxD7lOvp8njv_Pjr3jw5xwJPTHwkMJlnzeG7g==; PC_TOKEN=19c7963bcf; wvr=6; wb_view_log_6572116426=1920*10801; webim_unReadCount=%7B%22time%22%3A1651375688220%2C%22dm_pub_total%22%3A0%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A33%2C%22msgbox%22%3A0%7D; _dd_s=logs=1&id=bdbc9643-4def-4597-82e1-592bbf27a15c&created=1651372475412&expire=1651376617556"

    headers = {
        'authority': 'weibo.com',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'cache-control': 'max-age=0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        # 'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        # 'Accept-Encoding': 'gzip, deflate, br',  # 这里是设置返回的编码，一般不需要设置
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
        'Connection': 'keep-alive',
        'Host': 'weibo.com',
        'accept-language': 'zh-CN,zh;q=0.9',
        'Cookie': Cookie
    }


    add = urllib.request.Request(url='https://weibo.com/%s?is_hot=1' % uid, headers=headers)
    r = urllib.request.urlopen(url=add, timeout=10).read().decode('utf-8')
    print('r', r)

    p_id = re.findall(r'CONFIG\[\'page_id\']=\'(\d+)\'', r)[0]

    # 其他用户最多查看5页粉丝或关注列表
    num_page = 1 # todo
    for i in range(1, num_page+1):
        # 获取关注用户
        add = urllib.request.Request(url='https://weibo.com/p/%s/follow?page=%d' % (p_id, i), headers=headers)
        follow_page = urllib.request.urlopen(url=add, timeout=10).read().decode('utf-8')    # 注意改为utf-8，原来是unicode_escape

        follows = re.findall(r'action-type=\\"itemClick\\" action-data=\\"uid=(\d+)&fnick=(.*?)&', follow_page)
        print("关注：")
        print(follows)
        follows_data = [{'uid': uid, 'follows_id': follow[0], 'follows_nick': follow[1]} for follow in follows]

        # 获取粉丝用户
        add = urllib.request.Request(url='https://weibo.com/p/%s/follow?relate=fans&page=%d' % (p_id, i),
                                     headers=headers)
        fans_page = urllib.request.urlopen(url=add, timeout=10).read().decode('utf-8')  # 注意改为utf-8
        fans = re.findall(r'action-type=\\"itemClick\\" action-data=\\"uid=(\d+)&fnick=(.*?)&', fans_page)
        print("粉丝：")
        print(fans)
        fans_data = [{'uid': uid, 'fans_id': fan[0], 'fans_nick': fan[1]} for fan in fans]

        return follows_data, fans_data


if __name__ == '__main__':
    follows_data, fans_data = get_follow_fan("337558589")
    follows_df = pd.DataFrame(follows_data)
    fans_df = pd.DataFrame(fans_data)
    follows_df.to_csv('follows.csv', index=False, encoding='utf_8_sig')
    fans_df.to_csv('fans.csv', index=False, encoding='utf_8_sig')