import os
from urllib import request, parse
from urllib.parse import parse_qs
from utils import S3Connector
import json

def lambda_handler(event, context):
    CLIENT_ID = os.environ.get('SLACK_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('SLACK_CLIENT_SECRET')
    s3_conn = S3Connector(
        os.environ.get('AWS_KEY'),
        os.environ.get('AWS_SECRET')
    )

    qs = parse_qs(event['rawQueryString'])
    access_code = qs['code'][0]
    print(f"Query string : {qs}")
    
    try:
        res = req_access_token(access_code, CLIENT_ID, CLIENT_SECRET)
    except Exception as e:
        print(f"Slack API Request Error : {e}")
        redirect_url = "https://www.sayulab.com/auwrn/failed"
        return {
            "statusCode" : 302,
            "headers" : {
                "Location" : redirect_url
            }
        }
    
    if (res["ok"] == False): #res에 error가 포함돼있을 경우
        print(f"Slack Access API Error : {res['error']}")
        redirect_url = "https://www.sayulab.com/auwrn/failed"
        return {
            "statusCode" : 302,
            "headers" : {
                "Location" : redirect_url
            }
        }

    """
        S3에 업로드
        token_type, bot_user_id, team_id 순으로 파일 생성
        생성한 파일을 S3에 업로드
    """
    authed_user_id = res['authed_user']['id']
    team_id = res['team']['id']
    path = f"access-token/{team_id}/{authed_user_id}"
    redirect_url = "https://www.sayulab.com/auwrn/welcome"
    s3_conn.upload_object(
        path=path,
        data=json.dumps(res)
    )

    return {
        "statusCode" : 302,
        "headers" : {
            "Location" : redirect_url
        },
    }

    

def req_access_token(code, client_id, client_secret):
    url = "https://slack.com/api/oauth.v2.access"
    data = parse.urlencode({
        "code" : code,
        "client_id" : client_id,
        "client_secret" : client_secret
    }).encode("utf-8")
    
    req = request.Request(url, data=data, method='POST')
    res = request.urlopen(req).read().decode("utf-8")
    return json.loads(res)