import json
import platform
import os
import subprocess


class MissionComputer:
    '''
    화성 기지의 미션 컴퓨터 상태를 파악하기 위한 클래스
    '''

    def __init__(self):
        # 초기화 시 별도의 센서 데이터는 관리하지 않음
        pass

    def get_mission_computer_info(self):
        '''
        미션 컴퓨터의 시스템 정보를 JSON 형식으로 출력하는 메소드
        '''
        try:
            settings = self._read_settings()
            info = {}

            if settings.get('os', True):
                info['os'] = platform.system()
            if settings.get('os_version', True):
                info['os_version'] = platform.release()
            if settings.get('cpu_type', True):
                info['cpu_type'] = platform.machine()
            if settings.get('cpu_cores', True):
                info['cpu_cores'] = os.cpu_count()
            if settings.get('memory_size', True):
                # 총 메모리 크기 계산 (바이트 단위를 GB로 변환)
                try:
                    if platform.system() == 'Darwin':
                        mem_bytes = int(subprocess.check_output(
                            ['sysctl', '-n', 'hw.memsize']).strip())
                    else:
                        mem_bytes = os.sysconf('SC_PAGE_SIZE') * \
                            os.sysconf('SC_PHYS_PAGES')
                    info['memory_size'] = f'{round(mem_bytes / (1024**3), 2)} GB'
                except Exception:
                    info['memory_size'] = 'Unknown'

            print('\n[ Mission Computer Info ]')
            print(json.dumps(info, indent=4))
        except Exception as e:
            print(f'Error getting system info: {e}')

    def get_mission_computer_load(self):
        '''
        미션 컴퓨터의 실시간 부하 정보를 JSON 형식으로 출력하는 메소드
        '''
        try:
            settings = self._read_settings()
            load = {}

            if settings.get('cpu_usage', True):
                try:
                    if platform.system() == 'Darwin':
                        # macOS의 top 명령어를 사용하여 실시간 CPU 사용량 확인
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
                    else:
                        # 리눅스 등에서는 Load Average를 이용
                        load['cpu_usage'] = f'{os.getloadavg()[0] * 100}% (Load Avg)'
                except Exception:
                    load['cpu_usage'] = 'Unknown'

            if settings.get('memory_usage', True):
                try:
                    if platform.system() == 'Darwin':
                        # macOS의 vm_stat를 이용한 실시간 메모리 사용률 계산
                        vm = subprocess.check_output(['vm_stat']).decode()
                        vm_dict = {}
                        for line in vm.split('\n')[1:]:
                            if ':' in line:
                                key, val = line.split(':')
                                vm_dict[key.strip()] = int(val.strip().strip('.'))
                        
                        page_size = int(subprocess.check_output(
                            ['sysctl', '-n', 'hw.pagesize']).strip())
                        active = vm_dict.get('Pages active', 0) * page_size
                        wired = vm_dict.get('Pages wired down', 0) * page_size
                        free = vm_dict.get('Pages free', 0) * page_size
                        total = active + wired + free
                        used_percent = ((active + wired) / total) * 100
                        load['memory_usage'] = f'{round(used_percent, 2)}%'
                    else:
                        load['memory_usage'] = 'Unknown'
                except Exception:
                    load['memory_usage'] = 'Unknown'

            print('\n[ Mission Computer Load ]')
            print(json.dumps(load, indent=4))
        except Exception as e:
            print(f'Error getting system load: {e}')

    def _read_settings(self):
        '''
        setting.txt 파일을 읽어 출력 항목 설정을 가져오는 내부 메소드
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


if __name__ == '__main__':
    # MissionComputer 클래스를 runComputer 라는 이름으로 인스턴스화
    runComputer = MissionComputer()

    # 시스템 정보 출력 메소드 호출
    runComputer.get_mission_computer_info()

    # 실시간 부하 정보 출력 메소드 호출
    runComputer.get_mission_computer_load()
