def is_new_team(team_list):
    if team_list['KeyCount'] == 0:
        return True
    else:
        return False

def is_new_user(user_list):
    if user_list['KeyCount'] == 0:
        return True
    else:
        return False

def tutorial(app, client, channel_id, get_tutorial_view, team_id, user_id):
    user_list = app.client.users_list()['members']
    channel_list = app.client.conversations_list()['channels']
    dropdown_block = get_tutorial_view(user_list, channel_list, team_id, user_id)
    response = client.chat_postMessage(
        channel=channel_id,
        text = "연구노트 작성을 설정해주세요",
        blocks = dropdown_block
    )

def tutorial2(app, client, channel_id):
    print("AC")