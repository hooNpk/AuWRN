import os
from flask import Flask, request, make_response, Response
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App, BoltContext
from slack_bolt.adapter.flask import SlackRequestHandler

SLACK_BOT_TOKEN = "xoxb-5021438571312-5060156183073-0cf1vziuYMY5PocGN91ZOwHk"
SLACK_SIGNING_SECRET = "e14e7afc7a2cc698c6241d216d1b6264"

import os
from slack_bolt import App

# Initializes your app with your bot token and signing secret
app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

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
  text = "안녕하세요 테스트입니다."
  print("EVENT: ", event)
  channel_type = event['channel_type']
  if channel_type == 'im':
    try:
      result = client.chat_postMessage(
        channel=channel_id,
        text=text
      )
      print(result)
    except SlackApiError as e:
      print(f"Error: {e}")
  
   

# Start your app
if __name__ == "__main__":
    app.start(port=3000)