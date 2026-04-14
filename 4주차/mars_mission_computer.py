import json       # 데이터 구조를 JSON 문자열로 변환하거나 출력할 때 사용 (표준 라이브러리)
import platform   # 운영체제의 이름, 버전, 하드웨어 아키텍처 등 정적 정보 수집 (표준 라이브러리)
import os         # 파일 경로 조작, CPU 코어 수 확인 등 OS 기능 제어 (표준 라이브러리)
import subprocess # 외부 시스템 명령어(top, wmic 등)를 실행하고 결과를 수집 (표준 라이브러리)
import random     # 센서 데이터 시뮬레이션을 위한 랜덤 값 생성 (표준 라이브러리)
import datetime   # 로그 출력 시 현재 시간 기록 (표준 라이브러리)
import time       # 루프 실행 간격 조절 (표준 라이브러리)
import threading  # 키보드 입력 처리를 위한 멀티스레딩 (표준 라이브러리)


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


class SystemStatusManager:
    '''
    시스템의 상태 정보 및 부하를 관리하는 클래스 (Composition용)
    '''

    def get_info(self, settings):
        '''
        시스템 정보를 수집하여 반환
        '''
        info = {}
        system_os = platform.system()
        
        if settings.get('os', True):
            info['os'] = system_os
        if settings.get('os_version', True):
            info['os_version'] = platform.release()
        if settings.get('cpu_type', True):
            info['cpu_type'] = platform.machine()
        if settings.get('cpu_cores', True):
            info['cpu_cores'] = os.cpu_count()
        if settings.get('memory_size', True):
            try:
                if system_os == 'Darwin':
                    # macOS: sysctl 명령어 활용 (바이트 단위)
                    mem_bytes = int(subprocess.check_output(
                        ['sysctl', '-n', 'hw.memsize']).strip())
                elif system_os == 'Windows':
                    # Windows: wmic 명령어 활용 (바이트 단위)
                    output = subprocess.check_output(
                        ['wmic', 'computersystem', 'get', 'totalphysicalmemory']).decode()
                    mem_bytes = int(output.strip().split('\n')[1].strip())
                else:
                    # Linux/Unix: 페이지 크기 * 페이지 수
                    mem_bytes = os.sysconf('SC_PAGE_SIZE') * \
                                os.sysconf('SC_PHYS_PAGES')
                
                # 바이트 단위를 GB 단위로 변환 (1024**3 = 1GB)
                info['memory_size'] = f'{round(mem_bytes / (1024**3), 2)} GB'
            except Exception:
                info['memory_size'] = 'Unknown'
        return info

    def get_load(self, settings):
        '''
        실시간 부하 정보를 수집하여 반환
        '''
        load = {}
        system_os = platform.system()

        # CPU 사용률 측정
        if settings.get('cpu_usage', True):
            try:
                if system_os == 'Darwin':
                    # macOS: top 명령어로 실시간 사용량 확인
                    top_output = subprocess.check_output(
                        ['top', '-l', '1', '-n', '0']).decode()
                    for line in top_output.split('\n'):
                        if 'CPU usage' in line:
                            parts = line.split(':')
                            usage_parts = parts[1].split(',')
                            user = float(usage_parts[0].strip().split('%')[0])
                            sys = float(usage_parts[1].strip().split('%')[0])
                            load['cpu_usage'] = f'{user + sys}%'
                            break
                elif system_os == 'Windows':
                    # Windows: wmic 명령어로 사용률 가져오기
                    output = subprocess.check_output(
                        ['wmic', 'cpu', 'get', loadpercentage]).decode()
                    load['cpu_usage'] = output.strip().split('\n')[1].strip() + '%'
                else:
                    # Linux 등: Load Average 활용
                    load['cpu_usage'] = f'{os.getloadavg()[0] * 100}% (Load Avg)'
            except Exception:
                load['cpu_usage'] = 'Unknown'

        # 메모리 사용률 측정
        if settings.get('memory_usage', True):
            try:
                if system_os == 'Darwin':
                    # macOS: 실제 가용량(Free + Inactive + Speculative) 기반 계산
                    vm = subprocess.check_output(['vm_stat']).decode()
                    vm_dict = {}
                    for line in vm.split('\n')[1:]:
                        if ':' in line:
                            key, val = line.split(':')
                            vm_dict[key.strip()] = int(val.strip().strip('.'))
                    
                    page_size = int(subprocess.check_output(
                        ['sysctl', '-n', 'hw.pagesize']).strip())
                    total_mem_bytes = int(subprocess.check_output(
                        ['sysctl', '-n', 'hw.memsize']).strip())
                    
                    free = vm_dict.get('Pages free', 0) * page_size
                    inactive = vm_dict.get('Pages inactive', 0) * page_size
                    speculative = vm_dict.get('Pages speculative', 0) * page_size
                    
                    available = free + inactive + speculative
                    used = total_mem_bytes - available
                    load['memory_usage'] = f'{round((used / total_mem_bytes) * 100, 2)}%'
                elif system_os == 'Windows':
                    # Windows: (전체 - 가용) / 전체 계산
                    t_out = subprocess.check_output(
                        ['wmic', 'computersystem', 'get', 'totalphysicalmemory']).decode()
                    f_out = subprocess.check_output(
                        ['wmic', 'os', 'get', 'freephysicalmemory']).decode()
                    total = int(t_out.strip().split('\n')[1].strip())
                    free = int(f_out.strip().split('\n')[1].strip()) * 1024
                    load['memory_usage'] = f'{round(((total - free) / total) * 100, 2)}%'
                elif system_os == 'Linux':
                    # Linux: /proc/meminfo 활용
                    with open('/proc/meminfo', 'r') as f:
                        lines = f.readlines()
                    mem_info = {l.split(':')[0].strip(): int(l.split(':')[1].strip().split()[0]) for l in lines}
                    total = mem_info.get('MemTotal', 0)
                    available = mem_info.get('MemAvailable', total)
                    load['memory_usage'] = f'{round(((total - available) / total) * 100, 2)}%'
                else:
                    load['memory_usage'] = 'Unknown'
            except Exception:
                load['memory_usage'] = 'Unknown'
        return load


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
        # DummySensor 클래스를 ds라는 이름으로 인스턴스화
        self.ds = DummySensor()
        # SystemStatusManager 클래스를 status_manager라는 이름으로 인스턴스화 (Composition)
        self.status_manager = SystemStatusManager()
        self.is_running = True
        self.history = []  # 5분 평균 계산을 위한 데이터 저장 리스트

    def get_mission_computer_info(self):
        '''
        미션 컴퓨터의 시스템 정보를 JSON 형식으로 출력
        '''
        try:
            settings = self._read_settings()
            info = self.status_manager.get_info(settings)
            print('\n[ Mission Computer Info ]')
            print(json.dumps(info, indent=4))
        except Exception as e:
            print(f'Error getting system info: {e}')

    def get_mission_computer_load(self):
        '''
        미션 컴퓨터의 실시간 부하를 JSON 형식으로 출력
        '''
        try:
            settings = self._read_settings()
            load = self.status_manager.get_load(settings)
            print('\n[ Mission Computer Load ]')
            print(json.dumps(load, indent=4))
        except Exception as e:
            print(f'Error getting system load: {e}')

    def _read_settings(self):
        '''
        setting.txt 파일을 읽어 출력 항목 설정을 가져옴
        '''
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

    def get_sensor_data(self):
        '''
        센서 데이터를 가져와서 출력하고 5초마다 반복함
        '''
        # 특정 키(q)를 입력할 경우 반복 출력을 멈춤
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

                # 3. 5분(300초)마다 각 환경값에 대한 평균값 출력
                current_time = time.time()
                if current_time - last_avg_time >= 300:
                    self._print_averages()
                    self.history = []
                    last_avg_time = current_time

                # 5초에 한번씩 반복
                time.sleep(5)
        except KeyboardInterrupt:
            self.is_running = False

        # 반복 중단 시 지정된 문구 출력
        print('Sytem stoped….')

    def _wait_for_stop(self):
        '''
        특정 키 입력을 대기하여 시스템 중지 플래그를 설정
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
        저장된 데이터들의 평균값을 계산하여 출력
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
    # MissionComputer 클래스를 runComputer 라는 이름으로 인스턴스화
    runComputer = MissionComputer()

    # 시스템 정보 및 부하 정보 출력
    runComputer.get_mission_computer_info()
    runComputer.get_mission_computer_load()

    # 센서 데이터 수집 시작
    runComputer.get_sensor_data()
