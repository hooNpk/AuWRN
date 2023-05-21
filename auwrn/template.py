import random

templates = {
    0: [
        "오셨군요! 연구노트를 꾸준히 쓰기만 해도 연구 성과가 크게 높아진답니다. 오늘은 어떤 작업들을 하셨을까요?",
    ],
    1: [
        "",
        "",
        ""
    ],
    2: [],
    3: [],
    4: [
        "오늘은 벌써 연구노트를 작성해주셨습니다! 오른을 자주 찾아와주시는 건 기쁘지만 내일 추가적인 연구를 진행하신 뒤 알려주세요!"
    ],
}

def stage_template(stage:int):
    template = templates[stage]
    rd_num = random.randint(0, len(template)-1)
    return template[rd_num]

