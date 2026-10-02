# vvoori-cafe-winter v001 제작 계획

사용자 제공 겨울 장면 명세를 그대로 제작한다. 세부 선택과 전체 제작은 요청에서 승인됨.
기존 이미지 합성 제작 흐름을 독립 장면으로 확장하며 다른 장면과 결과를 보존한다.

- [x] built-in image_gen으로 새로운 공원 RGB와 가구/창테두리 포함 실내 RGBA 생성, 원본/프롬프트 보존 및 알파 검사.
- [x] 브리찌의 새 전용 Scene: 고정 50도 카메라, 셀 명암 차량 6대, 200~350개 눈. 정적 3D 실내/캐시 없음.
- [x] 실제 차도에 투영한 두 차선과 반대 방향 차량, 시야 밖 순환 눈. 주기 480프레임, frame 481=frame 1; 출력은 1~480 전부 렌더.
- [x] 실제 미리보기 검사/보정, 1920x1080 24fps 20초 무음 MP4와 반복 HTML.
- [x] 모든 프레임의 불투명 실내 ROI, 루프 위치/속도, 전체 영상 디코딩, 새 Blender 재개방/렌더 검사.
- [x] 파일 보존 해시 확인, current-state에 결과 추가.

Git 마무리는 이 제작의 자산/원본/결과/기록만 커밋하고 현재 브랜치에 푸시한 뒤,
로컬/추적/원격 해시를 비교한다. 실행 결과는 Git 이력과 대화 완료 보고를 기준으로 한다.

원본 명세: vvoori-cafe-winter-one-shot-prompt.txt. 제작 코드와 보고서는 이 폴더에,
자산은 assets/vvoori-cafe-winter/v001, 출력은 outputs/vvoori-cafe-winter/v001,
원본은 scenes/vvoori-cafe-winter-v001.blend에 저장한다.
