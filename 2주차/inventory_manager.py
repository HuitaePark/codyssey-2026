import pickle  # 보너스 작업을 위해 바이너리 파일 처리에 사용되는 표준 라이브러리

def process_inventory():
    """
    주어진 요구 사항에 따라 화성 기지 인벤토리 리스트를 처리하는 메인 함수입니다.
    """
    input_filename = 'Mars_Base_Inventory_List.csv'
    danger_filename = 'Mars_Base_Inventory_danger.csv'
    binary_filename = 'Mars_Base_Inventory_List.bin'

    inventory_list = []

    # 작업 1 & 2: CSV 파일을 읽고 파이썬 리스트로 변환
    print('--- [작업 1] Mars_Base_Inventory_List.csv 읽기 및 출력 ---')
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            header = f.readline().strip().split(',')
            print(f'헤더: {header}')
            
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # 각 줄을 읽을 때마다 출력
                print(line)
                
                # 분리 및 리스트로 변환
                row = line.split(',')
                # 정렬 및 필터링을 위해 인화성(Flammability)을 float로 변환
                try:
                    row[4] = float(row[4])
                except ValueError:
                    # "Various" 또는 숫자가 아닌 값이 있는 경우 0.0으로 설정하거나 처리
                    row[4] = 0.0
                
                inventory_list.append(row)
                
    except FileNotFoundError:
        print(f"오류: '{input_filename}' 파일을 찾을 수 없습니다.")
        return
    except Exception as e:
        print(f'읽기 중 예기치 않은 오류가 발생했습니다: {e}')
        return

    # 작업 3: 인화성을 기준으로 내림차순 정렬
    # lambda를 사용하여 5번째 열(인덱스 4)을 기준으로 정렬
    inventory_list.sort(key=lambda x: x[4], reverse=True)

    # 작업 4: 인화성이 0.7 이상인 항목을 필터링하고 출력
    print('\n--- [작업 4] 인화성이 0.7 이상인 항목 ---')
    danger_list = [item for item in inventory_list if item[4] >= 0.7]
    
    for item in danger_list:
        print(item)

    # 작업 5: 인화성이 높은 항목을 CSV로 저장
    print(f'\n--- [작업 5] 위험 리스트를 {danger_filename}으로 저장 중 ---')
    try:
        with open(danger_filename, 'w', encoding='utf-8') as f:
            # 헤더 작성
            f.write(','.join(header) + '\n')
            for item in danger_list:
                # CSV를 위해 다시 문자열로 변환
                str_item = [str(val) for val in item]
                f.write(','.join(str_item) + '\n')
    except Exception as e:
        print(f'{danger_filename} 저장 중 오류 발생: {e}')

    # 보너스 1: 정렬된 리스트를 바이너리 파일로 저장
    print(f'\n--- [보너스 1] 정렬된 리스트를 {binary_filename}으로 저장 중 ---')
    try:
        with open(binary_filename, 'wb') as f:
            pickle.dump(inventory_list, f)
    except Exception as e:
        print(f'바이너리 파일 저장 중 오류 발생: {e}')

    # 보너스 2: 바이너리 파일을 읽고 내용 출력
    print(f'\n--- [보너스 2] {binary_filename} 읽기 및 출력 ---')
    try:
        with open(binary_filename, 'rb') as f:
            loaded_data = pickle.load(f)
            for row in loaded_data:
                print(row)
    except Exception as e:
        print(f'바이너리 파일 읽기 중 오류 발생: {e}')

    # 보너스 3에 대한 설명
    print_explanation()

def print_explanation():
    """
    텍스트 파일과 바이너리 파일의 차이점을 출력합니다.
    """
    explanation = '''
--- [보너스 3] 비교: 텍스트 파일 vs 바이너리 파일 ---

1. 텍스트 파일 (.csv, .txt):
   - 정의: 데이터를 문자 시퀀스(예: UTF-8, ASCII)로 저장합니다.
   - 장점:
     - 사람이 읽을 수 있음: 어떤 텍스트 에디터(메모장, Vim 등)로도 열고 수정할 수 있습니다.
     - 이식성: 서로 다른 운영 체제 간에 공유하기 쉽습니다.
   - 단점:
     - 공간 효율성이 낮음: 숫자가 문자열로 저장됩니다 (예: "0.78"은 float의 4/8바이트 대신 4바이트를 차지함).
     - 파싱 속도가 느림: 읽을 때마다 매번 파싱(쉼표로 분리, 타입 변환)해야 합니다.

2. 바이너리 파일 (.bin, .dat):
   - 정의: 메모리에 표현되는 것과 동일한 형식(비트 및 바이트)으로 데이터를 저장합니다.
   - 장점:
     - 공간 효율적: 모든 값에 대해 문자 인코딩을 사용하지 않으므로 크기가 훨씬 작아지는 경우가 많습니다.
     - 빠른 성능: 수동 파싱 없이 메모리 구조(파이썬의 pickle 등)로 직접 읽어올 수 있습니다.
     - 보안: 특정 소프트웨어 없이는 사람이 쉽게 읽을 수 없어 기본적인 난독화 기능을 제공합니다.
   - 단점:
     - 사람이 읽을 수 없음: 텍스트 에디터에서 열면 "알 수 없는 기호"가 나타납니다.
     - 이식성 문제: 특정 아키텍처나 직렬화 라이브러리(예: pickle 버전)에 의존하는 경우가 있습니다.
'''
    print(explanation)

if __name__ == '__main__':
    process_inventory()
