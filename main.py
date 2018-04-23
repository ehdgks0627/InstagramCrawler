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
        while True:
            try:
                choice = int(input(">>> "))
                break
            except ValueError:
                continue
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
            print("100 : 완전일치")
            print("95  : 거의 유사함")
            print("80  : 약간 유사함")
            print("50  : 평균")
            while True:
                try:
                    threshold = float(input(">>> ")) / 100
                    break
                except ValueError:
                    continue

            sql = "SELECT value, post_id, Post.display_src, Post.user FROM Similarity LEFT JOIN Post ON Similarity.post_id = Post.id WHERE value > ? ORDER BY value DESC"
            manager.cur.execute(sql, (threshold,))
            result = manager.cur.fetchall()
            if len(result) > 0:
                for value, post_id, display_src, user_id in result:
                    print("유사도 : %s%%" % (round(value * 100, 2)))
                    print("포스트ID :", post_id)
                    print("사진 링크 :", display_src)
                    print("userID :", user_id)
            else:
                print("결과가 없습니다")
