import os
import openai
from openai.error import APIConnectionError
import traceback
from datetime import datetime
import pytz
from prompts import prompt
from auwrn.utils import S3Connector
import json
from retry import retry
KST = pytz.timezone('Asia/Seoul')

class ChatGenerator():
    def __init__(self, organization, key) -> None:
        self.conn = S3Connector(os.environ.get('AWS_KEY'), os.environ.get('AWS_SECRET'))
        openai.organization = organization
        openai.api_key = key
        self.prompts = prompt

    @retry(APIConnectionError, tries=3, delay=1)
    def generate_text(self, input_prompt, type=None, tok_num=1000):
        req_prompt = self.prompts[type]+input_prompt
        try:
            completions = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages = req_prompt,
                max_tokens = tok_num,
                n=1,
                stop=None,
                temperature=0.5
            )
            res = completions.choices[0].message
            message = res.content
        except Exception as e:
            print("gpt 에러 발생")
            print(traceback.format_exc())
        return message

    def set_prompt(self, id, input_txt):
        today = datetime.now(KST).strftime('%Y-%m-%d')
        cvstn = self.conn.get_object(f"team-{id['team_id']}/user-{id['user_id']}/dialogue/{today}.json")
        dialogue = json.loads(cvstn)['dialogue']
        prompt = dialogue+[{"role":"user", "content":input_txt}]
        return prompt
