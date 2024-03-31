import json
import os
from urllib import request, parse
 

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
    
    req = request.Request(url, data=payload, headers=headers)
    response = request.urlopen(req)
    response_data = response.read()

def lambda_handler(event, context):
    bot_token = os.environ.get('BOT_TOKEN')
    body = json.loads(event['body'])
    print(f"Received body: {body}")
    
    # Challenge 요청을 확인하고 응답
    if 'challenge' in body:
        return {
            'statusCode': 200,
            'body': json.dumps({'challenge': body['challenge']})
        }
    # 메시지 이벤트 처리
    elif 'event' in body:
        slack_event = body['event']
        event_type = slack_event['type']
        channel_type = slack_event['channel_type']
        
        # 채널 메시지인 경우
        if event_type == 'message' and channel_type == 'im':
            user_id = slack_event['user']
            text = slack_event['text']
            
            # "안녕" 메시지에 대한 응답
            if text == 'hello':
                response_text = f"hello, <@{user_id}>님!"
                post_message_to_slack(response_text, slack_event['channel'], bot_token)
                
    return {
        'statusCode': 200,
        'body': json.dumps('Event processed')
    }