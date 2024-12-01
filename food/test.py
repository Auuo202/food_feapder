import re
import json
from urllib.parse import urlparse, urlunparse




def full_url(base_url, href_url):
    # 使用urlparse解析URL
    parsed_url = urlparse(base_url)
    # 构造基础URL，只保留scheme（协议）、netloc（网络位置）和（可选的）params（参数，但通常不使用）
    base_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))

    if not href_url.startswith(("http://", "https://")):
        # 如果href是相对路径，进行拼接
        full_url = f"{base_url}/{href_url}"
    else:
        # 如果href是绝对路径，直接使用
        full_url = href_url
    return full_url

url = input('网址')