import os
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from config import *
from auwrn.utils import ChatGenerator


# Initializes your app with your bot token and signing secret
app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)
chat_gen = ChatGenerator(OPENAI_ORG, OPENAI_KEY)

@app.event("app_home_opened")
def update_home_tab(client, event, logger):
  try:
    # views.publish is the method that your app uses to push a view to the Home tab
    client.views_publish(
      # the user that opened your app's app home
      user_id=event["user"],
      # the view object that appears in the app home
      view={
        "type": "home",
        "callback_id": "home_view",

        # body of the view
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Welcome to AuWRN's Home_* :tada:"
            }
          },
          {
            "type": "divider"
          },
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
            }
          },
          {
            "type": "actions",
            "elements": [
              {
                "type": "button",
                "text": {
                  "type": "plain_text",
                  "text": "Click me!"
                }
              }
            ]
          }
        ]
      }
    )

  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")

@app.event("message")
def handle_message(client, event, logger):
  channel_id = event['channel']
  msg_text, msg_type = event['text'], event['type']
  
  print("EVENT: ", event)
  channel_type = event['channel_type']
  if channel_type == 'im':
    if '튜토리얼' in msg_text:
      user_list = app.client.users_list()['members']
      user_options = [{"text":{
                          "type":"plain_text",
                          "text":user["real_name"], 
                          "emoji":True
                          },
                        "value":user["id"]
                      }
                 for user in user_list if user['is_bot']== False]
      channel_list = app.client.conversations_list()['channels']
      channel_options = [{"text":{"type":"plain_text", "text":channel["name"], "emoji":True}, "value":channel["id"]}
                         for channel in channel_list]
      dropdown_block = [
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": """:mag: 연구노트 생성을 위해 미리 설정을 해줘야 해요.
              먼저 연구노트 검토자와 연구노트를 검토받을 채널을 지정해주세요.
              연구노트 검토자는 보통 교수님이나 연구 책임자에요.
              오른은 사용자와 대화를 나눈뒤 생성한 연구노트를 특정 채널에 보내 검토자에게 확인을 받아요.
              이때 연구노트를 보낼 채널도 지정해주세요.
              """
          }
        },
        {
          "type": "divider"
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "*<연구노트 검토자>*\n연구노트를 검토하여 승인할 사람입니다."
          },
          "accessory": {
            "type": "static_select",
            "placeholder": {
              "type": "plain_text",
              "emoji": True,
              "text": "검토자"
            },
            "options": user_options
          }
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "*<연구노트를 올릴 채널>*\n연구노트를 검토를 위해 올릴 채널입니다."
          },
          "accessory": {
            "type": "static_select",
            "placeholder": {
              "type": "plain_text",
              "emoji": True,
              "text": "검토받을채널"
            },
            "options": channel_options
          }
        },
        {
          "type": "divider"
        },
        {
          "type": "actions",
          "elements": [
            {
              "type": "button",
              "text": {
                "type": "plain_text",
                "emoji": True,
                "text": "제출"
              },
              "value": "click_me_123",
              "action_id" : "button_click"
            }
          ]
        }
      ]
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
  print("interaction : ",payload)


# Start your app
if __name__ == "__main__":
    app.start(port=3000)