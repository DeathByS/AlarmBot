# AlarmBot
카카오톡,위챗을 통해 현장 기기의 알람을 전송하는 봇

![image](https://user-images.githubusercontent.com/46432795/115644006-c4415e80-a358-11eb-8ee9-d63d6a50bf76.png)

## 내용

 * 카카오톡 채팅방 이름을 입력 후 On/OFF 버튼 클릭
 * 10초마다 한번씩 메인 plc와 통신하여 알람 내역 수신
 * 수신된 메시지를 Queue에 저장 후, 채팅방에 전송
