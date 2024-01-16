from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import psutil
import platform
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
import os
import logging

global_token = ""

driver = None

chromeOpen = False

def close_all_chrome():
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == 'chrome':
            try:
                # 해당 Chrome 프로세스 종료
                psutil.Process(process.info['pid']).terminate()
            except Exception as e:
                print(f"Error terminating Chrome process: {e}")
    
def create_app():
    logging.basicConfig(filename='app.log', level=logging.INFO)
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    # 불필요한 에러 메시지 없애기
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    current_os = platform.system()


    cred_path = os.path.join(os.path.dirname(__file__), "attent-a6682-firebase-adminsdk-ekjpv-9b5e0f7ee6.json")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
        

    # 윈도우인지 확인
    is_windows = (current_os == 'Windows')

    if is_windows:
        print("현재 실행 중인 운영 체제는 Windows입니다.")
    else:
        print("현재 실행 중인 운영 체제는 Windows가 아닙니다.")
        chrome_options.add_argument('--headless')
        
        close_all_chrome()

    # 브라우저 생성
    app = Flask(__name__)
    CORS(app)
    
    app.logger.info("정상적으로 실행됐어요!")
    
    def toggleChrome():
        global chromeOpen
        if chromeOpen:
            print("크롬이 켜져 있었어요. 끌게요")
            app.logger.info("크롬이 켜져 있어요 끌게요")
    
        else:
            print("크롬이 꺼져 있었어요. 켤게요")
            
            app.logger.info("크롬이 꺼져 있어요. 결게요")
        chromeOpen = not(chromeOpen)
    
    @app.route('/')
    def index():
        return render_template('index.html')
    @app.route('/test')
    def hello_world():
        print("옴!")
        app.logger.info("옴!")
        return "Hello World!"
    
    @app.route('/set_global_token')
    def test_set_token():
        global global_token
        global_token = "eeeeeee"
        return "설정함"
        
    @app.route('/get_global_token')
    def test_get_token():
        global global_token
        return global_token
        
    @app.route('/isChromeOpen')
    def isChromeOpen():
        global chromeOPen
        if chromeOpen:
            print("크롬이 켜져있어요")
            app.logger.info("크롬이 켜져있어요")
        else:
            print("크롬이 꺼져있어요")
            app.logger.info("크롬이 꺼져있어요")
        return str(chromeOpen)
    
    @app.route('/initiating', methods=['POST'])
    def initiating():
        global driver
        print("로그인 버튼이 눌렸어요")
        app.logger.info("로그인 버튼이 눌렸어요")
        kakao_id = request.get_json()['kakao_id']
        kakao_password = request.get_json()['kakao_password']
        print("카카오 아이디 : " + kakao_id)
        app.logger.info("카카오이이디: " + kakao_id)
        print("카카오 비밀번호 : " + kakao_password)
        app.logger.info("카카오비밀번호: " + kakao_password)
        driver = webdriver.Chrome(options=chrome_options)
        toggleChrome()
        driver.get('https://hanghae99.spartacodingclub.kr/v2/attendance')
        time.sleep(1)
        try:
            login_button = driver.find_element(By.XPATH, "//a[contains(text(), '로그인')]")
            print("로그인페이지")   
            app.logger.info("로그인페이지")
            driver.execute_script("arguments[0].click();", login_button)
            time.sleep(1)
            kakao_button = driver.find_elements(By.XPATH, "//button")
            for i in kakao_button:
                if i.text == '카카오로 3초만에 시작하기':
                    kakao_button = i
                    break
            driver.execute_script("arguments[0].click();", kakao_button)
            input_element = driver.find_element(By.XPATH, "//input[@placeholder='카카오메일 아이디, 이메일, 전화번호 ']")
            driver.execute_script("arguments[0].scrollIntoView();", input_element)
            input_element.send_keys(kakao_id)
            input_element = driver.find_element(By.XPATH, "//input[@placeholder='비밀번호']")
            driver.execute_script("arguments[0].scrollIntoView();", input_element)
            input_element.send_keys(kakao_password)
            checkbox = driver.find_element(By.XPATH, "//label[@id='label-saveSignedIn']")
            driver.execute_script("arguments[0].click();", checkbox)
            kakao_submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            driver.execute_script("arguments[0].scrollIntoView();", kakao_submit_button)
            driver.execute_script("arguments[0].click();", kakao_submit_button)
            time.sleep(1)
            try:
                print("2단계인증시도")
                
                app.logger.info("2단계인증시도")
                driver.find_element(By.XPATH, "//h2[contains(text(), '2단계 인증을 진행해 주세요.')]")
                
                print("계속시도중")
                
                app.logger.info("계속시도중")
                flag = False
                for i in range(4*60):
                    url = driver.current_url
                    current = url.split("?")[0]
                    url_list = current.split("/")
                    if url_list[3] == "oauth" and url_list[4] == "authorize":
                        flag = True
                        break
                    time.sleep(1)
                if flag == False:
                    toggleChrome()
                    if (driver != None): driver.quit()
                    return "2단계 인증에 실패했어요(Time out)"
                
                kakao_last_button = driver.find_element(By.XPATH, "//button[@name='user_oauth_approval']")
                
                driver.execute_script("arguments[0].click();", kakao_last_button)
                driver.get('https://hanghae99.spartacodingclub.kr/v2/attendance')
                print("출첵 페이지 도착")
                app.logger.info("출첵페이지 도착")
                return "성공"
            except NoSuchElementException:
                print("잘못된 아이디 혹은 비밀번호")
                app.logger.info("잘못된 아이디 혹은 비밀번호")
                toggleChrome()
                if (driver != None): driver.quit()
                return "잘못된 아이디 혹은 비밀번호"
            
        except NoSuchElementException:
            print("로그인버튼찾지못함")
            app.logger.info("로그인버튼 찾지못함")
            toggleChrome()
            if (driver != None): driver.quit()
            return "이미 로그인 되어있음"
        
          
    @app.route('/makeSchedule')    
    def make_schedule():
        
        global driver
        print("스케쥴만들기를 시작해요")
        app.logger.info("스케쥴만들기를 시작해요")
        scheduler = BlockingScheduler()
        @scheduler.scheduled_job('cron', hour='8', minute='30', second=0, id='test_1')
        def job1():
            try:
                print("출첵을 시도합니다")
                app.logger.info("출첵을 시도합니다.")
                driver.refresh()
                start_study_button = driver.find_element(By.XPATH, "//span[contains(text(), '학습 시작')]")
                # start_study_button.click()
                driver.execute_script("arguments[0].click();", start_study_button)
                print("출첵을 완료했습니다.")
                app.logger.info("출첵을 완료했습니다.")
                sendPushDef("자동출첵", "출첵 체크를 완료했어요!")
                
            except NoSuchElementException:
                print("공부 시작 버튼을 찾지 못함")
                app.logger.info("공부시작버튼을 찾지 못함")
            
        @scheduler.scheduled_job('cron', hour='21', minute='30', second=0, id='test_2')
        def job2():
            try:
                print("출석 체크아웃을 시도합니다")
                app.logger.info("출석 체크아웃을 시도합니다.")
                driver.refresh()
                end_study_button = driver.find_element(By.XPATH, "//span[contains(text(), '학습 종료')]")
                # end_study_button.click()
                driver.execute_script("arguments[0].click();", end_study_button)
                print("출석 체크아웃을 완료했습니다")
                app.logger.info("출석 체크아웃을 완료했습니다.")
                
                sendPushDef("자동출첵", "체크 아웃을 완료했어요!")
            except NoSuchElementException:
                print("공부 끝 버튼을 찾지 못함")
                app.logger.info("공부 끝 버튼을 찾지 못함")
        
        @scheduler.scheduled_job('interval', seconds=1200, id='test_3')
        def refresh(): 
            global global_token
            global driver
            app.logger.info("새로고침합니다.")
            app.logger.info("토큰 : " + global_token)
            print("새로고침 시작")
            print(global_token)
            print(driver)
            try:
                start_study_button = driver.find_element(By.XPATH, "//span[contains(text(), '학습 시작')]")
                app.logger.info(start_study_button.text + "버튼이 있어요")
            except NoSuchElementException:
                app.logger.info("공부 시작 버튼이 없어요")
                driver.get('https://hanghae99.spartacodingclub.kr/v2/attendance')
            try:
                end_study_button = driver.find_element(By.XPATH, "//span[contains(text(), '학습 종료')]")
                app.logger.info(end_study_button.text + "버튼이 있어요")
            except NoSuchElementException:
                app.logger.info("공부끝 버튼이 없어요")
                driver.get('https://hanghae99.spartacodingclub.kr/v2/attendance')
            app.logger.info("무사히 탐색을 마쳤어요")
            driver.refresh()
               
        scheduler.start()
        return "yes"
    
    @app.route("/checkToken")
    def checkToken():
        global global_token
        app.logger.info("토큰을 확인해요")
        return global_token
    
    @app.route("/sendToken/<token>")
    def sendToken(token):
        global global_token
        print("토큰을 저장해요")
        app.logger.info("토큰을 저장해요")
        global_token = token
        return "yes"
    
    @app.route("/sendPush")
    def sendPush():
        app.logger.info("푸쉬알람을 보내요")
        global global_token
        message = messaging.Message(
            data={
                'title': 'title',
                'body': 'body',
            },
            token=global_token,
        )
        
        response = messaging.send(message)
        print('Successfully sent message:', response)
        app.logger.info('Successfully sent message:', response)
        return "보내써요"
        
    def sendPushDef(title, body):
        app.logger.info("푸쉬알람을 보내요" + title + " " + body)
        global global_token
        message = messaging.Message(
            data={
                'title': title,
                'body': body,
            },
            token=global_token,
        )
        response = messaging.send(message)
        print('Successfully sent message:', response)
        app.logger.info('Successfully sent message:', response)
        return "보내써요"
        
    @app.route("/logout")
    def logout():
        global driver
        print("로그아웃 왔어요")
        app.logger.info("로그아웃 왔어요")
        toggleChrome()
        if (driver != None): driver.quit()
        driver = None
        return "yes"
        

    if __name__ == '__main__':
        app.run('0.0.0.0', port=5000, debug=True)
        
    return app