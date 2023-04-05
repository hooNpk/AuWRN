import os
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from config import *
from auwrn.utils import ChatGenerator

from slack_bolt import App

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
  

# Start your app
if __name__ == "__main__":
    app.start(port=3000)