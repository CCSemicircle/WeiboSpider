import requests
import urllib
from utils.get_ip import proxy

def urlib(add, timeout, decoding='utf-8'):
    # 设置代理操作器
    proxy_operation = urllib.request.ProxyHandler(proxy.random_proxy())
    # 构建新的请求器，覆盖默认opener
    opener = urllib.request.build_opener(proxy_operation, urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)
    resp = urllib.request.urlopen(url=add, timeout=timeout).read().decode(decoding)
    return resp

def request(url, headers, timeout):
    resp = requests.get(url, headers=headers, timeout=10, proxies=proxy.random_proxy())
    return resp