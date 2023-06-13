import os
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
os.add_dll_directory("C:\\Program Files\\GTK3-Runtime Win64\\bin")
MODULE_PATH = os.path.dirname(__file__)
from weasyprint import HTML
from auwrn.generate_content import ContentGenerator

KST = timezone(timedelta(hours=9))

class Contenter(ContentGenerator):
    def __init__(self, organization, key) -> None:
        super().__init__(organization, key)

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
            <h3 id="tomorrow" class="">내일 할 일</h3>
            <ul id="tomorrow-list" class="bulleted-list">
            </ul>
            </div>
            </body>
        ''', 'html.parser')

        print(datetime.now(KST).strftime('%Y-%m-%d, %H:%M'))
        soup.find('td', id='created').string = f"@{datetime.now(KST).strftime('%Y-%m-%d, %H:%M')}"

        keyword_prompt = self.set_prompt(ids, "키워드")
        content_keyword = self.generate_content(keyword_prompt, type='keyword')
        print(content_keyword)
        soup.find('td', id='keyword').string = f"{content_keyword}"
        soup.find('td', id='writer').string = ""
        soup.find('td', id='reviewer').string = ""

        summary = soup.find('ul', id='summary-list')
        new_tag = soup.new_tag("li", style="list-style-type:disc")
        new_tag.string = "테스트용 태그"
        summary.append(new_tag)
        soup.find('ul', id='learned-list')
        soup.find('ul', id='tomorrow-list')
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

if __name__=="__main__":
    contenter = Contenter(
        "org-IoS2U73DFBWnD9tF97CPmN3i",
        "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"
    )
    contents = contenter.form_content({'team_id':'T050MCWGT96','user_id':'U04V54ECS7Q'})
    contenter.make_pdf({'team_id':'T050MCWGT96','user_id':'U04V54ECS7Q'}, content=contents)