import openai
import traceback
from datetime import datetime
import pytz
from config import *
from prompts import prompt
from auwrn.utils import S3Connector
import json
KST = pytz.timezone('Asia/Seoul')

class ContentGenerator():
    def __init__(self, organization, key) -> None:
        self.conn = S3Connector(AWS_KEY, AWS_SECRET)
        openai.organization = organization
        openai.api_key = key
        self.prompts = prompt

    def generate_content(self, input_prompt, type=None, tok_num=250):
        req_prompt = self.prompts[type]+input_prompt
        try:
            completions = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
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
    
    def set_prompts(self, id):
        today = datetime.now(KST).strftime('%Y-%m-%d')
        cvstn = self.conn.get_object(f"team-{id['team_id']}/user-{id['user_id']}/dialogue/{today}.json")
        dialogue = json.loads(cvstn)['dialogue']
        prompts = {
            "keyword": dialogue+[{"role":"user", "content":"키워드 :"}],
            "summary":dialogue+[{"role":"user", "content":"요약 :"}],
            "learned":dialogue+[{"role":"user", "content":"배운점 :"}],
            "tomorrow":dialogue+[{"role":"user", "content":"내일 계획 :"}]
        }
        print(f"Dialogue : {dialogue}")
        return prompts