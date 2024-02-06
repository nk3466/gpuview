import requests, json, os, datetime
from core import load_reservations
def dooray_alarm_bot(send_message):
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "botName": "GPU MONITER BOT",
        "botIconImage": "https://cdn-icons-png.flaticon.com/512/4854/4854226.png",
        "text": send_message,
        "attachments":[
            {
                "title" : "GPU Moniter 바로가기",
                "titleLink" : "http://3.35.87.172:50005",
                "color" : "blue"
            }
        ]
    }

    # POST 요청을 보냅니다.
    url = "https://hook.dooray.com/services/3153689713330030041/3713722902797160820/AAR734NgSdGWtdg7xJffag"
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # 응답 확인
    if response.status_code == 200:
        print("요청이 성공적으로 전송되었습니다.")
    else:
        print(f"요청 실패. 상태 코드: {response.status_code}")
        


ABS_PATH = os.path.dirname(os.path.realpath(__file__))
RESERVATION_DB = os.path.join(ABS_PATH, 'gpu_reservations.db')
reservation_json = load_reservations()

today = datetime.date.today().strftime('%Y-%m-%d')

# endDate가 오늘 날짜와 같은 userName 찾기
user_names = []
week_names = []

weekday = today.weekday()  # 월요일은 0, 일요일은 6

# 지난 주말 날짜 계산 (오늘이 월요일인 경우에만)
if weekday == 0:
    last_sunday = today - datetime.timedelta(days=1)  # 어제 (일요일)
    last_saturday = today - datetime.timedelta(days=2)  # 그제 (토요일)
    weekend_dates = {last_sunday.strftime('%Y-%m-%d'), last_saturday.strftime('%Y-%m-%d')}
else:
    weekend_dates = set()
    
    
for gpu in reservation_json.values():
    for info in gpu.values():
        if info and info.get('endDate') == today:
            user_names.append(info.get('userName'))
            
user_names = list(set(user_names))
if len(user_names) > 0:
    result = ','.join(user_names)
    result += ' 매니저님 오늘까지 GPU 사용 예약하셨습니다. \n GPU 사용 연장을 원하실 경우 수정해주세요!'
    dooray_alarm_bot(result)
    print(today, ','.join(user_names) + '서버 예약 만료 알림 완료')