import requests
import urllib
from utils.get_ip import proxy

def urlib(add, timeout, decoding='utf-8'):
    # 设置代理操作器
    proxy_dict = proxy.random_proxy()
    proxy_operation = urllib.request.ProxyHandler(proxy_dict)
    # 构建新的请求器，覆盖默认opener
    opener = urllib.request.build_opener(proxy_operation, urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)
    # print('use proxy', proxy_dict)
    resp = urllib.request.urlopen(url=add, timeout=timeout).read().decode(decoding)
    # print('resp', resp)
    return resp

def request(url, headers, timeout):
    proxy_dict = proxy.random_proxy()
    # print('proxy ', proxy_dict)
    resp = requests.get(url, headers=headers, timeout=10, proxies=proxy_dict)
    return resp