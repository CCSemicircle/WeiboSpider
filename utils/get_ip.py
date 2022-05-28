import json
import requests
import re
import random
from utils.config import ip_api
from utils.TimeLogger import log


class Proxy:
    def __init__(self, ip_api):
        self.ip_api = ip_api
        # self.proxies = self._get_ip_from_api()

    def _get_ip_from_api(self):
        r = requests.get(url=self.ip_api)
        if json.loads(r.text)['code']:
            log('请添加 ip 白名单: {}'.format(r.text), save=True)
        ip_dicts = json.loads(r.text)['data']
        # print('ip_dicts', ip_dicts)
        proxies = []
        for ip_dict in ip_dicts:
            proxy = {
                'https': 'https://' + ip_dict['ip'] + ':' + str(ip_dict['port']),
                'http': 'http://' + ip_dict['ip'] + ':' + str(ip_dict['port'])
            }
            proxies.append(proxy)
        return proxies

    def _check_ip(self, proxy_dict):
        """对于一个代理IP，必须先测试ip是否可用"""
        # 判断ip是否可用, 不能去请求百度来验证，有可能是用本地ip请求的
        # http_url = 'http://ip.chinaz.com/getip.aspx'  # 失效
        # http_url = 'https://httpbin.org/ip'
        # http_url = 'http://httpbin.org/ip'
        # http_url = 'https://www.ip.cn/'
        # http_url = 'http://icanhazip.com/'
        http_url = 'https://ip.rtbasia.com/'
        try:

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
            response = requests.get(
                http_url, headers=headers, proxies=proxy_dict, timeout=2)
            print('response', response)
            response.raise_for_status()
            code = response.status_code
            print(proxy_dict)
            if code >= 200 and code < 300:
                text = response.text
                # print('text', text)
                for key, value in proxy_dict.items():
                    ip = re.match(r'.*://(.*?):\d+', value).group(1)
                    # print('ip', ip)
                    if ip in text:
                        return True
                    else:
                        return False
            else:
                return False
        except BaseException:
            # print('exception', BaseException)
            return False

    def random_proxy(self):
        # proxies = self._get_ip_from_api()
        # proxy_dict = random.choice(proxies)
        # # print('check ', self._check_ip(proxy_dict))
        # while not self._check_ip(proxy_dict):
        #     # print('check ', self._check_ip(proxy_dict))
        #     proxy_dict = random.choice(proxies)
        # # print('check ', self._check_ip(proxy_dict))
        #
        # print('get proxy', proxy_dict)
        # return proxy_dict
        pass  # todo


proxy = Proxy(ip_api)

if __name__ == '__main__':
    proxy = Proxy(ip_api)
    # print(proxy.proxies)
    # print(len(proxy.proxies))
    print(proxy.random_proxy())
