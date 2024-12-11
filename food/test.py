import re
import json
from urllib.parse import urlparse, urlunparse

class_a = "a[href]"
tag_name = class_a.split('[')[0]
attr_name = class_a.split('[')[1].split(']')[0]

print(tag_name)
print(attr_name)
