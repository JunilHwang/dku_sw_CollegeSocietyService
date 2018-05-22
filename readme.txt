18.05.22

1. windows용 apache 구동은 python 2.7 혹은 python 3.4가 사용할 수 있는 최신버전입니다.

2. 유니코드 해석 문제로 python 3 사용을 권장합니다.
   2버전 사용시에는 스크립트 내 한글 사용을 위해
   #-*- coding: utf-8 -*-을 달고,
   프로그램 진입부에 다음 세 줄의 코드를 추가해줍니다.

   import sys
   reload(sys)
   sys.setdefaultencoding('utf-8')

   위 코드는 문자열 기본 인코딩을 'utf-8'로 변경해주며, python2에서만 작동합니다.
   python3에서는 에러메시지가 뜰뿐더러 애초에 사용할 필요가 없습니다.

3. apache에서 구동시 config.py에서 DEBUG=False로 설정,
   wsgi파일에서 path를 확인하시길 바랍니다.

<Routing>
사용자등록, 전체 목록 : /member
사용자 정보 변경, 삭제 : /member/<사용자 idx>
카테고리 : /CategoryList
게시글 목록, 추가: /board/<category_id>
게시글 수정, 삭제: /board/<category_id>/<게시글 idx>
댓글 목록, 추가: /board/<게시글 idx>/comments
댓글 수정, 삭제: /comments/<댓글 idx>
교수 목록: /professor
교수 개별: /professor/<교수 idx>