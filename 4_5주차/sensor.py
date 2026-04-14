import random

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
        '''지정된 범위 내에서 랜덤하게 환경 값을 생성'''
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
        '''현재 환경 값을 갱신하여 반환'''
        self.set_env()
        return self.env_values
