#!/usr/bin/env python

import os
import re

files = [f for f in os.listdir('.') if f.endswith('.html')]
for f in files:
    if f == 'index.html':
        continue;
    html = open(f, 'r').read()
    html = html.replace('\'', '"')
    html = html.replace('\n', '')
    html = re.sub(">[^\w]+<", "><", html)
    jsonp = 'meddb.callback(\''+html+'\');\n'
    open(f.replace('.html','.jsonp'),'w').write(jsonp)
