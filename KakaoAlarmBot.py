import time, win32con, win32api, win32gui
import csv
from sync_Client import SyncClient
from enums import Regs, Machine, Alarms, OperatingTime, AbnormalSignAlarm, Coils, OnOffCheck
import schedule
import pyautogui as pg
import pyperclip

# # 카톡창 이름, (활성화 상태의 열려있는 창)
kakao_opentalk_name = 'KWT이신형'
wechat_name = '이신형'

connectList = []
alarmList = []
alarmCheck = {}
plcConnect = SyncClient()


def initConnectionList():
    
        with open('ConnectionList.csv', 'r', encoding='utf-8') as f:
            rdr = csv.reader(f)
            
            # connList = [] 
            
            for row in rdr:
                connectList.append(row)
                print(row[0])
                #  self.connectListBox.addItem(row[0])
                # self.connectListDict[row[0]] = row[1:]

            # self.connectListDict = dict(zip(connList[:1],connList[1:]))
            # print(self.connectListDict)

            # print(self.connectListDict['서울'])

def initAlarmList():
    with open('AlarmList.csv', 'r', encoding='utf-8') as f:
        rdr = csv.reader(f)
        
        for row in rdr:
            alarmList.append(row)
            print(row)
            #  self.connectListBox.addItem(row[0])
            # self.alarmListDict[row[0]] = row[1]

def initAlarmCheck():

        for i in connectList:
            # print(i[0])
            alarmCheck[i[0]] = [True] * (Alarms.DONTUSE4.value + 1)
               

def GetAlarmData():

        
        data = {}

        machine = 0 
        
        for i in connectList:
            try:   
                print("onoffcheck")
                onoffCheck = plcConnect.readCoil(OnOffCheck.UJB_A.value + machine, 1)
                print(onoffCheck[0])
                print("Alarm" + i[0])
            except:
                print("Get Alarm OnOff Error")
                continue
            try:    
                if(onoffCheck[0] != True):

                    print("getAlarm")
                
                    alarmData = plcConnect.readCoil(Machine.TERMOFCOIL.value * machine + Alarms.PANELEMERGENCYSTOP.value, 
                                                             Alarms.DONTUSE4.value)
                    for AlarmNum in Alarms:

                        machineName = i[0]

                        if(alarmData[AlarmNum.value]):

                             if(alarmCheck[machineName][AlarmNum.value]):
                                 # print(alarmData[k.value])
                                alarmCheck[machineName][AlarmNum.value] = False

                                data['machineName'] = machineName
                                data['alarm'] = str(alarmList[AlarmNum.value][1]) + ' ' + str(alarmList[AlarmNum.value][0])
                                dataText = machineName + " " + str(alarmList[AlarmNum.value][1]) + ' ' + str(alarmList[AlarmNum.value][0])
                                print(dataText)

                                print("kakako chatroom open")
                                open_chatroom(kakao_opentalk_name)

                                print("kakao send msg")
                                kakao_sendtext(kakao_opentalk_name, dataText)

                                time.sleep(0.5)
                                print("wechat send msg")
                                wechat_sendtext(wechat_name, dataText)

                        else:
                            if(alarmCheck[machineName][AlarmNum.value] == False):
                            
                                alarmCheck[machineName][AlarmNum.value] = True       
            except:
                print("Alarm read error")
                continue

            machine += 1  
                 # self.alarmCheck.clear()
                 # self.alarmCheck = [True] * (Alarms.DONTUSE4.value + 1)                                            

                
                           

                   
            


# # 채팅방에 메시지 전송
def kakao_sendtext(chatroom_name, text):
    # # 핸들 _ 채팅방
    hwndMain = win32gui.FindWindow( None, chatroom_name)
    hwndEdit = win32gui.FindWindowEx( hwndMain, None, "RICHEDIT50W", None)
    # hwndListControl = win32gui.FindWindowEx( hwndMain, None, "EVA_VH_ListControl_Dblclk", None)

    win32api.SendMessage(hwndEdit, win32con.WM_SETTEXT, 0, text)
    SendReturn(hwndEdit)


# # 엔터
def SendReturn(hwnd):
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    time.sleep(0.1)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)


# # 채팅방 열기
def open_chatroom(chatroom_name):
    # # 채팅방 목록 검색하는 Edit (채팅방이 열려있지 않아도 전송 가능하기 위하여)
    hwndkakao = win32gui.FindWindow(None, "카카오톡")
    hwndkakao_edit1 = win32gui.FindWindowEx( hwndkakao, None, "EVA_ChildWindow", None)
    hwndkakao_edit2_1 = win32gui.FindWindowEx( hwndkakao_edit1, None, "EVA_Window", None)
    hwndkakao_edit2_2 = win32gui.FindWindowEx( hwndkakao_edit1, hwndkakao_edit2_1, "EVA_Window", None)
    hwndkakao_edit3 = win32gui.FindWindowEx( hwndkakao_edit2_2, None, "Edit", None)

    # # Edit에 검색 _ 입력되어있는 텍스트가 있어도 덮어쓰기됨
    win32api.SendMessage(hwndkakao_edit3, win32con.WM_SETTEXT, 0, chatroom_name)
    time.sleep(1.5)   # 안정성 위해 필요
    SendReturn(hwndkakao_edit3)
    time.sleep(1.5)

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


    pyperclip.copy(text)
    pg.hotkey('ctrl', 'v')
    pg.press('enter')

    time.sleep(0.3)

    pg.press('esc')



def main():
    # open_chatroom(kakao_opentalk_name)  # 채팅방 열기

    # text = "test"
    # kakao_sendtext(kakao_opentalk_name, text)    # 메시지 전송

    plcConnect.connectClient("kwtkorea.iptime.org")
    initConnectionList()
    initAlarmList()
    initAlarmCheck() 

    GetAlarmData()


if __name__ == '__main__':
    main()

    schedule.every(10).seconds.do(GetAlarmData)
    schedule.run_all(delay_seconds=1)

    while(1):
        schedule.run_pending()
        time.sleep(1)