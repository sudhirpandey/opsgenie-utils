import requests
import json
import os
import time

access_token = os.environ.get('ACCESS_TOKEN', None)
api_server = "https://api.opsgenie.com"

if not access_token:
    raise ValueError('You must have "ACCESS_TOKEN" env variable')

def requestWrapper(func, **kwargs):
    attempt=1
    max_attempt=10
    headers = {'Authorization': 'GenieKey ' + access_token, 'Content-Type': 'application/json'}
    url=api_server
    params=None
    data=None
    for key, val in kwargs.items():
        if key == "endpoint":
            url+=val
        if key == "data":
            data=json.dumps(val)
        if key == "params":
            params=val
    response=func(url,headers=headers, params=params,data=data)
    while response.status_code == 429 and attempt <= max_attempt:
        sleep_time_secs=attempt*0.5
        time.sleep(sleep_time_secs)
        attempt+=1
        response = func(url,headers=headers, params=params,data=data)
    return response


def getResource(endpoint,params={}):
    response=requestWrapper(requests.get,endpoint=endpoint,params=params)
    return response

def patchResource(endpoint,payload,params={}):
    response=requestWrapper(requests.patch,endpoint=endpoint, data=payload, params=params)
    return response


def deleteResource(endpoint,params={}):
    response=requestWrapper(requests.delete,endpoint=endpoint, params=params)
    return response
