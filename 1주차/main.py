# -*- coding: utf-8 -*-
'''
미션 컴퓨터 로그 분석 소프트웨어
한 박사를 위한 로그 분석 및 사고 원인 파악 도구
'''

import sys


def main():
    # 1. Hello Mars 출력
    print('Hello Mars')
    print('-' * 40)

    file_name = 'mission_computer_main.log'
    error_file_name = 'problematic_logs.txt'
    
    try:
        # 2. 로그 파일 읽기
        with open(file_name, 'r', encoding='utf8') as file:
            lines = file.readlines()
        
        if not lines:
            print('로그 파일이 비어 있습니다.')
            return

        # 헤더와 데이터 분리
        header = lines[0].strip()
        log_data = lines[1:]

        # 3. 전체 내용 출력 (원본 순서)
        print(f'[{file_name} 전체 내용]')
        for line in lines:
            print(line.strip())
        print('-' * 40)

        # 보너스 과제 1: 시간 역순 정렬 출력
        print('[로그 데이터 시간 역순 정렬]')
        reversed_logs = log_data[::-1]
        print(header)
        for log in reversed_logs:
            print(log.strip())
        print('-' * 40)

        # 보너스 과제 2: 문제가 되는 부분(unstable, explosion 등) 별도 저장
        problem_keywords = ('unstable', 'explosion', 'ERROR', 'WARNING')
        problematic_logs = []
        
        for log in log_data:
            if any(keyword in log.lower() for keyword in problem_keywords):
                problematic_logs.append(log)
        
        if problematic_logs:
            with open(error_file_name, 'w', encoding='utf8') as error_file:
                error_file.write(header + '\n')
                error_file.writelines(problematic_logs)
            print(f'문제가 되는 로그를 {error_file_name}에 저장했습니다.')
        
    except FileNotFoundError:
        print(f'오류: {file_name} 파일을 찾을 수 없습니다.')
    except PermissionError:
        print(f'오류: {file_name} 파일에 접근할 권한이 없습니다.')
    except Exception as e:
        print(f'알 수 없는 오류가 발생했습니다: {e}')


if __name__ == '__main__':
    main()
