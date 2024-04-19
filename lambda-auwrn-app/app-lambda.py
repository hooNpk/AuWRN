import json
import os
from utils import S3Connector
from slack_api import post_to_slack
from generate_chat import generate_text
import view
import base64
from urllib import parse

def lambda_handler(event, context):
    print(f"Received Event: {event}")
    if event['isBase64Encoded']:
        decoded_str = base64.b64decode(event['body']).decode('utf-8')
        body = json.loads(
            parse.parse_qs(decoded_str)['payload'][0]
        )
    else:
        body = json.loads(event['body'])
    print(f"Received Body : {body}")

    s3_conn = S3Connector(
        os.environ.get('AWS_KEY'),
        os.environ.get('AWS_SECRET')
    )
    
    if 'challenge' in body: # Challenge 요청을 확인하고 응답
        return {
            'statusCode': 200,
            'body': json.dumps(
                {'challenge': body['challenge']}
            )
        }
    elif 'event' in body: # 메시지 이벤트 처리
        slack_event = body['event']
        team_id = body['team_id']
        event_type = slack_event['type']
        ch_id = slack_event['channel']
        
        #bot_token을 요청 보낸 사용자에 맞게 S3에서 받아온다.
        user_id = slack_event['user']
        
        bot_access_token = s3_conn.get_object(
            f"access-token/{team_id}/{user_id}"
        )
        if(bot_access_token):
            bot_access_token = json.loads(bot_access_token)['access_token']
        else:
            response_text = f"인증이 제대로 되지 않았습니다. 오른을 워크 스페이스에 다시 임포트한 뒤 대화를 시도해주세요."
            post_to_slack(
                bot_access_token,
                json.dumps({
                    'channel' : ch_id,
                    'text' : response_text
                }).encode('utf-8')
            )
            return {
                'statusCode': 200,
                'body': json.dumps('Event processed')
            }
        
        if event_type == "app_home_opened":#app_home을 열었음
            if s3_conn.is_new_user(team_id, user_id): #새로운 유저
                s3_conn.upload_object(
                    path=f"org-list/team-{team_id}/user-{user_id}/config.json",
                    data = json.dumps({})
                )
                user_list = json.loads(post_to_slack( #유저 리스트 받음
                    bot_access_token,
                    {},
                    req_type = "user_list"
                ))['members']
                tutorial_block = view.get_tutorial_view(
                    user_list,
                    {'team_id':team_id, 'user_id':user_id, 'channel_id':ch_id}
                )
                post_to_slack(
                    bot_access_token,
                    json.dumps({
                        'channel' : ch_id,
                        'text' : '연구노트 작성 설정',
                        'blocks' : tutorial_block
                    }).encode('utf-8')
                )

        # 채널 메시지인 경우
        elif event_type == 'message' and ch_id.startswith('D'):
            user_id = slack_event['user']
            text = slack_event['text']
            
            # "사랑해" 메시지에 대한 응답
            if text == '사랑해':
                response_text = f"고맙습니다. 저도 사랑해요, <@{user_id}>님!"
            else:
                response_text = generate_text(
                    [{"role": "user", "content":text}]
                )
            try:
                post_to_slack(
                    bot_access_token,
                    json.dumps({
                        'channel' : ch_id,
                        'text' : response_text
                    }).encode('utf-8')
                )
            except Exception as e:
                print(f"POST MESSAGE ERROR : {e}")


    elif 'actions' in body: #button interaction
        block = body['actions'][0]
        block_id:str = block['block_id']
        team_id, user_id = body['team']['id'], body['user']['id']

        bot_access_token = s3_conn.get_object(
            f"access-token/{team_id}/{user_id}"
        )
        if(bot_access_token):
            bot_access_token = json.loads(bot_access_token)['access_token']
        else:
            response_text = f"인증이 제대로 되지 않았습니다. 오른을 워크 스페이스에 다시 임포트한 뒤 대화를 시도해주세요."
            post_to_slack(
                bot_access_token,
                json.dumps({
                    'channel' : ch_id,
                    'text' : response_text
                }).encode('utf-8')
            )
            return {
                'statusCode': 200,
                'body': json.dumps('Event processed')
            }
        if block_id.startswith("tutorial-reviewer"):
            team_id, user_id = block_id.split(':')[1].split('-')
            reviewer_id = block['selected_option']['value']
            s3_conn.update_user_config(
                team_id,
                user_id,
                {"reviewerId":reviewer_id}
            )
        elif block_id.startswith("tutorial-org"):
            team_id, user_id = block_id.split(':')[1].split('-')
            user_org = block['value']
            s3_conn.update_user_config(
                team_id,
                user_id,
                {"organization":user_org}
            )
        elif block_id.startswith("tutorial-project"):
            team_id, user_id = block_id.split(':')[1].split('-')
            user_proj = block['value']
            s3_conn.update_user_config(
                team_id,
                user_id,
                {"projectName":user_proj}
            )
        elif block_id.startswith("tutorial-submit-button-clicked"):
            
            team_id, user_id, ch_id = block_id.split(':')[1].split('-')
            info_cfg = json.loads(s3_conn.get_object(
                f"org-list/team-{team_id}/user-{user_id}/config.json"
            ))

            check_list = {
                    "reviewerId":"연구노트 검토자",
                    "organization" : "연구 기관",
                    "projectName" : "연구 과제 제목"
                }
            not_list = []
            for check, val in check_list.items():
                if check not in info_cfg:
                    not_list.append(val)

            if not not_list: # config 가 잘 채워졌는지 확인
                tutorial_block = view.get_tutorial2_view()
                post_to_slack(
                    bot_access_token,
                    json.dumps({
                        'channel' : ch_id,
                        'text' : '연구노트 작성 설정',
                        'blocks' : tutorial_block
                    }).encode('utf-8')
                )
            else: 
                response_text = f" {', '.join(not_list)} 설정이 되지 않았습니다. 위의 모달에서 설정을 완료해주세요"
                post_to_slack(
                    bot_access_token,
                    json.dumps({
                        'channel' : ch_id,
                        'text' : response_text
                    }).encode('utf-8')
                )

    return {
        'statusCode': 200,
        'body': json.dumps('Event processed')
    }