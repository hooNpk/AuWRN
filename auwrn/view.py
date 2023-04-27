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

def get_tutorial_view(user_list, channel_list, team_id, user_id):
    user_options = [{"text":{"type":"plain_text","text":user["real_name"], "emoji":True}, 
                    "value":user["id"]}
                    for user in user_list if user['is_bot']== False]
    channel_options = [{"text":{"type":"plain_text","text":channel["name"], "emoji":True}, 
                        "value":channel["id"]}
                        for channel in channel_list]
    tutorial_views = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":mag: 안녕하세요 처음 오셨네요! 반가워요 저는 오른이에요.\n연구노트 생성을 위해 미리 설정을 해줘야 해요.\n먼저 연구노트 검토자와 연구노트를 검토받을 채널을 지정해주세요.\n연구노트 검토자는 보통 교수님이나 연구 책임자에요.\n오른은 연구노트를 생성하여 특정 채널에 보내 검토자에게 확인을 받아요.\n이때 연구노트를 보낼 채널도 지정해주세요."
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "block_id": f"tutorial-reviewer:{team_id}-{user_id}",
            "text": {
                "type": "mrkdwn",
                "text": "*<연구노트 검토자>*\n연구노트를 검토하여 승인할 사람입니다."
            },
            "accessory": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "검토자",
                    "emoji": True,
                },
                "options": user_options,
                "action_id" : "button_click",
            }
        },
        {
            "type": "section",
            "block_id": f"tutorial-review-channel:{team_id}-{user_id}",
            "text": {
                "type": "mrkdwn",
                "text": "*<연구노트를 올릴 채널>*\n연구노트를 검토를 위해 올릴 채널입니다."
            },
            "accessory": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "검토받을채널",
                    "emoji": True,
                },
                "options": channel_options,
                "action_id" : "button_click",
            }
        },
        {
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"multiline": True,
				"action_id": "button_click"
			},
			"label": {
				"type": "plain_text",
				"text": "소속된 기관을 알려주세요. 예시)성균관대학교 소프트웨어공학 연구실",
				"emoji": True
			}
		},
        {
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"multiline": True,
				"action_id": "button_click"
			},
			"label": {
				"type": "plain_text",
				"text": "연구노트를 작성할 연구 과제 제목을 알려주세요. 예시) 이기종 비정형 데이터 대용량 처리 시스템",
				"emoji": True
			}
		},
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "block_id": f"tutorial-submit-button-clicked:{team_id}-{user_id}",
            "elements": [
                {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "제출"
                },
                "value": "submit",
                "action_id" : "button_click",
                }
            ]
        }
    ]
    return tutorial_views