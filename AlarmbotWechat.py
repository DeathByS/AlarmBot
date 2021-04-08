from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5 import uic
import sys
import time
import csv
from sync_Client import SyncClient
from enums import Regs, Machine, Alarms, OperatingTime, AbnormalSignAlarm, Coils, OnOffCheck
import pyautogui as pg
import pyperclip
from PyQt5.QtCore import pyqtSlot


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("./wechatalarm.ui", self)
        self.init()

    def init(self):
        self.kakaoName = ''
        self.wechatName = ''
        self.connectList = []
        self.alarmList = []
        self.alarmCheck = {}
        self.plcConnect = SyncClient()
        self.plcConnect.connectClient("kwtkorea.iptime.org")
        self.triger = False
        self.pushButton_OnOff.clicked.connect(lambda state, button=self.pushButton_OnOff : self.onoffButtonClick(state, button))
        self.schedule = False
        self.buttonLocate = pg.locateOnScreen('num2.png', confidence=0.65)
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
            self.wechatName = self.lineEdit_wechat.text()
            self.label_OnOff.setText("On")
            self.timer.start()

           
        else:
            self.label_OnOff.setText("Off")
            self.initAlarmCheck()
            self.timer.stop()



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
            # try:    
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
                
                            if(self.lineEdit_wechat.text() != ''):
                                print("wechat send msg")
                                self.wechat_sendtext(self.wechatName, dataText)
                                # time.sleep(0.2)

                    else:
                        if(self.alarmCheck[machineName][AlarmNum.value] == False):
                        
                            self.alarmCheck[machineName][AlarmNum.value] = True
            # except:
                # print('error 발생')
                # pass
            machine += 1         
            # except:
                # print("Alarm read error")
                # continue
                 # self.alarmCheck.clear()
                 # self.alarmCheck = [True] * (Alarms.DONTUSE4.value + 1)                                            

    def wechat_sendtext(self,chatroom_name, text =''):
    # 위쳇이 실행되고 있는 상태에서 위챗 창 켜기
        print('type wechat')
        
        pg.press('win')
        pg.write('wechat')
        pg.press('enter')

        # 대화목록의 search 찾은 후 클릭 
        time.sleep(0.2)    
      
        # print('button locate 탐색 에러 - 다시 찾기 ')
        if(self.buttonLocate == None):
            self.buttonLocate = pg.locateOnScreen('num2.png', confidence=0.65)
    
        point = pg.center(self.buttonLocate)
        print(point)
  
        # button1locate = 
        print('step1 clear')
        # time.sleep(0.3)
        
        
        pg.moveTo(point)
        pg.click(clicks=2, interval=0.2)
        print('step2 clear')
        # search 에 원하는 사람의 이름 입력 후 대화창 켜기
        name = chatroom_name
        pyperclip.copy(name)
        pg.hotkey('ctrl', 'v')
        pg.press('enter')
        print('step3 clear')
        time.sleep(0.1)
        print("wechat text : " + text)
        pyperclip.copy(text)
        pg.hotkey('ctrl', 'v')
        pg.press('enter')
        print('step4 clear')
        time.sleep(0.1)
        pg.press('esc')
        
    # except:
    #     print('error wechat send msg')
    #     pass



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())