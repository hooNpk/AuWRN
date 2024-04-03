import json
import os
from urllib import request, parse
from utils import S3Connector

def post_message_to_slack(response_text, channel_id, bot_token):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        'Authorization': f"Bearer {bot_token}",
        'Content-Type': 'application/json'
    }
    payload = json.dumps({
        'channel': channel_id,
        'text': response_text
    }).encode('utf-8')
    
    req = request.Request(
        url,
        data=payload,
        headers=headers
    )
    response = request.urlopen(req)
    response_data = response.read()

def lambda_handler(event, context):
    
    body = json.loads(event['body'])
    s3_conn = S3Connector(
        os.environ.get('AWS_KEY'),
        os.environ.get('AWS_SECRET')
    )
    print(f"Received Event: {event}")
    
    if 'challenge' in body: # Challenge 요청을 확인하고 응답
        return {
            'statusCode': 200,
            'body': json.dumps(
                {'challenge': body['challenge']}
            )
        }
    elif 'event' in body: # 메시지 이벤트 처리
        slack_event = body['event']
        event_type = slack_event['type']
        channel_type = slack_event['channel_type']
        
        #bot_token을 요청 보낸 사용자에 맞게 S3에서 받아온다.
        user_id = slack_event['user']
        team_id = slack_event['team']
        bot_access_token = s3_conn.get_object(
            f"access-token/{team_id}/{user_id}"
        )
        if(bot_access_token):
            bot_access_token = json.loads(bot_access_token)['access_token']
        else:
            response_text = f"인증이 제대로 되지 않았습니다. 오른을 워크 스페이스에 다시 임포트한 뒤 대화를 시도해주세요."
            post_message_to_slack(
                response_text,
                slack_event['channel'],
                bot_access_token
            )
            return {
                'statusCode': 200,
                'body': json.dumps('Event processed')
            }
        
        # 채널 메시지인 경우
        if event_type == 'message' and channel_type == 'im':
            user_id = slack_event['user']
            text = slack_event['text']
            
            # "안녕" 메시지에 대한 응답
            if text == 'hello':
                response_text = f"hello, <@{user_id}>님!"
                try:
                    post_message_to_slack(
                        response_text,
                        slack_event['channel'],
                        bot_access_token
                    )
                except Exception as e:
                    print(f"POST MESSAGE ERROR : {e}")
                
    return {
        'statusCode': 200,
        'body': json.dumps('Event processed')
    }