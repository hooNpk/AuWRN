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

def get_tutorial_view(user_list, ids:dict):
    user_options = [
        {"text":{"type":"plain_text","text":user["real_name"], "emoji":True}, "value":user["id"]}
        for user in user_list if user['is_bot']== False]
    
    # channel_options = [{"text":{"type":"plain_text","text":channel["name"], "emoji":True}, 
    #                     "value":channel["id"]}
    #                     for channel in channel_list]
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
        # {
		# 	"type": "input",
        #     "block_id": f"research-keywords:{ids['team_id']}-{ids['user_id']}",
		# 	"element": {
		# 		"type": "plain_text_input",
		# 		"multiline": True,
		# 		"action_id": "button_click"
		# 	},
		# 	"label": {
		# 		"type": "plain_text",
		# 		"text": "연구 분야 : 자세히 작성하면 오른과 좀 더 유용한 대화를 나눌 수 있어요.",
		# 		"emoji": True
		# 	},
        #     "hint": {
		# 		"type": "plain_text",
		# 		"text": "연구노트를 작성할 연구 과제 제목을 알려주세요. 예시) 이기종 비정형 데이터 대용량 처리 시스템",
		# 		"emoji": True
		# 	},
        #     "dispatch_action" : True
		# },
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
                "text": "설정이 끝났습니다! :partying_face: \n\n 연구를 하시면서 떠오르는 아이디어, 읽은 논문, 실험 결과 등을 \n 오른에게 메모하듯 남겨주시면 오후 5시에 연구노트를 만들어서 보내드려요.\n 편하게 메모해주시면 오른이 관련 전문 지식을 찾아보고 피드백도 드려요. \n오른과 함께 생산적인 연구를 해보세요!:partying_face::partying_face:"
            }
        },
        {
            "type": "divider"
        },
    ]
    return tutorial_views