import os
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from config import *
from auwrn.generate_chat import ChatGenerator
from auwrn.view import home_view, get_tutorial_view
from auwrn.utils import S3Connector
import auwrn.tools as tool

# Initializes your app with your bot token and signing secret
app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)
chat_gen = ChatGenerator(OPENAI_ORG, OPENAI_KEY)
s3_conn = S3Connector(AWS_KEY, AWS_SECRET)

@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        client.views_publish(
        user_id=event["user"],
        view=home_view
    )
    except Exception as e:
      logger.error(f"Error publishing home tab: {e}")

@app.event("message")
def handle_message(client, event, logger):
    print("EVENT: ", event)
    channel_id = event['channel']
    msg_text, msg_type = event['text'], event['type']
    user_id, team_id = event['user'], event['team']
    channel_type = event['channel_type']

    if channel_type == 'im': #오른과의 DM
        team_list = s3_conn.get_list(f"team-{team_id}/")
        is_new_tm = tool.is_new_team(team_list)
        if is_new_tm:
            s3_conn.upload_object(path=f"team-{team_id}/user-{user_id}/", data='')
            tool.tutorial(app, client, channel_id, get_tutorial_view, team_id, user_id)
        else:
            service_user_list = s3_conn.get_list(f"team-{team_id}/user-{user_id}")
            is_new_ur = tool.is_new_user(service_user_list)
            if is_new_ur:
                s3_conn.upload_object(path=f"team-{team_id}/user-{user_id}/", data='')
                tool.tutorial(app, client, channel_id, get_tutorial_view, team_id, user_id)
            else:
                try:
                    msg_prompt = chat_gen.set_prompt(msg_text)
                    res_text = chat_gen.generate_text(msg_prompt)
                    result = client.chat_postMessage(
                        channel=channel_id,
                        text=res_text
                    )
                    print(result)
                except SlackApiError as e:
                    print(f"Error: {e}")

@app.block_action('button_click')
def handle_interaction(ack, payload):
    ack()
    block_id:str = payload['block_id']#TODO interaction 들어올 때 사용자 정보 업데이트
    if block_id.startswith("tutorial-reviewer"): #user 폴더에 있는 config.json 업데이트
        team_id, user_id = block_id.split(':')[1].split('-')
        
    elif block_id.startswith("tutorial-review-channel"):
        team_id, user_id = block_id.split(':')[1].split('-')
        print("BCD")
    elif block_id.startswith("tutorial-submit-button-clicked"):
        team_id, user_id = block_id.split(':')[1].split('-')
        print("CDE")
    print("interaction : ", payload)
    #interaction 받을 때마다 S3에 올리기.

# Start your app
if __name__ == "__main__":
    app.start(port=3000)