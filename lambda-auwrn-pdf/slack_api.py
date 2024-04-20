from urllib import request, parse

URL = {
    "msg" : "https://slack.com/api/chat.postMessage",
    "view" : "https://slack.com/api/views.publish",
    "user_list" : "https://slack.com/api/users.list",
    "channel_list" : "app.client.conversations_list",
}


def post_to_slack(bot_token, data, req_type="msg"):
    url = URL[req_type]
    headers = {
        'Authorization': f"Bearer {bot_token}",
        'Content-Type': 'application/json'
    }
    req = request.Request(
        url,
        data=data,
        headers=headers
    )
    response = request.urlopen(req)
    response_data = response.read().decode('utf-8')
    return response_data