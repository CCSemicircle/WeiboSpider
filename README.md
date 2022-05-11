# 微博爬虫

## 功能介绍

1. 爬取”V影响力“榜单博主
2. 爬取用户个人信息
3. 爬取用户关注与粉丝列表
4. 爬取用户指定时间区间内的微博
5. 爬取微博的一、二级评论

## 运行代码

```python
# 示例
python WeiboSpider.py --top_100_date "2022-04-18" --top_100_type "week" --friend_num 2000 --weibo_start_date "2022-04-29" --weibo_end_date "2022-05-01" --thread_num 4
```
## 参数说明

> 注意：以下参数没有设置默认值的都是必须在输入运行代码（如上示例）时添加
- top_100_type：榜单类型，可选"week"或"month"，默认"week"
- top_100_date：榜单日期，如果top_100_type为"week"，格式为"YYYY-mm-dd"，如果top_100_type为"month"，格式为"YYYY-mm"
- friend_num：粉丝与关注的爬取数量，设置过大可能无法获取，默认2000
- weibo_start_date：微博时间范围的起始时间，格式为"YYYY-mm-dd"，**包括这天当天**
- weibo_end_date：微博时间范围的终止时间，格式为"YYYY-mm-dd"，**包括这天当天**
- thread_num：同时运行的多线程个数

## 注意事项
- 在运行之前，先运行创建数据库，并且执行sql文件夹下的weibo.sql文件以创建数据表
- 在运行之间在utils文件夹下创建config.py文件，配置好cookie与ip_api
```python
# utils/config.py
cookie = ""

user_agent = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]

ip_api = ""

mysql_info = {
    'host': 'localhost',
    'user': 'root',
    'passwd': '123456'
}
```
- 支持IP代理，需要设置ip动态获取api，即ip_api，推荐品易IP代理（利益无关，本人尝试过感觉还行）
- 代码各部分均设置了识别已经爬取内容，如果因为意外中止了爬取，重新运行即可，无须修改运行参数
