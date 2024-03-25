import os, sys
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from loguru import logger
#os.add_dll_directory("C:\\Program Files\\GTK3-Runtime Win64\\bin")
MODULE_PATH = os.path.dirname(__file__)
sys.path.append(os.getcwd())#없애야 할 수도 있음.

from weasyprint import HTML
from auwrn.generate_content import ContentGenerator
import auwrn.tools as tool

KST = timezone(timedelta(hours=9))

class Contenter(ContentGenerator):
    def __init__(self, organization, key, s3_conn) -> None:
        super().__init__(organization, key)
        self.s3_conn = s3_conn

    def form_content(self, ids):
        soup = BeautifulSoup('''
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
        ''', 'html.parser')

        soup.find('td', id='created').string = f"@{datetime.now(KST).strftime('%Y-%m-%d, %H:%M')}"

        prompts = self.set_prompts(ids)
        content_keyword = self.generate_content(prompts['keyword'], type='keyword')
        logger.info(f"Content Keyword : {content_keyword}")

        cfg = tool.get_user_config(self.s3_conn, ids)

        soup.find('td', id='keyword').string = f"{content_keyword}"
        soup.find('td', id='writer').string = cfg['userRealName']
        soup.find('td', id='reviewer').string = cfg['reviewerRealName']

        conv = self.get_dialogues(ids)
        #TODO : 문어체로, 레포트 형식으로 어떻게 나오게 할 지 정하고 pdf로 옮겨야 함.
        summary_tag = soup.find('ul', id='summary-list')
        generated_summary = self.gen_chain_content(conv, type='summary', tok_num=400)
        generated_summary = self.trim_contents(generated_summary)
        logger.info(f"Generated summary : {generated_summary}")
        for elem in generated_summary:
            new_tag = soup.new_tag("li", style="list-style-type:disc")
            new_tag.string = "● "+elem
            summary_tag.append(new_tag)

        result_tag = soup.find('ul', id='learned-list')
        generated_result = self.gen_chain_content(conv, type='learned', tok_num=1000)
        generated_result = self.trim_contents(generated_result)
        logger.info(f"Generated Leanred : {generated_result}")
        for elem in generated_result:
            new_tag = soup.new_tag("li", style="list-style-type:disc")
            new_tag.string = "● "+elem
            result_tag.append(new_tag)
        
        return soup.prettify()

    def make_pdf(self, ids, content=None, css=None):
        today = datetime.now(KST).strftime('%Y-%m-%d')
        path=f"{MODULE_PATH}/notes/{ids['team_id']}-{ids['user_id']}-{today}.pdf"

        html = HTML(string=content)
        #css = CSS(string=css)
        html.write_pdf(
            path,
            #stylesheets=[css]
        )
        return path

    def trim_contents(self, content):
        content = content.replace('저는 ', '')
        content = content.replace('나는 ', '')
        return content.split('-')

if __name__=="__main__":
    from auwrn.utils import S3Connector
    from config import *
    from auwrn.log import ProductionLogConfig, DevelopmentLogConfig
    logger.remove()
    log_config = DevelopmentLogConfig()
    logger.configure(**log_config.LOGURU_SETTINGS)
    s3_conn = S3Connector(AWS_KEY, AWS_SECRET)
    
    contenter = Contenter(
        "org-IoS2U73DFBWnD9tF97CPmN3i",

        s3_conn=s3_conn
    )
    contents = contenter.form_content({'team_id':'T050MCWGT96','user_id':'U04V54ECS7Q'})
    contenter.make_pdf({'team_id':'T050MCWGT96','user_id':'U04V54ECS7Q'}, content=contents)