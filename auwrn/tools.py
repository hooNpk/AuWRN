import json
import requests
import io
from auwrn.view import get_tutorial_view, get_tutorial2_view
from datetime import datetime, timezone, timedelta
KST = timezone(timedelta(hours=9))

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

def which_stage(conn, team_id, user_id):
    today = datetime.now(KST).strftime('%Y-%m-%d')
    today_dialogue = conn.get_list(f"team-{team_id}/user-{user_id}/dialogue/{today}.json")
    if today_dialogue['KeyCount']==0:
        update_dialogue(
            conn,
            id={"team_id":team_id, "user_id":user_id},
            start=True
        )
        return 0
    else:
        cvstn = conn.get_object(f"team-{team_id}/user-{user_id}/dialogue/{today}.json")
        cvstn = json.loads(cvstn)
        return cvstn['stage']

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

def update_dialogue(conn, id:dict={}, talks=[], start=False, distract=False):
    today = datetime.now(KST).strftime('%Y-%m-%d')
    if start:
        cvstn = {"stage":0, "dialogue":[]}
        conn.upload_object(f"team-{id['team_id']}/user-{id['user_id']}/dialogue/{today}.json",data=json.dumps(cvstn, ensure_ascii=False))
    else:
        cvstn = conn.get_object(f"team-{id['team_id']}/user-{id['user_id']}/dialogue/{today}.json")
        cvstn = json.loads(cvstn)
        cvstn['dialogue'] = cvstn['dialogue']+talks
        if not distract:
            cvstn['stage'] = cvstn['stage']+1
        conn.upload_object(f"team-{id['team_id']}/user-{id['user_id']}/dialogue/{today}.json",data=json.dumps(cvstn, ensure_ascii=False))

def get_user_config(conn, id):
    cfg = conn.get_object(f"team-{id['team_id']}/user-{id['user_id']}/config.json")
    cfg = json.loads(cfg)
    return cfg

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