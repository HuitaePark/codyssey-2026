import json
import time
import datetime
import threading
import os
from sensor import DummySensor
from system_manager import SystemStatusManager

class MissionComputer:
    '''
    화성 기지의 통합 미션 컴퓨터 클래스
    센서 데이터 수집과 시스템 모니터링을 총괄함 (Composition 방식)
    '''
    def __init__(self):
        # 4주차 센서 로직 모듈화
        self.ds = DummySensor()
        # 5주차 시스템 관리 로직 모듈화
        self.status_manager = SystemStatusManager()
        self.is_running = True
        self.history = []

    def get_mission_computer_info(self):
        '''미션 컴퓨터의 시스템 정보 출력 (매니저 객체에 위임)'''
        try:
            settings = self._read_settings()
            info = self.status_manager.get_info(settings)
            print('\n[ Mission Computer Info ]')
            print(json.dumps(info, indent=4))
        except Exception as e:
            print(f'Error: {e}')

    def get_mission_computer_load(self):
        '''미션 컴퓨터의 실시간 부하 출력 (매니저 객체에 위임)'''
        try:
            settings = self._read_settings()
            load = self.status_manager.get_load(settings)
            print('\n[ Mission Computer Load ]')
            print(json.dumps(load, indent=4))
        except Exception as e:
            print(f'Error: {e}')

    def _read_settings(self):
        '''setting.txt 파일을 읽어 설정 반환'''
        settings = {}
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_path, 'setting.txt')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=')
                            settings[key.strip()] = value.strip().lower() == 'true'
        except Exception:
            pass
        return settings

    def run_monitor(self):
        '''실시간 센서 데이터 모니터링 루프 시작'''
        print("Press 'q' then Enter to stop the mission computer.")
        # 키보드 입력을 대기하는 별도 스레드 시작
        stop_thread = threading.Thread(target=self._wait_for_stop)
        stop_thread.daemon = True
        stop_thread.start()

        try:
            while self.is_running:
                # 센서 데이터 수집
                data = self.ds.get_env()
                self.history.append(data.copy())

                # 현재 시간과 데이터 출력
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f'\n[ {timestamp} ]')
                print(json.dumps(data, indent=4))

                # 5초 대기
                time.sleep(5)
        except KeyboardInterrupt:
            self.is_running = False
        
        print('System stopped.')

    def _wait_for_stop(self):
        '''시스템 종료를 위한 키 입력 대기'''
        while self.is_running:
            try:
                if input().lower() == 'q':
                    self.is_running = False
                    break
            except EOFError:
                break

if __name__ == '__main__':
    # MissionComputer 인스턴스화
    runComputer = MissionComputer()

    # 시스템 상태 점검 (5주차 요구사항)
    runComputer.get_mission_computer_info()
    runComputer.get_mission_computer_load()

    # 센서 모니터링 루프 시작 (4주차 요구사항)
    runComputer.run_monitor()
