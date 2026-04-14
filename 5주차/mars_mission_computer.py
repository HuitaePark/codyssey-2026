import json
import platform
import os
import subprocess


class MissionComputer:
    '''
    화성 기지 미션 컴퓨터의 시스템 상태를 점검하고 부하를 측정하는 클래스
    '''

    def __init__(self):
        '''
        MissionComputer 클래스 초기화
        '''
        pass

    def get_mission_computer_info(self):
        '''
        시스템의 정적 정보(OS, CPU, 메모리 사양 등)를 수집하여 JSON 형식으로 출력
        '''
        try:
            # setting.txt에서 출력 여부 설정을 읽어옴
            settings = self._read_settings()
            info = {}

            # 운영체제 이름 (예: Darwin, Windows, Linux)
            if settings.get('os', True):
                info['os'] = platform.system()
            
            # 운영체제 릴리스 버전
            if settings.get('os_version', True):
                info['os_version'] = platform.release()
            
            # CPU 아키텍처 타입 (예: x86_64, arm64)
            if settings.get('cpu_type', True):
                info['cpu_type'] = platform.machine()
            
            # 논리 CPU 코어 수
            if settings.get('cpu_cores', True):
                info['cpu_cores'] = os.cpu_count()
            
            # 전체 물리 메모리 크기 계산
            if settings.get('memory_size', True):
                try:
                    system_os = platform.system()
                    if system_os == 'Darwin':
                        # macOS: sysctl 명령어를 통해 전체 메모리 바이트 수를 가져옴
                        mem_bytes = int(subprocess.check_output(
                            ['sysctl', '-n', 'hw.memsize']).strip())
                    elif system_os == 'Windows':
                        # Windows: wmic 명령어를 통해 물리 메모리 총량을 바이트 단위로 가져옴
                        output = subprocess.check_output(
                            ['wmic', 'computersystem', 'get', 'totalphysicalmemory']).decode()
                        mem_bytes = int(output.strip().split('\n')[1].strip())
                    else:
                        # Linux/Unix: 페이지 크기와 총 페이지 수를 곱하여 계산
                        mem_bytes = os.sysconf('SC_PAGE_SIZE') * \
                            os.sysconf('SC_PHYS_PAGES')
                    # 바이트 단위를 GB 단위로 변환하여 저장 (1024**3 = 1GB)
                    info['memory_size'] = f'{round(mem_bytes / (1024**3), 2)} GB'
                except Exception:
                    info['memory_size'] = 'Unknown'

            # 최종 수집된 정보를 JSON 형태로 보기 좋게 출력
            print('\n[ Mission Computer Info ]')
            print(json.dumps(info, indent=4))
        except Exception as e:
            print(f'Error getting system info: {e}')

    def get_mission_computer_load(self):
        '''
        시스템의 실시간 부하(CPU 사용률, 메모리 점유율)를 측정하여 JSON 형식으로 출력
        '''
        try:
            settings = self._read_settings()
            load = {}

            # CPU 실시간 사용량 측정
            if settings.get('cpu_usage', True):
                try:
                    if platform.system() == 'Darwin':
                        # macOS: top 명령어를 1회 실행하여 user+sys 사용량을 파싱
                        top_output = subprocess.check_output(
                            ['top', '-l', '1', '-n', '0']).decode()
                        for line in top_output.split('\n'):
                            if 'CPU usage' in line:
                                # 예: "CPU usage: 10.5% user, 15.2% sys, 74.3% idle"
                                parts = line.split(':')
                                usage_parts = parts[1].split(',')
                                user = float(usage_parts[0].strip().split('%')[0])
                                sys = float(usage_parts[1].strip().split('%')[0])
                                load['cpu_usage'] = f'{user + sys}%'
                                break
                    else:
                        # 기타 OS: 최근 1분간의 Load Average를 백분율로 표시 (근사치)
                        load['cpu_usage'] = f'{os.getloadavg()[0] * 100}% (Load Avg)'
                except Exception:
                    load['cpu_usage'] = 'Unknown'

            # 메모리 실시간 사용량 측정
            if settings.get('memory_usage', True):
                try:
                    if platform.system() == 'Darwin':
                        # macOS: vm_stat 결과를 파싱하여 실제 사용 중인 페이지 비율 계산
                        vm = subprocess.check_output(['vm_stat']).decode()
                        vm_dict = {}
                        for line in vm.split('\n')[1:]:
                            if ':' in line:
                                key, val = line.split(':')
                                # 페이지 수는 숫자로 변환 (마지막 마침표 제거)
                                vm_dict[key.strip()] = int(val.strip().strip('.'))
                        
                        # 하드웨어 페이지 크기 확인
                        page_size = int(subprocess.check_output(
                            ['sysctl', '-n', 'hw.pagesize']).strip())
                        
                        # Active, Wired 페이지는 사용 중 / Free 페이지는 여유 공간
                        active = vm_dict.get('Pages active', 0) * page_size
                        wired = vm_dict.get('Pages wired down', 0) * page_size
                        free = vm_dict.get('Pages free', 0) * page_size
                        
                        total = active + wired + free
                        if total > 0:
                            used_percent = ((active + wired) / total) * 100
                            load['memory_usage'] = f'{round(used_percent, 2)}%'
                        else:
                            load['memory_usage'] = 'Unknown'
                    else:
                        load['memory_usage'] = 'Unknown'
                except Exception:
                    load['memory_usage'] = 'Unknown'

            # 부하 측정 결과를 JSON 형태로 출력
            print('\n[ Mission Computer Load ]')
            print(json.dumps(load, indent=4))
        except Exception as e:
            print(f'Error getting system load: {e}')

    def _read_settings(self):
        '''
        동일 디렉토리의 setting.txt 파일을 읽어 출력 항목 설정을 반환하는 내부 메소드
        '''
        settings = {}
        try:
            # 스크립트 파일의 절대 경로를 기준으로 setting.txt 위치 파악
            base_path = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_path, 'setting.txt')
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        # 'key = value' 형식의 라인을 파싱
                        if '=' in line:
                            key, value = line.strip().split('=')
                            # value가 'true'인 경우 True로 저장
                            settings[key.strip()] = value.strip().lower() == 'true'
        except Exception:
            # 파일 읽기 실패 시 빈 사전을 반환하여 기본값(True)을 사용하도록 함
            pass
        return settings


if __name__ == '__main__':
    # 1. MissionComputer 클래스를 runComputer 라는 이름으로 인스턴스화
    runComputer = MissionComputer()

    # 2. 시스템 기본 정보(OS, CPU 등) 출력 메소드 실행
    runComputer.get_mission_computer_info()

    # 3. 실시간 시스템 부하(CPU, 메모리) 출력 메소드 실행
    runComputer.get_mission_computer_load()
