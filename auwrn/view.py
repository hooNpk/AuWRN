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

def get_tutorial_view(user_list, channel_list, ids:dict):
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
                "text": "안녕하세요 처음 오셨네요! 반가워요 저는 오른이에요. :microscope: \n 오른은 연구노트를 작성하며 창의적이고 발전적인 연구를 도와드리고 있어요.\n 오른과 함께 연구 성과 내실 준비 되셨죠? :smile: \n\n오른과 대화를 하면 연구노트가 만들어져요.\n이 연구노트가 법적으로도 인정을 받으려면 필요한 정보들이 있어요. \n아래 빈칸들을 채워서 알려주세요. :smiling_face_with_3_hearts:"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "block_id": f"tutorial-reviewer:{ids['team_id']}-{ids['user_id']}",
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
            "block_id": f"tutorial-review-channel:{ids['team_id']}-{ids['user_id']}",
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
            "block_id": f"tutorial-org:{ids['team_id']}-{ids['user_id']}",
			"element": {
				"type": "plain_text_input",
				"multiline": True,
				"action_id": "button_click"
			},
			"label": {
				"type": "plain_text",
				"text": "연구 기관",
				"emoji": True
			},
            "hint" : {
				"type": "plain_text",
				"text": "소속된 기관을 알려주세요. 예시)성균관대학교 소프트웨어공학 연구실",
				"emoji": True
			},
            "dispatch_action" : True
		},
        {
			"type": "input",
            "block_id": f"tutorial-project:{ids['team_id']}-{ids['user_id']}",
			"element": {
				"type": "plain_text_input",
				"multiline": True,
				"action_id": "button_click"
			},
			"label": {
				"type": "plain_text",
				"text": "연구 과제 제목",
				"emoji": True
			},
            "hint": {
				"type": "plain_text",
				"text": "연구노트를 작성할 연구 과제 제목을 알려주세요. 예시) 이기종 비정형 데이터 대용량 처리 시스템",
				"emoji": True
			},
            "dispatch_action" : True
		},
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "block_id": f"tutorial-submit-button-clicked:{ids['team_id']}-{ids['user_id']}-{ids['channel_id']}",
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

def get_tutorial2_view():
    tutorial_views = [
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "거의 끝났습니다! :partying_face: \n\n 오른과 대화하시면 연구노트가 생성되어 지정된 채널에 보내져요.\n 검토자가 해당 파일을 검토하여 :white_check_mark: 이모지를 남기면 정식 연구노트로 인정돼요. \n\n 정식 연구노트로 인정받으려면 연구자와 검토자의 서명이 필요해요. \n 마지막으로 연구자와 검토자의 서명으로 쓰일 png 파일을 올려주시면 끝이에요. :muscle: \n 배경이 투명인 서명 png 파일을 보내주세요. \n 연구자의 png파일을 researcher.png 이름으로 먼저 보내주시고, 검토자의 서명 png파일을 reviewer.png 이름으로 보내주세요."
            }
        },
        {
            "type": "divider"
        },
    ]
    return tutorial_views