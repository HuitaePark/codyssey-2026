import platform
import os
import subprocess

class SystemStatusManager:
    '''
    시스템의 정보 및 실시간 부하를 관리하는 전담 클래스
    '''
    def get_info(self, settings):
        '''시스템 정적 정보를 수집'''
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
            try:
                system_os = platform.system()
                if system_os == 'Darwin':
                    # macOS: sysctl 명령어를 통해 전체 메모리 바이트(Byte) 수를 가져옵니다.
                    mem_bytes = int(subprocess.check_output(
                        ['sysctl', '-n', 'hw.memsize']).strip())
                elif system_os == 'Windows':
                    # Windows: wmic 명령어를 통해 물리 메모리 총량을 바이트(Byte) 단위로 가져옵니다.
                    # 'TotalPhysicalMemory'의 값만 필터링하여 가져옵니다.
                    output = subprocess.check_output(
                        ['wmic', 'computersystem', 'get', 'totalphysicalmemory']).decode()
                    # 출력 결과의 두 번째 줄에 있는 숫자 값을 추출하여 정수로 변환합니다.
                    mem_bytes = int(output.strip().split('\n')[1].strip())
                else:
                    # Linux/Unix: 페이지 크기(Page Size)와 총 페이지 수를 곱하여 전체 바이트를 계산합니다.
                    mem_bytes = os.sysconf('SC_PAGE_SIZE') * \
                                os.sysconf('SC_PHYS_PAGES')
                
                # [ 단위 변환 계산 상세 설명 ]
                # 1. 1024**3 (1024의 3제곱): 바이트(Byte)를 기가바이트(GB)로 변환하기 위한 분모입니다.
                # 2. round(..., 2): 계산된 결과를 소수점 둘째 자리까지 반올림합니다.
                info['memory_size'] = f'{round(mem_bytes / (1024**3), 2)} GB'
            except Exception:
                info['memory_size'] = 'Unknown'
        return info

    def get_load(self, settings):
        '''시스템 실시간 부하를 측정'''
        load = {}
        system_os = platform.system()

        # CPU 사용률 측정
        if settings.get('cpu_usage', True):
            try:
                if system_os == 'Darwin':
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
                    # Windows: wmic 명령어로 현재 CPU 사용률(%) 가져오기
                    output = subprocess.check_output(
                        ['wmic', 'cpu', 'get', 'loadpercentage']).decode()
                    load['cpu_usage'] = output.strip().split('\n')[1].strip() + '%'
                else:
                    # Linux 등: 최근 1분간의 Load Average를 백분율로 표시
                    load['cpu_usage'] = f'{os.getloadavg()[0] * 100}% (Load Avg)'
            except Exception:
                load['cpu_usage'] = 'Unknown'

        # 메모리 사용률 측정
        if settings.get('memory_usage', True):
            try:
                if system_os == 'Darwin':
                    # macOS: vm_stat 결과를 파싱
                    vm = subprocess.check_output(['vm_stat']).decode()
                    vm_dict = {}
                    for line in vm.split('\n')[1:]:
                        if ':' in line:
                            key, val = line.split(':')
                            vm_dict[key.strip()] = int(val.strip().strip('.'))
                    
                    # 하드웨어 페이지 크기와 전체 물리 메모리 크기 확인
                    page_size = int(subprocess.check_output(
                        ['sysctl', '-n', 'hw.pagesize']).strip())
                    total_mem_bytes = int(subprocess.check_output(
                        ['sysctl', '-n', 'hw.memsize']).strip())
                    
                    # 가용 가능한 메모리(Free + Inactive + Speculative)
                    # Inactive와 Speculative는 필요시 OS가 즉시 비워줄 수 있는 영역입니다.
                    free = vm_dict.get('Pages free', 0) * page_size
                    inactive = vm_dict.get('Pages inactive', 0) * page_size
                    speculative = vm_dict.get('Pages speculative', 0) * page_size
                    
                    available = free + inactive + speculative
                    used = total_mem_bytes - available
                    
                    if total_mem_bytes > 0:
                        used_percent = (used / total_mem_bytes) * 100
                        load['memory_usage'] = f'{round(used_percent, 2)}%'
                    else:
                        load['memory_usage'] = 'Unknown'
                elif system_os == 'Windows':
                    # Windows: 전체 물리 메모리와 가용 메모리를 가져와 계산
                    t_out = subprocess.check_output(
                        ['wmic', 'computersystem', 'get', 'totalphysicalmemory']).decode()
                    f_out = subprocess.check_output(
                        ['wmic', 'os', 'get', 'freephysicalmemory']).decode()
                    
                    total = int(t_out.strip().split('\n')[1].strip())
                    free = int(f_out.strip().split('\n')[1].strip()) * 1024  # KB to Byte
                    used_percent = ((total - free) / total) * 100
                    load['memory_usage'] = f'{round(used_percent, 2)}%'
                elif system_os == 'Linux':
                    # Linux: /proc/meminfo 파일에서 정보 추출
                    with open('/proc/meminfo', 'r') as f:
                        lines = f.readlines()
                    mem_info = {}
                    for line in lines:
                        parts = line.split(':')
                        if len(parts) == 2:
                            mem_info[parts[0].strip()] = int(parts[1].strip().split()[0])
                    total = mem_info.get('MemTotal', 0)
                    available = mem_info.get('MemAvailable', total)
                    if total > 0:
                        used_percent = ((total - available) / total) * 100
                        load['memory_usage'] = f'{round(used_percent, 2)}%'
                else:
                    load['memory_usage'] = 'Unknown'
            except Exception:
                load['memory_usage'] = 'Unknown'
        return load
