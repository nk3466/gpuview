from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from datetime import datetime

# 변수, 함수 정의
now = datetime.now()
today_date = now.strftime("%d")
today_day = now.strftime("%A")

# 브라우저 꺼짐 방지 옵션
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--single-process")
chrome_options.add_argument("--disable-dev-shm-usage")
# Get driver and open url
driver = webdriver.Chrome(options=chrome_options)

def check_commute(id, pw, go_type):
    try:
        # 로그인 URL 설정 및 접속
        login_url = "https://gw.hdc-labs.co.kr/gw/uat/uia/egovLoginUsr.do"
        driver.get(login_url)

        driver.find_element(By.XPATH, '//*[@id="userId"]').send_keys(id)
        driver.find_element(By.XPATH, '//*[@id="userPw"]').send_keys(pw + Keys.ENTER)
        time.sleep(1)

        # 팝업창 뜰 경우 메인 윈도우만 남기고 close
        windows = driver.window_handles
        if len(windows) > 1:
            for window in windows:
                if window != windows[0]:    # 메인 윈도우 아닌 경우(팝업창인 경우)
                    print("pop up found")
                    driver.switch_to.window(window)

                    # 비밀번호 변경 팝업인지 정보 안내 팝업인지 구분
                    try:
                        if driver.find_element(By.CLASS_NAME, 'pop_wrap.password_change2'):
                            driver.find_element(By.CLASS_NAME, 'gray_btn').click()
                            time.sleep(1)
                            Alert(driver).accept()
                    except:
                        print("info pop up")
                        driver.close()  # 정보 팝업 -> 닫기

            driver.switch_to.window(windows[0])
            print('popup clear')
        time.sleep(2)

        login_flag = True

    except:
        if driver:
            driver.close()
        print('login error occured')
        return 'login error occured'
    if login_flag:
        # 출근
        if go_type == 1: 
            try:
                driver.find_element(By.ID, 'btnConfirm').click()
                return "출근 완료! 오늘도 화이팅!! 👊🏻"
            except:
                return "악...! 출근 버튼 안눌리넹! 뛰어!! 🏃🏻‍♀️"
        
        # 퇴근
        elif go_type == 2:
            try:
                driver.find_element(By.CSS_SELECTOR, "li[rel='tab2']").click()
                driver.find_element(By.ID, 'outBtn').click()
                
                driver.find_element(By.ID, 'btnConfirm').click()
                
                return "퇴근 완료! 오늘두 고생했어!! 🤸🏻‍♀️"
            except:
                return "퇴근이 안되넹.. 7층 가서 퇴근 찍고 가자~ 🏃🏻‍♀️"
            


        driver.quit()
        print('quit driver')
# print(check_commute(2310039, 'skarud@1028', 2))