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
                if platform.system() == 'Darwin':
                    mem_bytes = int(subprocess.check_output(
                        ['sysctl', '-n', 'hw.memsize']).strip())
                else:
                    mem_bytes = os.sysconf('SC_PAGE_SIZE') * \
                                os.sysconf('SC_PHYS_PAGES')
                info['memory_size'] = f'{round(mem_bytes / (1024**3), 2)} GB'
            except Exception:
                info['memory_size'] = 'Unknown'
        return info

    def get_load(self, settings):
        '''시스템 실시간 부하를 측정'''
        load = {}
        if settings.get('cpu_usage', True):
            try:
                if platform.system() == 'Darwin':
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
                    load['cpu_usage'] = f'{os.getloadavg()[0] * 100}% (Load Avg)'
            except Exception:
                load['cpu_usage'] = 'Unknown'

        if settings.get('memory_usage', True):
            try:
                if platform.system() == 'Darwin':
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
                    if total > 0:
                        used_percent = ((active + wired) / total) * 100
                        load['memory_usage'] = f'{round(used_percent, 2)}%'
                    else:
                        load['memory_usage'] = 'Unknown'
                else:
                    load['memory_usage'] = 'Unknown'
            except Exception:
                load['memory_usage'] = 'Unknown'
        return load
