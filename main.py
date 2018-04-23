from HashTagSearchManager import HashTagSearchManager
import logging as log
import os

if __name__ == '__main__':
    log.basicConfig(level=log.INFO)
    manager = HashTagSearchManager()
    while True:
        print("0. 사용법 출력")
        print("1. 일반 모드")
        print("2. 비교할 이미지 등록하기")
        print("3. 결과 보기")
        choice = int(input(">>> "))
        if choice == 0:
            print("일반 모드 - [키워드입력 -> 이미지 크롤링 -> 등록된 이미지와 비교 반복]")
            print("비교할 이미지 등록하기 - [비교할 이미지를 사전에 등록합니다]")
            print("결과보기 - 비교 결과를 봅니다")
        elif choice == 1:
            print("검색할 키워드를 입력하세요")
            keyword = input(">>> ")
            manager.extract_recent_tag(keyword)
        elif choice == 2:
            print("경로를 입력하세요")
            path = input(">>> ")
            if not os.path.exists(path):
                print("파일을 찾을 수 없습니다")
            else:
                manager.cur.execute(manager.source_image_insert_sql, (path,))
                manager.conn.commit()
                print("정상적으로 등록되었습니다")
        elif choice == 3:
            pass  # TODO(sprout): ...
