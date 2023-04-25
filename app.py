import os
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from config import *
from auwrn.generate_chat import ChatGenerator
from auwrn.view import home_view, get_tutorial_view
from auwrn.utils import S3Connector

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
    channel_id = event['channel']
    msg_text, msg_type = event['text'], event['type']
    print("EVENT: ", event)
    channel_type = event['channel_type']
    if channel_type == 'im': #오른과의 DM
        if '튜토리얼' in msg_text:
            user_list = app.client.users_list()['members']
            channel_list = app.client.conversations_list()['channels']
            dropdown_block = get_tutorial_view(user_list, channel_list)
            response = client.chat_postMessage(
                channel=channel_id,
                text = "연구노트를 설정해주세요",
                blocks = dropdown_block
            )
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
    print("interaction : ", payload)


# Start your app
if __name__ == "__main__":
    app.start(port=3000)