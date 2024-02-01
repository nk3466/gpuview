import requests, json, os, datetime
from core import load_reservations, save_reservations

ABS_PATH = os.path.dirname(os.path.realpath(__file__))
RESERVATION_DB = os.path.join(ABS_PATH, 'gpu_reservations.db')
remove_reservation_data = load_reservations()

today = datetime.date.today().strftime('%Y-%m-%d')

user_names = []

for server in remove_reservation_data:
        for idx in remove_reservation_data[server]:
            if remove_reservation_data[server][idx].get('endDate') == today:
                user_names.append(remove_reservation_data[server][idx].get('userName'))
                remove_reservation_data[server][idx] = {}
                
save_reservations(remove_reservation_data)

result = ','.join(user_names)
print(today, result + "서버 예약 삭제 완료")

