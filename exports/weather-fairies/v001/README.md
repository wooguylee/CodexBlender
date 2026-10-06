# 오늘의 날씨 요정들 — 개별 모델 / Unity 6 URP

몽실(Mongsil), 해롱(Haerong), 또르(Ttorr), 송송(Songsong), 솔솔(Solsol)을 각각 독립 파일로 제공한다.

## 가장 쉬운 Unity 사용법

1. Unity **6.3 LTS + URP** 프로젝트를 연다. 검증 버전은 6000.3.25f1 / URP 17.3.0이다.
2. `WeatherFairies-Unity6-URP-v001.unitypackage`를 열거나 **Assets → Import Package → Custom Package**로 가져온다.
3. `Assets/WeatherFairies/Prefabs/`의 원하는 캐릭터를 Scene으로 드래그한다. 뼈대·재질·Animator·표정 조절 컴포넌트가 연결되어 있다.
4. 전체 시안은 `Assets/WeatherFairies/Scenes/WeatherFairiesShowcase.unity`를 연다. Play를 누르면 약 16초 리깅 시연이 재생된다.

`unity/Assets/`의 두 전용 폴더를 프로젝트의 `Assets/`에 복사하는 방법도 있다. `.meta` 파일을 함께 복사해야 재질·Prefab·클립 연결 GUID가 유지된다. Blender `.blend`는 Unity 프로젝트 바깥에서 편집용으로 보관하면 된다.

## 제공 파일

| 캐릭터 | 편집용 Blender | Unity 원본 FBX | Prefab | 뼈 | 표정 BlendShape |
|---|---|---|---|---:|---:|
| 몽실 | `blender/Mongsil.blend` | `unity/Assets/WeatherFairies/Models/Mongsil.fbx` | `Mongsil.prefab` | 24 | 9 |
| 해롱 | `blender/Haerong.blend` | `unity/Assets/WeatherFairies/Models/Haerong.fbx` | `Haerong.prefab` | 35 | 11 |
| 또르 | `blender/Ttorr.blend` | `unity/Assets/WeatherFairies/Models/Ttorr.fbx` | `Ttorr.prefab` | 23 | 12 |
| 송송 | `blender/Songsong.blend` | `unity/Assets/WeatherFairies/Models/Songsong.fbx` | `Songsong.prefab` | 29 | 10 |
| 솔솔 | `blender/Solsol.blend` | `unity/Assets/WeatherFairies/Models/Solsol.fbx` | `Solsol.prefab` | 31 | 11 |

- `.blend`: 캐릭터 하나와 Armature 하나. 원래 IK·driver·표정·특수 조절·컨트롤 모양을 유지한다. 카메라·배경·다른 캐릭터는 포함하지 않는다. 열면 몸 컨트롤이 Pose Mode로 선택된다.
- `.fbx`: 실제 스킨 가중치, 뼈대, 표정 모양과 베이크한 애니메이션을 포함한다. 다른 프로젝트에서 FBX만 사용한다면 **Rig → Generic / Create From This Model**, **Import BlendShapes**를 켜고 URP 재질을 연결한다.
- `.unitypackage`: 다섯 모델, 32개 URP 재질, 다섯 Prefab과 Animator Controller, 표정 C# 컴포넌트, 시연 Scene과 조명/톤매핑 설정을 포함한다. URP 패키지 자체를 설치하거나 기존 렌더 파이프라인/Build Settings를 변경하지 않는다.
- `WeatherFairies-Models-v001.zip`: Blender 5개, 원본 FBX 5개, Unity 패키지, 이 설명과 미리보기를 묶은 전달용 압축 파일.

## 애니메이션과 표정

각 Animator에 `RigDemo`, `Idle`, `HandsIK`, `Expressions`, `Weather`, `Special` 6개 클립이 연결되어 있다. 기본 상태는 `RigDemo`이며 처음부터 한 번 재생한다. `Idle`은 기본 자세 반복이다. 나머지는 기존 리깅 시연을 구간별로 나눈 것으로 보행·달리기 전용 동작은 아니다.

```csharp
// Prefab 루트의 Animator에서 원하는 클립 상태를 재생한다.
GetComponent<Animator>().Play("Special", 0, 0f);
```

수동 표정은 Prefab 루트의 **Weather Fairy Expressions → Manual Expressions**를 켜서 조절한다. `Awake`, `Blink`, `Smile`, `Surprise`는 0–1이며 또르의 `Tip Sway`는 −1–1이다. 이 모드는 얼굴 BlendShape에 한해 Animator 값을 덮어쓴다. 원래 표정 애니메이션으로 돌아가려면 Manual Expressions를 끈다. 몽실·솔솔의 감은 눈과 송송의 윙크를 열 때 Awake를 사용한다.

Blender의 IK 제약과 driver 프로그램은 FBX/Unity에서 그대로 실행되지 않는다. Unity에는 프레임별 뼈 변환·표정 값을 베이크했고, 직접 바꿀 수 있는 표정 컴포넌트를 함께 제공한다. 손발 IK 목표를 실시간 조작하는 Unity 전용 IK 솔버는 포함하지 않는다. Unity에서 움직임을 추가하려면 이 Generic 뼈대를 Animate하거나 Blender 개별 원본에서 작업한 뒤 다시 베이크한다.

## 좌표·재질·성능

- 발의 가장 낮은 점이 원점 높이 0에 오도록 정리했다. X가 가로, Unity Y가 위쪽이며 캐릭터 정면은 **−Z**다. 단위는 1 Blender 단위 = 1 Unity 단위다.
- 원형을 유지한 기본 높이는 몽실 약 2.70, 해롱 3.22, 또르 2.56, 송송 3.26, 솔솔 3.38 Unity 단위다. 게임 크기에 맞춰 Prefab 루트 전체를 균일하게 줄인다.
- Blender는 볼륨 보존 스키닝, Unity는 기본 선형 스키닝을 사용한다. 극단적으로 비튼 포즈와 조명·색 관리 결과는 두 프로그램에서 차이가 날 수 있다. URP 재질은 원본 색·거칠기를 옮긴 것이다.
- 고해상도 원본을 보존한 모델이다. Unity 정점 수는 몽실 64,308 / 해롱 46,565 / 또르 37,477 / 송송 64,838 / 솔솔 131,964이며 메시도 소품/표정별로 나뉜다. LOD·메시 병합·모바일 최적화는 적용하지 않았다.
- Humanoid 자동 리타게팅이 아닌 **Generic 리그**다. Built-in/HDRP에서는 재질을 해당 파이프라인으로 바꿔야 한다.

## 검증

5개 Blender 파일 독립 재개방, 캐릭터별 단일 Armature, 스키닝·표정 driver 124개, 외부 링크 없음 확인. Unity에서 142개 뼈 / 149개 SkinnedMeshRenderer / 53개 BlendShape / 30개 클립을 확인했다. 발 높이 오차는 0.000002 단위 미만이다.

Unity에서 실제 메시 변형, 표정 애니메이션 값의 0→100 변화, 런타임 Play Mode에서 다섯 Animator와 놀란 표정 재생을 확인했다. 기본/놀람/특수 동작을 Unity 카메라로 렌더해 직접 확인했다. 초안의 다각형 가져오기 경고를 수정한 후 최종 재가져오기·컴파일·검증의 콘솔 오류와 경고는 0개였다. 기존 제작 원본은 보존했다.

검증 기록은 저장소의 `outputs/weather-unity/v001/`, 제작 코드는 `workflows/weather-unity/`에 있다. 원본 파일 SHA-256과 배포 묶음 검사는 `delivery-verification.json`에 기록한다.

참고: [Unity 6.3 Generic Rig 설정](https://docs.unity3d.com/6000.3/Documentation/Manual/FBXImporter-Rig.html), [Unity BlendShape 사용](https://docs.unity.com/en-us/engine/6000.6/manual/animation-section/animation-mecanim/animation-clips/animation-editor-guide/blend-shapes).
