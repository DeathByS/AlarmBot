import pyautogui as pg
import pyperclip
import time

def wechat_sendtext(chatroom_name, text =''):
# 위쳇이 실행되고 있는 상태에서 위챗 창 켜기
    pg.press('win')
    pg.write('wechat')
    pg.press('enter')

    # 대화목록의 search 찾은 후 클릭 
    time.sleep(0.2)
    button1locate = pg.locateOnScreen('num2.png', confidence=0.7)
    point = pg.center(button1locate)
    print(point)

    pg.moveTo(point)
    pg.click(clicks= 2, interval=0.5)

    # search 에 원하는 사람의 이름 입력 후 대화창 켜기
    name = chatroom_name
    pyperclip.copy(name)
    pg.hotkey('ctrl', 'v')
    pg.press('enter')


    pyperclip.copy()
    pg.hotkey('ctrl', 'v')
    pg.press('enter')




wechat_sendtext('이신형')