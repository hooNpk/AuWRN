home_view = {
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

def get_tutorial_view(user_options, channel_options):
    tutorial_views = {
    "review" : [
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
                "options": user_options,
                "action_id" : "button_click"
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
                "options": channel_options,
                "action_id" : "button_click"
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
    }
    return tutorial_views