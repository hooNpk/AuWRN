import os
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from config import *
from auwrn.generate_chat import ChatGenerator
from auwrn.utils import S3Connector
from auwrn.view import home_view
from auwrn.log import ProductionLogConfig, DevelopmentLogConfig
import auwrn.tools as tool
import json
from loguru import logger

# Initializes your app with your bot token and signing secret
logger.remove()
log_config = DevelopmentLogConfig()
logger.configure(**log_config.LOGURU_SETTINGS)
app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)
chat_gen = ChatGenerator(OPENAI_ORG, OPENAI_KEY)
s3_conn = S3Connector(AWS_KEY, AWS_SECRET)
REQ_SGNTRE = False

@app.event("app_home_opened")
def update_home_tab(client, event):
    try:
        client.views_publish(
        user_id=event["user"],
        view=home_view
    )
    except Exception as e:
      logger.error(f"Error publishing home tab: {e}")

@app.event("message")
def handle_message(client, event):
    logger.info(f"MESSAGE EVENT: {event}")
    
    event_type = event['type']
    channel_type = event['channel_type']

    if channel_type == 'im': #오른과의 기본 DM
        if 'subtype' in event.keys():
            sub_type = event['subtype']
            if sub_type == 'file_share' and REQ_SGNTRE:
                files = event['files']
                channel_id = event['channel']
                tool.upload_image(files, s3_conn)
                res_text = "정상적으로 등록됐습니다! :smile:\n이제 오른과 자유롭게 대화하면서 연구 인사이트를 얻고 연구노트를 생성해보세요!"
                result = client.chat_postMessage(
                    channel=channel_id,
                    text=res_text
                )
        else:
            channel_id = event['channel']
            user_id, team_id = event['user'], event['team']
            msg_text = event['text']
            is_new_tm = tool.is_new_team(s3_conn, team_id)
            if is_new_tm:
                s3_conn.upload_object(path=f"team-{team_id}/user-{user_id}/config.json", data=json.dumps({}))
                #TODO 요금제 등록.
                tool.tutorial(app, channel_id, team_id, user_id)
            else:
                is_new_ur = tool.is_new_user(s3_conn, team_id, user_id)
                if is_new_ur:
                    s3_conn.upload_object(path=f"team-{team_id}/user-{user_id}/config.json", data=json.dumps({}))
                    tool.tutorial(app, channel_id, team_id, user_id)
                else:
                    try:
                        msg_prompt = chat_gen.set_prompt(msg_text)
                        res_text = chat_gen.generate_text(msg_prompt)
                        result = client.chat_postMessage(
                            channel=channel_id,
                            text=res_text
                        )
                    except SlackApiError as e:
                        logger.error(f"Error: {e}")
    else:
        print("ABC")

# 3. 대화를 통해 연구노트 작성하도록 하기.
@app.block_action('button_click')
def handle_interaction(ack, payload):
    ack()
    logger.info(f"interaction : {payload}")
    block_id:str = payload['block_id']
    if block_id.startswith("tutorial-reviewer"):
        team_id, user_id = block_id.split(':')[1].split('-')
        reviewer_name, reviewer_id = payload['selected_option']['text']['text'], payload['selected_option']['value']
        tool.update_user_config(
            {"team_id":team_id, "user_id":user_id},
            s3_conn,
            {"reviewName":reviewer_name, "reviewerId":reviewer_id}
        )
    elif block_id.startswith("tutorial-review-channel"):
        team_id, user_id = block_id.split(':')[1].split('-')
        channel_name, channel_id = payload['selected_option']['text']['text'], payload['selected_option']['value']
        tool.update_user_config(
            {"team_id":team_id, "user_id":user_id},
            s3_conn,
            {"channelName":channel_name, "channelId":channel_id}
        )
    elif block_id.startswith("tutorial-org"):
        team_id, user_id = block_id.split(':')[1].split('-')
        user_org = payload['value']
        tool.update_user_config(
            {"team_id":team_id, "user_id":user_id},
            s3_conn,
            {"organization":user_org}
        )
    elif block_id.startswith("tutorial-project"):
        team_id, user_id = block_id.split(':')[1].split('-')
        user_proj = payload['value']
        tool.update_user_config(
            {"team_id":team_id, "user_id":user_id},
            s3_conn,
            {"projectName":user_proj}
        )
        
    elif block_id.startswith("tutorial-submit-button-clicked"):
        team_id, user_id, channel_id = block_id.split(':')[1].split('-')
        #TODO Config 제대로 들어가 있는지 확인
        global REQ_SGNTRE
        REQ_SGNTRE = True
        tool.tutorial2(app, channel_id)
    

# Start your app
if __name__ == "__main__":
    app.start(port=3000)