import json
import requests
import io
from auwrn.view import get_tutorial_view, get_tutorial2_view

def is_new_team(conn, team_id):
    team_list = conn.get_list(f"team-{team_id}/")
    if team_list['KeyCount'] == 0:
        return True
    else:
        return False

def is_new_user(conn, team_id, user_id):
    user_list = conn.get_list(f"team-{team_id}/user-{user_id}")
    if user_list['KeyCount'] == 0:
        return True
    else:
        return False

def tutorial(app, channel_id, team_id, user_id):
    user_list = app.client.users_list()['members']
    channel_list = app.client.conversations_list()['channels']
    dropdown_block = get_tutorial_view(
        user_list, channel_list,
        {"team_id":team_id, "user_id":user_id, "channel_id":channel_id})
    response = app.client.chat_postMessage(
        channel=channel_id,
        text = "연구노트 작성을 설정해주세요",
        blocks = dropdown_block
    )

def tutorial2(app, channel_id):
    block = get_tutorial2_view()
    response = app.client.chat_postMessage(
        channel=channel_id,
        text = "연구노트 작성을 설정해주세요",
        blocks = block
    )

def update_user_config(id:dict, conn, kwargs):
    config = conn.get_object(f"team-{id['team_id']}/user-{id['user_id']}/config.json")
    config = json.loads(config)
    for key, item in kwargs.items():
        config[key] = item
    conn.upload_object(f"team-{id['team_id']}/user-{id['user_id']}/config.json", data=json.dumps(config, ensure_ascii=False))

def upload_image(files, conn):
    for file in files:
        file_id = file['id']
        filetype = file['filetype']
        file_name = file['title']
        user_id = file['user']
        team_id = file['user_team']
        file_dwld_url = file['url_private_download']
        response = requests.get(file_dwld_url)
        image_bytes = io.BytesIO(response.content)
        if 'research' in file_name or '연구' in file_name or '작성' in file_name:
            conn.upload_file_object(
                path=f"team-{team_id}/user-{user_id}/researcher.{filetype}",
                data=image_bytes
            )
        elif 'reviewer' in file_name or '검토' in file_name:
            conn.upload_file_object(
                path=f"team-{team_id}/user-{user_id}/reviewer.{filetype}",
                data=image_bytes
            )