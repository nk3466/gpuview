import requests, json, os, pytz
from datetime import datetime
from core import load_reservations
def dooray_alarm_bot(send_message):
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "botName": "GPU BOT",
        "botIconImage": "https://cdn-icons-png.flaticon.com/512/4712/4712139.png",
        "text": send_message,
        "attachments":[
            {
                "title" : "GPU VIEW 바로가기",
                "titleLink" : "http://220.117.189.130:8800/",
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

utc_now = datetime.utcnow()
kst = pytz.timezone('Asia/Seoul')
today = datetime.now(kst).date()

user_names = []
    
for gpu in reservation_json.values():
    for info in gpu.values():
        end_date = datetime.strptime(info.get('endDate'), '%Y-%m-%d').date()
        if end_date <= today:
            user_names.append(info.get('userName'))

            
user_names = list(set(user_names))
if len(user_names) > 0:
    result = ','.join(user_names)
    result += ' 매니저님\n GPU 사용 연장을 원하실 경우 날짜를 수정해주세요!'
    dooray_alarm_bot(result)
    print(today, ','.join(user_names) + '서버 예약 만료 알림 완료')