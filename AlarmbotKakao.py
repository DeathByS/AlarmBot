from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5 import uic
import sys
import time, win32con, win32api, win32gui
import csv
from sync_Client import SyncClient
from enums import Regs, Machine, Alarms, OperatingTime, AbnormalSignAlarm, Coils, OnOffCheck
from queue import Queue
from PyQt5.QtCore import pyqtSlot


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("./kakaoalarm.ui", self)
        self.init()

    def init(self):
        # 의정부, 검단
        self.kakaoNameA = ''
        # 부산, 청난
        self.kakaoNameB = ''
        self.wechatName = ''
        self.connectList = []
        self.alarmList = []
        self.alarmCheck = {}
        self.plcConnect = SyncClient()
        self.plcConnect.connectClient("kwtkorea.iptime.org")
        self.triger = False
        self.pushButton_OnOff.clicked.connect(lambda state, button=self.pushButton_OnOff : self.onoffButtonClick(state, button))
        self.schedule = False

        # 부산, 청난을 제외한 나머지 사이트 
        self.msgQueueA = Queue()
        # 부산, 청난
        self.msgQueueB = Queue()

        self.timer = QTimer(self) 
        self.timer.setInterval(10000)
        # self.timer.start()
        self.timer.timeout.connect(self.GetAlarmData)

        self.initConnectionList()
        self.initAlarmList()
        self.initAlarmCheck()

    @pyqtSlot()
    def onoffButtonClick(self,state,button):
        self.triger = not self.triger
        
        if(self.triger):
            self.kakaoNameA = self.lineEdit_kakao_A.text()
            self.kakaoNameB = self.lineEdit_kakao_B.text()
            self.label_OnOff.setText("On")
            self.timer.start()

            # self.job = schedule.every(10).seconds.do(mainWindow.GetAlarmData)
            # schedule.run_all()
        else:
            self.label_OnOff.setText("Off")
            self.initAlarmCheck()
            self.timer.stop()
            # if(self.job is not False):
            #     schedule.cancel_job(self.job)


    # QMainWindow 에서 제공하는 이벤트 함수
    def changeEvent(self, event):
        print('window event call')

    
    def initConnectionList(self):
    
        with open('ConnectionList.csv', 'r', encoding='utf-8') as f:
            rdr = csv.reader(f)
            
            # connList = [] 
            
            for row in rdr:
                self.connectList.append(row)
                print(row[0])
                #  self.connectListBox.addItem(row[0])
                # self.connectListDict[row[0]] = row[1:]

            # self.connectListDict = dict(zip(connList[:1],connList[1:]))
            # print(self.connectListDict)

            # print(self.connectListDict['서울'])

    def initAlarmList(self):
        with open('AlarmList.csv', 'r', encoding='utf-8') as f:
            rdr = csv.reader(f)
        
            for row in rdr:
                self.alarmList.append(row)
                print(row)
            #  self.connectListBox.addItem(row[0])
            # self.alarmListDict[row[0]] = row[1]

    def initAlarmCheck(self):

        for i in self.connectList:
            # print(i[0])
            self.alarmCheck[i[0]] = [True] * (Alarms.DONTUSE4.value + 1)


    def GetAlarmData(self):
        
        data = {}

        machine = 0 
        
        for i in self.connectList:
            try:   
                print("onoffcheck")
                onoffCheck = self.plcConnect.readCoil(OnOffCheck.UJB_A.value + machine, 1)
                print(onoffCheck[0])
                print("Alarm" + i[0])
            except:
                print("Get Alarm OnOff Error")
                continue
            try:    
                if(onoffCheck[0] != True):

                    print("getAlarm")
                
                    alarmData = self.plcConnect.readCoil(Machine.TERMOFCOIL.value * machine + Alarms.PANELEMERGENCYSTOP.value, Alarms.DONTUSE4.value)
                    for AlarmNum in Alarms:

                        machineName = i[0]

                        if(alarmData[AlarmNum.value]):

                            if(self.alarmCheck[machineName][AlarmNum.value]):
                                # print(alarmData[k.value])
                                self.alarmCheck[machineName][AlarmNum.value] = False

                                data['machineName'] = machineName
                                data['alarm'] = str(self.alarmList[AlarmNum.value][1]) + ' ' + str(self.alarmList[AlarmNum.value][0])
                                dataText = machineName + " " + str(self.alarmList[AlarmNum.value][1]) + ' ' + str(self.alarmList[AlarmNum.value][0])
                                print(dataText)
                                
                                if machineName == '청난': 
                                    self.msgQueueB.put(dataText)
                                elif machineName == '부산_A':
                                    self.msgQueueB.put(dataText)
                                else:
                                    self.msgQueueA.put(dataText)



                            
                        else:
                            if(self.alarmCheck[machineName][AlarmNum.value] == False):
                            
                                self.alarmCheck[machineName][AlarmNum.value] = True
                                    
                
                         
            except:
                print("Alarm read error")
                continue
                 # self.alarmCheck.clear()
                 # self.alarmCheck = [True] * (Alarms.DONTUSE4.value + 1) 
                 # 
            machine += 1 

        if self.msgQueueA.qsize() != 0:
            print("kakako chatroom open A")
            print("kakao : " + self.kakaoNameA)
            self.open_chatroom(self.kakaoNameA)
            print("kakao send msg")
            self.kakao_sendtext(self.kakaoNameA, self.msgQueueA)
            print("over")  

        if self.msgQueueB.qsize() != 0:
            print("kakako chatroom open B")
            print("kakao : " + self.kakaoNameB)
            self.open_chatroom(self.kakaoNameB)
            print("kakao send msg")
            self.kakao_sendtext(self.kakaoNameB, self.msgQueueB)
            print("over")   
                                                              

# # 채팅방에 메시지 전송
    # # 엔터
    def SendReturn(self, hwnd):
        win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
        time.sleep(0.02)
        win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
        time.sleep(0.02)
        

    
    def kakao_sendtext(self, chatroom_name, msg = 0):
        # # 핸들 _ 채팅방
        hwndMain = win32gui.FindWindow( None, chatroom_name)
        hwndEdit = win32gui.FindWindowEx( hwndMain, None, "RICHEDIT50W", None)
        # hwndListControl = win32gui.FindWindowEx( hwndMain, None, "EVA_VH_ListControl_Dblclk", None)
        while msg.qsize():
            text = msg.get()
            print("alarm " + text)
            win32api.SendMessage(hwndEdit, win32con.WM_SETTEXT, 0, text)
            time.sleep(0.2)
            self.SendReturn(hwndEdit)
        
        # time.sleep(0.1)

        

    # # 채팅방 열기s
    def open_chatroom(self,chatroom_name):
        # # 채팅방 목록 검색하는 Edit (채팅방이 열려있지 않아도 전송 가능하기 위하여)
        hwndkakao = win32gui.FindWindow(None, "카카오톡")
        hwndkakao_edit1 = win32gui.FindWindowEx( hwndkakao, None, "EVA_ChildWindow", None)
        hwndkakao_edit2_1 = win32gui.FindWindowEx( hwndkakao_edit1, None, "EVA_Window", None)
        hwndkakao_edit2_2 = win32gui.FindWindowEx( hwndkakao_edit1, hwndkakao_edit2_1, "EVA_Window", None)
        hwndkakao_edit3 = win32gui.FindWindowEx( hwndkakao_edit2_2, None, "Edit", None)

        # # Edit에 검색 _ 입력되어있는 텍스트가 있어도 덮어쓰기됨
        win32api.SendMessage(hwndkakao_edit3, win32con.WM_SETTEXT, 0, chatroom_name)
        time.sleep(1.2)   # 안정성 위해 필요
        self.SendReturn(hwndkakao_edit3)
        time.sleep(1.2)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())