import random
import datetime
import json
import time
import threading


class DummySensor:
    '''
    화성 기지의 환경 데이터를 시뮬레이션하는 더미 센서 클래스
    '''

    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }

    def set_env(self):
        '''
        지정된 범위 내에서 랜덤하게 환경 값을 생성하여 env_values에 설정
        '''
        self.env_values['mars_base_internal_temperature'] = \
            round(random.uniform(18, 30), 2)
        self.env_values['mars_base_external_temperature'] = \
            round(random.uniform(0, 21), 2)
        self.env_values['mars_base_internal_humidity'] = \
            round(random.uniform(50, 60), 2)
        self.env_values['mars_base_external_illuminance'] = \
            round(random.uniform(500, 715), 2)
        self.env_values['mars_base_internal_co2'] = \
            round(random.uniform(0.02, 0.1), 4)
        self.env_values['mars_base_internal_oxygen'] = \
            round(random.uniform(4, 7), 2)

    def get_env(self):
        '''
        현재 환경 값을 반환
        '''
        self.set_env()
        return self.env_values


class MissionComputer:
    '''
    화성 기지의 미션 컴퓨터 클래스
    '''

    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }
        # 문제 3에서 제작한 DummySensor 클래스를 ds라는 이름으로 인스턴스화
        self.ds = DummySensor()
        self.is_running = True
        self.history = []  # 5분 평균 계산을 위한 데이터 저장 리스트

    def get_sensor_data(self):
        '''
        센서 데이터를 가져와서 출력하고 5초마다 반복함
        '''
        # 특정 키(q)를 입력할 경우 반복 출력을 멈춤 (보너스 과제)
        print("Press 'q' then Enter to stop the mission computer.")
        stop_thread = threading.Thread(target=self._wait_for_stop)
        stop_thread.daemon = True
        stop_thread.start()

        last_avg_time = time.time()

        try:
            while self.is_running:
                # 1. 센서의 값을 가져와서 env_values에 담음
                sensor_data = self.ds.get_env()
                self.env_values.update(sensor_data)
                self.history.append(self.env_values.copy())

                # 2. env_values의 값을 JSON 형태로 화면에 출력
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f'\n[ {timestamp} ]')
                print(json.dumps(self.env_values, indent=4))

                # 3. 5분(300초)마다 각 환경값에 대한 평균값 출력 (보너스 과제)
                current_time = time.time()
                if current_time - last_avg_time >= 300:
                    self._print_averages()
                    self.history = []
                    last_avg_time = current_time

                # 5초에 한번씩 반복
                time.sleep(5)
        except KeyboardInterrupt:
            self.is_running = False

        # 반복 중단 시 지정된 문구 출력 (보너스 과제)
        print('Sytem stoped….')

    def _wait_for_stop(self):
        '''
        특정 키 입력을 대기하여 시스템 중지 플래그를 설정 (보너스 과제)
        '''
        while self.is_running:
            try:
                user_input = input()
                if user_input.lower() == 'q':
                    self.is_running = False
                    break
            except EOFError:
                break

    def _print_averages(self):
        '''
        저장된 데이터들의 평균값을 계산하여 출력 (보너스 과제)
        '''
        if not self.history:
            return

        print('\n' + '=' * 40)
        print('--- 5-Minute Average Report ---')
        keys = self.history[0].keys()
        for key in keys:
            avg_val = sum(item[key] for item in self.history) / len(self.history)
            print(f'{key}_average: {round(avg_val, 4)}')
        print('=' * 40 + '\n')


if __name__ == '__main__':
    # MissionComputer 클래스를 RunComputer 라는 이름으로 인스턴스화
    RunComputer = MissionComputer()

    # RunComputer 인스턴스의 get_sensor_data() 메소드를 호출
    RunComputer.get_sensor_data()
