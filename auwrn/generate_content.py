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
from langchain.chat_models import ChatOpenAI
from loguru import logger
KST = pytz.timezone('Asia/Seoul')

class ContentGenerator():
    def __init__(self, organization, key) -> None:
        self.conn = S3Connector(os.environ.get('AWS_KEY'), os.environ.get('AWS_SECRET'))
        self.key = key
        openai.organization = organization
        openai.api_key = key
        self.prompts = prompt

    @retry(APIConnectionError, tries=3, delay=1)
    def generate_content(self, input_prompt, type=None, tok_num=400):
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

    def gen_chain_content(self, conversation, type='learned', tok_num=400):
        input_prompt = self.prompts[type]
        chat = ChatOpenAI(
            max_retries=3,
            max_tokens=tok_num,
            model_name = 'gpt-3.5-turbo-0613',
            openai_api_key=self.key,
            request_timeout=10,
            streaming=True,
            temperature=0.3
        )
        response = chat(input_prompt.format_messages(
            conversation = conversation
        )).content
        return response

    def set_prompt(self, id, input_txt):
        today = datetime.now(KST).strftime('%Y-%m-%d')
        cvstn = self.conn.get_object(f"team-{id['team_id']}/user-{id['user_id']}/dialogue/{today}.json")
        dialogue = json.loads(cvstn)['dialogue']
        prompt = dialogue+[{"role":"user", "content":input_txt}]
        return prompt
    
    def get_dialogues(self, id):
        today = datetime.now(KST).strftime('%Y-%m-%d')
        cvstn = self.conn.get_object(f"team-{id['team_id']}/user-{id['user_id']}/dialogue/{today}.json")
        dialogue = json.loads(cvstn)['dialogue']
        dialogues = [dial for dial in dialogue if dial['role']=='user']
        logger.info(f"Dialogue : {dialogues}")
        return dialogues

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