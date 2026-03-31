import random
import datetime


class DummySensor:
    '''
    화성 기지의 환경 데이터를 시뮬레이션하는 더미 센서 클래스
    '''

    def __init__(self):
        # 환경 변수들을 저장할 사전 객체 초기화
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
        # 내부 온도: 18~30도
        self.env_values['mars_base_internal_temperature'] = \
            round(random.uniform(18, 30), 2)
        # 외부 온도: 0~21도
        self.env_values['mars_base_external_temperature'] = \
            round(random.uniform(0, 21), 2)
        # 내부 습도: 50~60%
        self.env_values['mars_base_internal_humidity'] = \
            round(random.uniform(50, 60), 2)
        # 외부 광량: 500~715 W/m2
        self.env_values['mars_base_external_illuminance'] = \
            round(random.uniform(500, 715), 2)
        # 내부 이산화탄소 농도: 0.02~0.1%
        self.env_values['mars_base_internal_co2'] = \
            round(random.uniform(0.02, 0.1), 4)
        # 내부 산소 농도: 4%~7%
        self.env_values['mars_base_internal_oxygen'] = \
            round(random.uniform(4, 7), 2)

    def get_env(self):
        '''
        현재 환경 값을 반환하고, 파일에 로그를 남김 (보너스 과제 포함)
        '''
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_data = (
            f"{now}, "
            f"{self.env_values['mars_base_internal_temperature']}°C, "
            f"{self.env_values['mars_base_external_temperature']}°C, "
            f"{self.env_values['mars_base_internal_humidity']}%, "
            f"{self.env_values['mars_base_external_illuminance']}W/m2, "
            f"{self.env_values['mars_base_internal_co2']}%, "
            f"{self.env_values['mars_base_internal_oxygen']}%"
        )

        # 'sensor_log.txt' 파일에 로그 추가
        with open('sensor_log.txt', 'a', encoding='utf-8') as f:
            f.write(log_data + '\n')

        return self.env_values


if __name__ == '__main__':
    # DummySensor 클래스의 인스턴스 ds 생성
    ds = DummySensor()

    # 환경 값 설정
    ds.set_env()

    # 환경 값 확인 및 로그 기록
    current_env = ds.get_env()

    # 결과 출력
    print('--- 화성 기지 환경 센서 데이터 ---')
    for key, value in current_env.items():
        print(f'{key}: {value}')
    print('\n로그가 sensor_log.txt 파일에 저장되었습니다.')
