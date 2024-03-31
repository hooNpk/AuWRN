import json
import os
import requests
from urllib.parse import parse_qs

def lambda_handler(event, context):
    CLIENT_ID = os.environ.get('SLACK_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('SLACK_CLIENT_SECRET')

    qs = parse_qs(event['rawQueryString'])
    access_code = qs['code']
    res = req_access_token(access_code, CLIENT_ID, CLIENT_SECRET)
    
    #S3에 업로드

    redirect_url = "https://www.sayulab.com/auwrn/welcome"
    return {
        "statusCode" : 302,
        "headers" : {
            "Location" : redirect_url
        },
    }

def req_access_token(code, client_id, client_secret):
    url = "https://slack.com/api/oauth.v2.access"
    payload = {
        "code" : code,
        "client_id" : client_id,
        "client_secret" : client_secret
    }
    
    res = requests.post(url, data=payload)
    print(res.json())
    return res.json()