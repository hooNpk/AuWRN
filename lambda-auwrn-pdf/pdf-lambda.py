#!/usr/bin/env python
import subprocess
import base64
import os
import json

import urllib.request
from functools import partial
import tempfile
from weasyprint import CSS, HTML
import pathlib
from urllib.parse import urlparse
import concurrent.futures
import boto3
import uuid

from slack_api import post_to_slack

s3 = boto3.client("s3")
pdf_blueprint = '''
    <body>
    <header>
    <div class="page-header-icon"><span class="icon">✏️</span></div>
    <h1 class="page-title" id="page-title">BERT 탑재, Tech Lead란.</h1>
    <table class="properties"><tbody>
    <tr class="property-row property-row-created_time">
        <th>생성일</th>
        <td id="created"><time>2023-05-23, 16:25</time></td>
    </tr>
    <tr class="property-row property-row-multi_select">
        <th>키워드</th>
        <td id="keyword"><span class="selected-value select-value-color-blue">공부</span></td>
    </tr>
    <tr class="property-row property-row-person">
        <th>작성자</th>
        <td id="writer"><span class="user">Sayu Park</span></td>
    </tr>
    <tr class="property-row property-row-person">
        <th>검토자</th>
        <td id="reviewer"><span class="user">Sayu Park</span></td>
    </tr>
    </tbody></table>
    </header>
    <div class="page-body">
    <h3 id="summary" class="">요약</h3>
    <ul id="summary-list" class="bulleted-list">
    </ul>
    <h3 id="learned" class="">결과</h3>
    <ul id="learned-list" class="bulleted-list">
    </ul>
    </div>
    </body>
'''


def gen_pdf_name(tmpdir):
    return tmpdir / f"{uuid.uuid4()}.pdf"

def download(tmpdir, url):
    name = gen_pdf_name(tmpdir)
    urllib.request.urlretrieve(url, name)
    return name

def fetch_attachments(downloader, pdfs):
    if not pdfs:
        return []

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(len(pdfs), 6)
    ) as executor:
        return list(executor.map(downloader, pdfs))


def postprocess(tmpdir, document, attachments):
    pdfs = fetch_attachments(partial(download, tmpdir), attachments)
    tmpfile = gen_pdf_name(tmpdir)
    subprocess.check_call(
        [
            "gs",
            "-q",
            "-sDEVICE=pdfwrite",
            "-dPDFSETTINGS=/prepress",
            "-dFIXEDMEDIA",
            "-sPAPERSIZE=a4",
            "-dPDFFitPage",
            "-dAutoRotatePages=/PageByPage",
            "-o",
            f"{tmpfile}",
            document,
            *pdfs,
        ]
    )
    return tmpfile

def lambda_handler(event, context):
    filename = event["filename"]
    bot_access_token = event['token']
    ch_id = event['channel']
    parsed_file = filename.split('/')
    user_id = parsed_file[2].split('-')[1]
    file_name = '/'.join(parsed_file[3:])

    attachments = [
        a
        for a in event.get("attachments", [])
        if urlparse(a).path.lower().endswith(".pdf")
    ]
    always_postprocess = event.get("always_postprocess", False)
    return_base64 = event.get("return") == "base64"
    basename = os.path.basename(filename)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)
        document = gen_pdf_name(tmpdir)
        
        HTML(string=pdf_blueprint).write_pdf(
            target=document,
            stylesheets=[CSS(string=event["css"])] if "css" in event else None,
        )

        if attachments or always_postprocess:
            document = postprocess(tmpdir, document, attachments)
        if return_base64:
            with open(document, "rb") as f:
                data = f.read()
            return {
                "statusCode": 200,
                "headers": {
                    "Content-type": "application/pdf",
                    "Content-Disposition": f"attachment;filename={basename}",
                },
                "isBase64Encoded": True,
                "body": base64.b64encode(data).decode("utf-8"),
            }
        else:
            bucket = os.environ["BUCKET"]
            with open(document, "rb") as f:
                s3.upload_fileobj(
                    f,
                    bucket,
                    filename,
                    ExtraArgs={"ContentType": "application/pdf"},
                )
            url = s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": bucket, "Key": filename},
                ExpiresIn=3600,
            )
            #url을 가지고 다운로드 받을 수 있도록 변경
            
            note_block = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"안녕하세요 <@{user_id}>님! 오늘도 최선을 다해주셔서 고맙습니다. 저에게 남겨주신 대화를 기반으로 연구노트를 정리하여 보내드려요! :nerd_face:"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{file_name}"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Click Me",
                            "emoji": True
                        },
                        "value": "click_me_123",
                        "url": url,
                        "action_id": "button-action"
                    }
                }
            ]

            post_to_slack(
                bot_access_token,
                json.dumps({
                    'channel' : ch_id,
                    'text' : '연구노트 다운로드',
                    'blocks' : note_block
                }).encode('utf-8')
            )

            return {"statusCode": 200, "body": "Hello from Lambda!"}


# import json
# import os, sys
# from datetime import datetime, timezone, timedelta
# from bs4 import BeautifulSoup

# from weasyprint import HTML
# KST = timezone(timedelta(hours=9))

# def form_content(ids):
#     soup = BeautifulSoup('''
#         <body>
#         <header>
#         <div class="page-header-icon"><span class="icon">✏️</span></div>
#         <h1 class="page-title" id="page-title">BERT 탑재, Tech Lead란.</h1>
#         <table class="properties"><tbody>
#         <tr class="property-row property-row-created_time">
#             <th>생성일</th>
#             <td id="created"><time>2023-05-23, 16:25</time></td>
#         </tr>
#         <tr class="property-row property-row-multi_select">
#             <th>키워드</th>
#             <td id="keyword"><span class="selected-value select-value-color-blue">공부</span></td>
#         </tr>
#         <tr class="property-row property-row-person">
#             <th>작성자</th>
#             <td id="writer"><span class="user">Sayu Park</span></td>
#         </tr>
#         <tr class="property-row property-row-person">
#             <th>검토자</th>
#             <td id="reviewer"><span class="user">Sayu Park</span></td>
#         </tr>
#         </tbody></table>
#         </header>
#         <div class="page-body">
#         <h3 id="summary" class="">요약</h3>
#         <ul id="summary-list" class="bulleted-list">
#         </ul>
#         <h3 id="learned" class="">결과</h3>
#         <ul id="learned-list" class="bulleted-list">
#         </ul>
#         </div>
#         </body>
#     ''', 'html.parser')

#     soup.find('td', id='created').string = f"@{datetime.now(KST).strftime('%Y-%m-%d, %H:%M')}"

#     # prompts = self.set_prompts(ids)
#     # content_keyword = self.generate_content(prompts['keyword'], type='keyword')
#     # logger.info(f"Content Keyword : {content_keyword}")

#     # cfg = tool.get_user_config(self.s3_conn, ids)

#     # soup.find('td', id='keyword').string = f"{content_keyword}"
#     # soup.find('td', id='writer').string = cfg['userRealName']
#     # soup.find('td', id='reviewer').string = cfg['reviewerRealName']

#     # conv = self.get_dialogues(ids)
#     # #TODO : 문어체로, 레포트 형식으로 어떻게 나오게 할 지 정하고 pdf로 옮겨야 함.
#     # summary_tag = soup.find('ul', id='summary-list')
#     # generated_summary = self.gen_chain_content(conv, type='summary', tok_num=400)
#     # generated_summary = self.trim_contents(generated_summary)
#     # logger.info(f"Generated summary : {generated_summary}")
#     # for elem in generated_summary:
#     #     new_tag = soup.new_tag("li", style="list-style-type:disc")
#     #     new_tag.string = "● "+elem
#     #     summary_tag.append(new_tag)

#     # result_tag = soup.find('ul', id='learned-list')
#     # generated_result = self.gen_chain_content(conv, type='learned', tok_num=1000)
#     # generated_result = self.trim_contents(generated_result)
#     # logger.info(f"Generated Leanred : {generated_result}")
#     # for elem in generated_result:
#     #     new_tag = soup.new_tag("li", style="list-style-type:disc")
#     #     new_tag.string = "● "+elem
#     #     result_tag.append(new_tag)
    
#     return soup.prettify()

# def make_pdf(ids, content=None, css=None):
#     today = datetime.now(KST).strftime('%Y-%m-%d')
#     path=f"/tmp/{ids['team_id']}-{ids['user_id']}-{today}.pdf"

#     html = HTML(string=content)
#     #css = CSS(string=css)
#     html.write_pdf(
#         path,
#         #stylesheets=[css]
#     )
#     return path

# def trim_contents(self, content):
#         content = content.replace('저는 ', '')
#         content = content.replace('나는 ', '')
#         return content.split('-')

# def lambda_handler(event, context):
#     # TODO implement
#     contents = form_content({'team_id':'T050MCWGT96','user_id':'U04V54ECS7Q'})
#     pdf_path = make_pdf({'team_id':'T050MCWGT96','user_id':'U04V54ECS7Q'}, content=contents)
#     print(f"PDF PATH : {pdf_path}")
#     return {
#         'statusCode': 200,
#         'body': json.dumps(f"Hello from Lambda! {pdf_path}")
#     }
