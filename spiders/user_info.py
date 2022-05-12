import json
import re
from urllib import request
import urllib
import chardet
from utils.config import cookie
import requests
from utils.mysql import db
from utils import helper

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    # 'Accept-Encoding': 'gzip, deflate, br',  # 这里是设置返回的编码，一般不需要设置
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://weibo.com',
    'refer': 'https://img.t.sinajs.cn/t6/style/css/module/base/frame.css?version=895020bb',
    'Connection': 'keep-alive',
    'Host': 'weibo.com',
    'Cookie': cookie
}


def get_user_info(uid, sql_table_name='user_info'):
    """获取用户个人信息"""
    sql = f'select uid from {sql_table_name} where uid={uid}'
    res = db.getOne(sql)
    # todo
    # if res:
    #     # 如果存在，代表改用户信息已经爬取，可以直接返回
    #     return 0

    dic = {}
    # headers = config.get_headers()
    add = urllib.request.Request(url="https://weibo.com/%s?is_hot=1" % (uid), headers=headers)
    main_page = urllib.request.urlopen(url=add, timeout=20).read().decode(encoding="utf-8")

    dic['uid'] = uid

    # 大V认证
    grade = {'approve': '黄V', 'approve_co': '蓝V', 'approve_gold': '红V'}
    authentication_grade_info = re.findall(r'title=.*?class=\\"W_icon icon_pf_(.*?)\\"', main_page)
    if authentication_grade_info:
        authentication_grade = grade[authentication_grade_info[0]] if authentication_grade_info[0] in grade.keys() else '其他'
    else:
        authentication_grade = None
    dic['authentication_grade'] = authentication_grade

    if authentication_grade == '蓝V':
        # 蓝V认证的信息界面链接不同
        add = urllib.request.Request(url="https://weibo.com/%s/about" % (uid), headers=headers)
        info_page = urllib.request.urlopen(url=add, timeout=20).read().decode('utf-8')

        # 基本信息
        screen_name = re.findall(r'<h1 class=\\"username\\">(.*?)<\\/h1>', info_page)
        intro = re.findall(r'<p class=\\"p_txt\\">(.*?)<\\/p>', info_page)
        industry_category = re.findall(r'行业类别<\\/span>(.*?)<\\/span>', info_page)

        dic['screen_name'] = screen_name[0] if screen_name else None
        dic['intro'] = intro[0] if intro else None
        dic['industry_category'] = industry_category[0].replace(" ", "").replace("\\r\\n", "").replace("\\t", "") if industry_category else None

        # 微博认证
        authentication = re.findall(r'<div class=\\"pf_intro\\" title=\\"(.*?)\\">', info_page)
        dic['authentication'] = authentication[0] if authentication else None

        # 会员信息
        vip_rank = re.findall(r'W_icon icon_member(\d*)', info_page)
        growth_value = re.findall(r'成长值：.*?<span.*?>(\d*)<\\/span>', info_page)
        dic['growth_value'] = growth_value[0] if growth_value else None
        dic['vip_rank'] = vip_rank[0] if vip_rank else None

        # 蓝V认证info界面没有关注个数等信息，需要在主界面获取
        follower_num = re.findall(r'<strong.*?>(\d*\.?\d+?.?)<\\/strong>.*?<span class=\\"S_txt2\\">关注', main_page)
        fans_num = re.findall(r'关注.*?<strong.*?>(\d*\.?\d+?.?)<\\/strong>.*?<span class=\\"S_txt2\\">粉丝', main_page)
        post_num = re.findall(r'粉丝.*?<strong.*?>(\d*\.?\d+?.?)<\\/strong>.*?<span class=\\"S_txt2\\">微博', main_page)

        dic["follower_num"] = helper.textNumber2int(follower_num[0]) if follower_num else None
        dic["fans_num"] = helper.textNumber2int(fans_num[0]) if fans_num else None
        dic["post_num"] = helper.textNumber2int(post_num[0]) if post_num else None

    else:
        try:
            page_id = re.findall(r'\$CONFIG\[\'page_id\']=\'(\d+)\'', main_page)[0]
        except:
            return -1
        add = urllib.request.Request(url="https://weibo.com/p/%s/info" % (page_id), headers=headers)
        info_page = urllib.request.urlopen(url=add, timeout=20).read().decode('utf-8')

        # 基本信息
        screen_name = re.findall(r'昵称：.*?<span class=\\"pt_detail\\">(.*?)<\\/span>', info_page)
        location = re.findall(r'所在地：.*?<span class=\\"pt_detail\\">(.*?)<\\/span>', info_page)
        sex = re.findall(r'性别：.*?<span class=\\"pt_detail\\">(.*?)<\\/span>', info_page)
        sexual_orientaion = re.findall(r'性取向：.*?<span class=\\"pt_detail\\">(.*?)<\\/span>', info_page)
        marriage = re.findall(r'感情状况：.*?<span class=\\"pt_detail\\">(.*?)<\\/span>', info_page)
        birthday = re.findall(r'生日：.*?<span class=\\"pt_detail\\">(.*?)<\\/span>', info_page)
        blood_type = re.findall(r'血型：.*?<span class=\\"pt_detail\\">(.*?)<\\/span>', info_page)
        blog = re.findall(r'博客：.*?<a href=\\".*?\\">(.*?)<\\/a>.*?<\\/li>', info_page)
        style_domain = re.findall(r'个性域名：.*?<a href=\\".*?\\">(.*?)<\\/a>.*?<\\/li>', info_page)
        intro = re.findall(r'简介：.*?<span class=\\"pt_detail\\">(.*?)<\\/span>', info_page)
        regist_time = re.findall(r'注册时间：.*?<span class=\\"pt_detail\\">(.*?)<\\/span>', info_page)

        dic['screen_name'] = screen_name[0].replace(" ", "").replace("\\r\\n", "") if screen_name else None
        dic['location'] = location[0].replace("\\r\\n", "") if location else None
        dic['sex'] = sex[0].replace(" ", "").replace("\\r\\n", "") if sex else None
        dic['sexual_orientation'] = sexual_orientaion[0].replace(" ", "").replace("\\r\\n", "") if sexual_orientaion else None
        dic['marriage'] = marriage[0].replace(" ", "").replace("\\r\\n", "") if marriage else None
        dic['birthday'] = birthday[0].replace(" ", "").replace("\\r\\n", "") if birthday else None
        dic['blood_type'] = blood_type[0].replace(" ", "").replace("\\r\\n", "") if blood_type else None
        dic['blog'] = blog[0].replace(" ", "").replace("\\r\\n", "").replace('\/', '/') if blog else None
        dic['style_domain'] = style_domain[0].replace(" ", "").replace("\\r\\n", "").replace('\/', '/')  if style_domain else None
        dic['intro'] = intro[0].replace(" ", "").replace("\\r\\n", "") if intro else None
        dic['regist_time'] = regist_time[0].replace(" ", "").replace("\\r\\n", "") if regist_time else None

        # ip属地
        ip_region = re.findall(r'IP属地.*?<span class=\\"pt_detail ipRegion\\">(.*?)<span class=\\"W_icon icon_askS\\">', info_page)
        dic['ip_region'] = ip_region[0] if ip_region else None

        # 微博认证
        authentication = re.findall(r'<div class=\\"pf_intro\\" title=\\"(.*?)\\">', info_page)
        dic['authentication'] = authentication[0] if authentication else None

        # 工作信息
        company = re.findall(r'公司：.*?<span class=\\"pt_detail\\">.*?<a href=\\".*?\\">(.*?)<\\/a>(.*?)<\\/span>', info_page)
        dic['company'] = "".join(list(company[0])).replace(" ", "").replace("\\r\\n", "").replace("<br\/>", " ") if company else None

        # 教育信息
        university = re.findall(r'大学：.*?<span class=\\"pt_detail\\">.*?<a href=\\".*?\\">(.*?)<\\/a>(.*?)<\\/span>', info_page)
        dic['university'] = "".join(list(university[0])).replace(" ", "").replace("\\r\\n", "").replace("<br\/>", " ") if university else None

        # 标签
        tags = re.findall(r'<a target=\\"_blank\\" node-type=\\"tag\\".*?<\\/span>(.*?)<\\/a>', info_page)
        if tags:
            tags = [tag.replace(" ", "").replace("\\r\\n", "") for tag in tags]
            tags = ",".join(tags)
        dic['tags'] = tags if tags else None

        # 粉丝、关注、微博数
        follower_num = re.findall(r'<strong.*?>(\d*\.?\d+?.?)<\\/strong>.*?<span class=\\"S_txt2\\">关注', info_page)
        fans_num = re.findall(r'关注.*?<strong.*?>(\d*\.?\d+?.?)<\\/strong>.*?<span class=\\"S_txt2\\">粉丝', info_page)
        post_num = re.findall(r'粉丝.*?<strong.*?>(\d*\.?\d+?.?)<\\/strong>.*?<span class=\\"S_txt2\\">微博', info_page)

        dic["follower_num"] = helper.textNumber2int(follower_num[0]) if follower_num else None
        dic["fans_num"] = helper.textNumber2int(fans_num[0]) if fans_num else None
        dic["post_num"] = helper.textNumber2int(post_num[0]) if post_num else None


        # 会员信息
        vip_rank = re.findall(r'W_icon icon_member(\d*)', info_page)
        growth_value = re.findall(r'成长值：.*?<span.*?>(\d*)<\\/span>', info_page)
        dic['growth_value'] = int(growth_value[0]) if growth_value else None
        dic['vip_rank'] = int(vip_rank[0]) if vip_rank else None


    # print(dic)

    db.insert_dict(dic, sql_table_name)

    return 0


if __name__ == '__main__':
    uids = [1906123125, 5184087910, 6105713761, 3929704484]
    # uids = ["6105713761"]
    data = []
    for uid in uids:
        res = get_user_info(uid, sql_table_name='user_info')
        # data.append(get_infos(uid))
    # df = pd.DataFrame(data)
    # df.to_csv('user_info_sample.csv', index=False, encoding='utf_8_sig')
