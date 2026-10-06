# Storybook cast 제작 계약

기존 날씨 요정의 검증된 Blender→Generic FBX→Unity URP 제작 흐름을 4개 주제/20개 신규 캐릭터로 확장한다. 사용자 요청으로 실제 제작/리깅/동작/개별 저장/Unity 검증이 승인되었다. 별도 설치나 외부 자산은 없다. 기존 파일은 보존한다.

모델 함수는 `build(b, key)`다. 각 theme 모듈만 작성하며 Blender/Unity 연결, Scene 생성, 파일 저장, Git 명령은 root가 수행한다. 모델러는 `b`의 아래 API만 호출한다. 직접 bpy 변경은 하지 않는다. 좌표: X 좌우, Y 깊이, Z 위, 정면 −Y. 신발 바닥 0. 머리 중심 기본 (0,0,1.75), 몸 중심 (0,0,1.02). 전체 폭은 2.3 이하, 귀 포함 높이 3.1 이하 권장.

## Builder API

- `b.mat(name, hex_color, roughness=.48, metallic=0)` → 재질 이름 문자열. hex는 `#` 없는 6자리. 캐릭터별 12개 이하 권장.
- `b.ell(name, center, scale, material, bone='DEF_Head', rotation=(0,0,0), segments=20, rings=12)` → Part. 회전은 radian XYZ. scale은 반지름이다. 분리된 파트들을 최종 하나의 스킨 메시로 합친다.
- `b.box(name, center, size, material, bone='DEF_Head', bevel=.08, rotation=(0,0,0))` → Part. size는 전체 폭/깊이/높이다.
- `b.tube(name, points, radius, material, bone='DEF_Head', chain=None, sides=10)` → Part. points는 경로 좌표 리스트. radius는 숫자 또는 각 points와 같은 길이의 반지름 리스트. 곡선 보간한다. chain이 주어지면 해당 뼈에 경로 기준으로 가중치를 배분한다.
- `b.cone(name, start, end, radius, material, bone='DEF_Head', radius_end=0.01, sides=16)` → Part.
- `b.star(name, center, radius, depth, material, bone='DEF_Head', points=5, rotation=(0,0,0))` → Part. 별 면은 XZ, 두께는 Y. 꼭짓점은 위쪽. 둥근 bevel 포함.
- `b.ring(name, center, major, minor, material, bone='DEF_Head', rotation=(0,0,0))` → Part. 기본 링 평면은 XZ. 회전 radian XYZ.
- `b.mesh(name, vertices, faces, material, bone='DEF_Head')` → Part. 사용자 다각형은 삼각/사각 위주, 최종 export에서 n-gon을 정리한다.
- `b.extra(name, head, tail, parent='DEF_Head')` → 뼈 이름 `DEF_<name>`. 기본 머리/몸 외에 귀/안테나 등 추가 뼈. 자동 부가 흔들림 애니메이션이 포함된다.
- `b.chain(name, points, parent='DEF_Body')` → 뼈 이름 리스트. 예: tail. 각 뼈에 기본 흔들림이 추가된다.
- `b.limbs(skin, shoe=None, hand=None, style='standard', radius=.105, omit_legs=False, omit_arms=False)` 기본 짧은 손발 생성. style='fins'이면 수영용 지느러미 표현. 걷기/달리기/앉기는 동일 리그를 사용하며 물고기/해마는 수영으로 표현한다.
- `b.face(center=(0,-.55,1.75), spread=.22, scale=1., eye_color=None, blush=True)` 눈/빛반사/홍조/미소를 만들고 Blink·Smile·Surprise Shape Key를 추가한다. 중심 Y는 머리 표면보다 0.02 앞으로. 부리/주둥이를 추가할 때 입을 가리지 않도록 한다.

기본 뼈: `CTRL_Root`, `CTRL_Body`, `CTRL_Head`, `CTRL_Face`, `DEF_Body`, `DEF_Head`, `DEF_UpperArm.L/R`, `DEF_Forearm.L/R`, `DEF_Hand.L/R`, `DEF_Thigh.L/R`, `DEF_Shin.L/R`, `DEF_Foot.L/R`, `CTRL_Hand.L/R`, `CTRL_Foot.L/R`.

팔 rest points: L [(-.57,0,1.25),(-.77,-.06,1.03),(-.87,-.13,.84)], R는 x 양수. 다리: L [(-.25,0,.68),(-.25,-.08,.44),(-.25,0,.18)], R는 x 양수. 손에 소품을 붙일 때 `DEF_Hand.L/R` 사용. 뼈 좌표는 변경하지 않는다. 몸은 DEF_Body, 머리/얼굴은 DEF_Head. 통짜 형태는 DEF_Body를 주로 사용해도 된다.

## 분담 키

- `theme_forest.py`: PipiRabbit(씩씩한 토끼 집배원), DodoBear(느긋한 곰 우체국장), ToriSquirrel(꼼꼼한 다람쥐 분류원), BibiOwl(길 잃는 아기 부엉이), MoriHedgehog(우표 수집 고슴도치).
- `theme_space.py`: PokoAlien(덜렁 외계인), BoltRobot(네모 로봇), LunaRabbit(달토끼), TwinkleStar(별 생물), PingoPenguin(우주 길잡이 펭귄).
- `theme_sea.py`: OctoOctopus(문어), TutuTurtle(거북이), BobaPuffer(복어), KikiHermit(소라게), HaniSeahorse(해마).
- root의 `theme_dessert.py`: PuruPudding, MomoMochi, PanBread, RoniMacaron, ShushuPuff.

각 디자인은 이름만 다른 색상 변형이 아니라 종/재료와 직업 소품으로 분명히 구분한다. 특징을 몸/얼굴 뒤에 가리지 않는다. 1캐릭터 10k–25k 정점 목표, 지나친 상세 대신 좋은 실루엣과 얼굴 비례를 우선한다.
