"""바닷속 구조대 다섯 친구: 승인된 20종 캐릭터 제작의 해양 파트.

Builder API만 사용한다. 정면은 -Y, 바닥은 Z=0이며 Blender 실행과 저장은
공통 제작기가 담당한다. 문어의 여덟 팔, 거북 등딱지, 복어의 둥근 가시,
소라게 집게/나선 껍질, 해마 주둥이/말린 꼬리를 각각 실루엣으로 구분한다.
"""

import math


def _palette(b, skin, pale, accent, shell):
    # 얼굴용 공통 재질을 위해 이 모듈의 재질은 캐릭터당 여덟 개로 제한한다.
    return {
        "skin": b.mat("Sea_Skin", skin),
        "pale": b.mat("Sea_SoftAccent", pale),
        "accent": b.mat("Sea_Accent", accent),
        "shell": b.mat("Sea_Shell", shell),
        "orange": b.mat("Sea_RescueOrange", "FA7950"),
        "navy": b.mat("Sea_DeepBlue", "264F6C"),
        "cream": b.mat("Sea_ReflectiveCream", "FFF0CB"),
        "gold": b.mat("Sea_SignalGold", "F5C85C"),
    }


def _vest(b, p, width=.47, y=-.35, z=1.08, height=.44):
    """앞이 열린 두 부력 패널과 반사띠. 몸 뼈를 따라 움직인다."""
    for side in (-1, 1):
        label = "L" if side < 0 else "R"
        x = side * width * .53
        b.ell("VestPanel_" + label, (x, y, z),
              (width * .47, .105, height * .57), p["orange"],
              bone="DEF_Body", segments=28, rings=16)
        b.box("VestReflector_" + label, (x, y - .104, z + .025),
              (width * .68, .033, .065), p["cream"],
              bone="DEF_Body", bevel=.019)
        b.tube("VestShoulder_" + label,
               [(x, .08, z + height * .30),
                (x, -.08, z + height * .59),
                (x, y, z + height * .39)], .049, p["orange"],
               bone="DEF_Body")
    b.box("VestWaistStrap", (0, y - .09, z - height * .23),
          (width * 1.72, .048, .082), p["navy"],
          bone="DEF_Body", bevel=.02)
    b.box("VestBuckle", (0, y - .125, z - height * .23),
          (.13, .038, .10), p["gold"], bone="DEF_Body", bevel=.022)
    b.ell("VestRescueBadge", (-width * .53, y - .13, z + height * .30),
          (.068, .023, .068), p["navy"], bone="DEF_Body")
    b.star("VestBadgeStar", (-width * .53, y - .154, z + height * .30),
           .045, .015, p["cream"], bone="DEF_Body")


def _whistle(b, p, x=.19, y=-.5, z=1.15):
    b.tube("WhistleLanyard", [(x - .05, y + .01, z + .19),
                              (x - .08, y - .035, z + .06),
                              (x, y - .04, z)], .012, p["navy"],
           bone="DEF_Body", sides=8)
    b.box("RescueWhistle", (x + .034, y - .04, z), (.125, .07, .074),
          p["gold"], bone="DEF_Body", bevel=.025)
    b.box("WhistleAirSlot", (x + .055, y - .078, z + .013),
          (.035, .01, .017), p["navy"], bone="DEF_Body", bevel=.004)


def _octopus(b):
    p = _palette(b, "AB8CE1", "E4BDFA", "7862B2", "72CFC8")
    b.ell("OctopusMantle", (0, .025, 1.85), (.65, .51, .61),
          p["skin"], segments=40, rings=24)
    b.ell("OctopusBody", (0, 0, 1.08), (.46, .36, .39),
          p["skin"], bone="DEF_Body", segments=32, rings=20)
    b.ell("MantleHighlight", (-.25, -.407, 2.15), (.13, .025, .095),
          p["pale"], rotation=(0, -.28, 0))
    # 기본 좌우 팔과 다리를 4지로 세고 체인 촉수는 정확히 4개만 추가한다.
    b.limbs(p["skin"], shoe=p["skin"], hand=p["skin"], radius=.115)
    for side in (-1, 1):
        label = "L" if side < 0 else "R"
        outside = [(side * .40, .11, .91),
                   (side * .66, .12, .61),
                   (side * .94, .08, .35),
                   (side * 1.02, -.01, .33),
                   (side * 1.02, -.09, .49)]
        rear = [(side * .18, .28, .85),
                (side * .38, .33, .51),
                (side * .55, .28, .24),
                (side * .65, .14, .20),
                (side * .71, .03, .31)]
        for position, points in (("Outer", outside), ("Rear", rear)):
            chain = b.chain("Tentacle" + position + "_" + label, points)
            b.tube("Tentacle" + position + "_" + label, points,
                   [.126, .118, .097, .071, .032], p["skin"],
                   chain=chain, bone="DEF_Body", sides=12)
            for i, point in enumerate(points[1:-1], 1):
                radius = (.060, .049, .037)[i - 1]
                b.ell("Sucker" + position + label + str(i),
                      (point[0], point[1] - .088, point[2]),
                      (radius, .021, radius), p["pale"],
                      bone=chain[min(i - 1, len(chain) - 1)])
        # 기본 팔다리에도 흡반이 있어 신발 대신 문어 팔로 읽힌다.
        b.ell("ArmSucker_" + label, (side * .864, -.243, .865),
              (.060, .023, .073), p["pale"], bone="DEF_Hand." + label)
        b.ell("FootSucker_" + label, (side * .25, -.145, .22),
              (.06, .025, .06), p["pale"], bone="DEF_Foot." + label)
    _vest(b, p, width=.44, y=-.35, z=1.10, height=.40)
    _whistle(b, p, x=.22, y=-.50, z=1.16)
    # 구조대 작은 선원 모자: 문어 머리의 큰 둥근 윤곽을 유지한다.
    b.ell("SailorCapCrown", (0, .005, 2.42), (.25, .22, .105),
          p["cream"], segments=28, rings=16)
    b.ell("SailorCapBand", (0, -.01, 2.375), (.277, .235, .048),
          p["navy"])
    b.star("CapRescueStar", (0, -.243, 2.414), .077, .020, p["gold"])
    b.face(center=(0, -.50, 1.88), spread=.235, scale=1.06)


def _turtle(b):
    p = _palette(b, "83CFA2", "CEECC0", "417F74", "BA9260")
    # 등딱지는 머리 뒤쪽(+Y)에 놓고 몸보다 크게 만들어 옆 윤곽에 드러낸다.
    b.ell("TurtleShell", (0, .29, 1.15), (.65, .35, .70), p["accent"],
          bone="DEF_Body", segments=36, rings=24)
    b.ell("ShellAmberCenter", (0, .545, 1.16), (.53, .15, .58), p["shell"],
          bone="DEF_Body", segments=28, rings=20)
    b.ring("ShellRim", (0, .245, 1.15), .607, .064, p["pale"],
           bone="DEF_Body")
    # 뒤에서도 종이 식별되도록 등딱지의 육각 판과 바깥 판을 만든다.
    vertices = []
    for i in range(6):
        angle = math.pi / 6 + i * math.pi / 3
        vertices.append((.27 * math.cos(angle), .704,
                         1.16 + .30 * math.sin(angle)))
    b.tube("ShellCentralScute", vertices + [vertices[0]], .024,
           p["accent"], bone="DEF_Body")
    for i, point in enumerate(vertices):
        angle = math.pi / 6 + i * math.pi / 3
        b.tube("ShellScuteSeam" + str(i),
               [point, (.46 * math.cos(angle), .63,
                        1.16 + .52 * math.sin(angle))], .022,
               p["accent"], bone="DEF_Body")
    b.ell("TurtleBody", (0, -.065, 1.06), (.43, .36, .43), p["skin"],
          bone="DEF_Body", segments=28, rings=18)
    b.ell("TurtleNeck", (0, -.015, 1.49), (.235, .225, .25), p["skin"],
          bone="DEF_Head")
    b.ell("TurtleHead", (0, -.025, 1.94), (.545, .44, .475), p["skin"],
          segments=40, rings=24)
    b.ell("TurtleMuzzle", (0, -.42, 1.75), (.285, .075, .145), p["pale"],
          segments=28, rings=16)
    b.limbs(p["skin"], shoe=p["skin"], hand=p["skin"], style="fins")
    _vest(b, p, width=.425, y=-.395, z=1.11, height=.44)
    b.face(center=(0, -.515, 1.98), spread=.205, scale=.99)
    # 왼손에 손잡이 없는 구명환. 손 위치를 기준으로 고정한다.
    buoy_center = (-.88, -.295, .86)
    b.ring("TurtleLifebuoy", buoy_center, .205, .068, p["cream"],
           bone="DEF_Hand.L")
    for i in range(4):
        angle = i * math.pi / 2
        b.ell("LifebuoyOrangeBand" + str(i),
              (buoy_center[0] + .203 * math.cos(angle), -.298,
               buoy_center[2] + .203 * math.sin(angle)),
              (.077, .073, .077), p["orange"], bone="DEF_Hand.L")
    b.tube("BuoyRope", [(-.99, -.25, .72), (-.99, -.20, .52),
                       (-.78, -.21, .49), (-.76, -.25, .67)],
           .018, p["shell"], bone="DEF_Hand.L", sides=8)
    _whistle(b, p, x=.22, y=-.55, z=1.17)


def _puffer(b):
    p = _palette(b, "F5CF66", "FFF0B8", "DF9C46", "71CED0")
    b.ell("PufferRoundBody", (0, 0, 1.65), (.705, .52, .715),
          p["skin"], segments=44, rings=28)
    b.ell("PufferBelly", (0, -.45, 1.43), (.45, .092, .36),
          p["pale"], segments=32, rings=20)
    b.ell("PufferLowerBody", (0, .01, 1.05), (.435, .345, .29),
          p["skin"], bone="DEF_Body", segments=28, rings=18)
    # 가장자리에 짧고 뭉툭한 가시. 얼굴 앞 중앙은 깨끗이 비운다.
    for i, degrees in enumerate((-32, -2, 28, 56, 82, 109, 137, 166, 196, 213)):
        angle = math.radians(degrees)
        x, z = .68 * math.cos(angle), 1.65 + .69 * math.sin(angle)
        direction = (math.cos(angle), math.sin(angle))
        b.cone("PufferSilhouetteSpine" + str(i), (x, .015, z),
               (x + .145 * direction[0], .015, z + .145 * direction[1]),
               .063, p["accent"], radius_end=.018)
        b.ell("SpineRoundedTip" + str(i),
              (x + .145 * direction[0], .015, z + .145 * direction[1]),
              (.022, .024, .022), p["accent"], segments=12, rings=8)
    for side in (-1, 1):
        for i, (x, z) in enumerate(((.44, 2.02), (.53, 1.74), (.41, 2.16))):
            b.cone("PufferFaceSpine" + str(side) + str(i),
                   (side * x, -.32, z), (side * (x + .035), -.42, z + .057),
                   .045, p["accent"], radius_end=.013)
    b.limbs(p["shell"], shoe=p["shell"], hand=p["shell"],
            style="fins", omit_legs=True, radius=.093)
    tail_points = [(0, .35, 1.25), (0, .65, 1.25), (0, .86, 1.31)]
    tail_chain = b.chain("PufferTail", tail_points)
    b.tube("PufferTailStem", tail_points, [.14, .11, .07], p["skin"],
           bone="DEF_Body", chain=tail_chain)
    for side in (-1, 1):
        b.ell("PufferTailFan" + str(side), (side * .145, .88, 1.30),
              (.205, .095, .235), p["shell"], bone=tail_chain[-1],
              rotation=(0, side * -.48, 0), segments=28, rings=16)
    _vest(b, p, width=.545, y=-.405, z=1.10, height=.44)
    b.face(center=(0, -.565, 1.81), spread=.23, scale=1.0)
    # 수면 신호용 작은 비콘을 둥근 몸 위에 둔다.
    b.ell("BeaconBase", (0, .01, 2.36), (.12, .105, .042), p["navy"])
    b.ell("BeaconLight", (0, .01, 2.425), (.078, .075, .09), p["shell"])
    b.ell("BeaconGlint", (-.025, -.053, 2.456), (.018, .012, .03), p["cream"])
    _whistle(b, p, x=.27, y=-.55, z=1.16)


def _hermit(b):
    p = _palette(b, "EB9D83", "FFD3B0", "BB715F", "76C6BD")
    b.ell("HermitSpiralShell", (.29, .32, 1.45), (.74, .43, .77),
          p["shell"], bone="DEF_Body", segments=40, rings=26)
    spiral = []
    for i in range(89):
        fraction = i / 88
        angle = math.pi * .1 + fraction * math.pi * 4.7
        radius = .63 * (1 - fraction) + .034
        dx = radius * math.cos(angle)
        dz = radius * math.sin(angle)
        surface = math.sqrt(max(.04, 1 - (dx / .74) ** 2 - (dz / .77) ** 2))
        spiral.append((.29 + dx, .32 - .43 * surface - .022, 1.45 + dz))
    b.tube("RaisedShellSpiral", spiral, .046, p["cream"],
           bone="DEF_Body", sides=10)
    b.ell("ShellApex", (.77, .31, 1.95), (.15, .17, .22), p["shell"],
          bone="DEF_Body", rotation=(0, .55, 0))
    b.ell("HermitBody", (0, -.13, 1.05), (.42, .34, .37), p["skin"],
          bone="DEF_Body", segments=30, rings=18)
    b.ell("HermitHead", (-.065, -.22, 1.84), (.52, .43, .425), p["skin"],
          segments=40, rings=24)
    b.ell("HermitJaw", (-.065, -.51, 1.68), (.31, .15, .13), p["pale"])
    b.limbs(p["skin"], shoe=p["accent"], omit_arms=True, radius=.087)
    for side in (-1, 1):
        label = "L" if side < 0 else "R"
        b.tube("CrabUpperArm" + label,
               [(side * .52, -.02, 1.23), (side * .73, -.07, 1.04)],
               [.083, .09], p["skin"], bone="DEF_UpperArm." + label)
        b.tube("CrabForearm" + label,
               [(side * .73, -.07, 1.04), (side * .87, -.13, .84)],
               [.09, .105], p["skin"], bone="DEF_Forearm." + label)
        hand = "DEF_Hand." + label
        b.ell("LargeClawPalm" + label, (side * .89, -.17, .87),
              (.205, .14, .22), p["orange"], bone=hand,
              rotation=(0, side * -.17, 0), segments=30, rings=18)
        b.tube("ClawOuterFinger" + label,
               [(side * 1.015, -.17, .93), (side * 1.08, -.17, 1.09),
                (side * 1.035, -.17, 1.23), (side * .94, -.17, 1.22)],
               [.085, .081, .055, .025], p["skin"], bone=hand)
        b.tube("ClawInnerFinger" + label,
               [(side * .79, -.17, .93), (side * .775, -.17, 1.08),
                (side * .825, -.17, 1.145)], [.09, .065, .029],
               p["skin"], bone=hand)
        b.ell("ClawPalmHighlight" + label, (side * .91, -.294, .9),
              (.095, .018, .08), p["pale"], bone=hand)
        leg = [(side * .35, .13, .97), (side * .57, .17, .67),
               (side * .70, .10, .35), (side * .76, -.025, .20)]
        chain = b.chain("HermitSideLeg" + label, leg)
        b.tube("HermitSideLeg" + label, leg, [.079, .068, .057, .031],
               p["accent"], chain=chain, bone="DEF_Body")
        feeler = [(side * .30 - .065, -.02, 2.12),
                  (side * .35 - .065, -.05, 2.32),
                  (side * .48 - .065, -.055, 2.39)]
        antenna = b.chain("HermitFeeler" + label, feeler, parent="DEF_Head")
        b.tube("HermitFeeler" + label, feeler, [.027, .022, .018],
               p["accent"], chain=antenna, sides=8)
        b.ell("FeelerTip" + label, feeler[-1], (.045, .04, .045),
              p["gold"], bone=antenna[-1], segments=16, rings=10)
    _vest(b, p, width=.40, y=-.435, z=1.11, height=.40)
    b.face(center=(-.065, -.668, 1.91), spread=.205, scale=.99)
    # 등껍질 위의 작은 구조대 표식도 몸을 따라간다.
    b.star("ShellRescueStar", (.84, .055, 1.83), .12, .032, p["gold"],
           bone="DEF_Body", rotation=(0, -.12, 0))
    _whistle(b, p, x=.19, y=-.585, z=1.15)


def _seahorse(b):
    p = _palette(b, "75CFC4", "D3EEE0", "5998A0", "B3A3E1")
    b.ell("SeahorseChest", (0, .035, 1.21), (.355, .30, .46),
          p["skin"], bone="DEF_Body", segments=36, rings=22)
    b.tube("SeahorseCurvedNeck",
           [(0, .04, 1.27), (.07, .025, 1.52),
            (-.09, .01, 1.70), (-.13, .015, 1.89)],
           [.25, .23, .23, .27], p["skin"], sides=16)
    b.ell("SeahorseHead", (-.13, .015, 1.98), (.375, .33, .43),
          p["skin"], segments=40, rings=24)
    # 긴 주둥이를 오른쪽 앞으로 기울여 정면에서도 길이가 드러나게 한다.
    b.tube("LongSeahorseSnout",
           [(.09, -.19, 1.91), (.29, -.30, 1.85),
            (.50, -.385, 1.855), (.64, -.40, 1.90)],
           [.155, .133, .108, .10], p["skin"], sides=16)
    b.ell("SnoutRim", (.64, -.40, 1.90), (.115, .108, .105), p["pale"])
    b.ell("SnoutOpening", (.67, -.489, 1.906), (.059, .016, .058), p["accent"])
    b.limbs(p["shell"], hand=p["shell"], style="fins", omit_legs=True,
            radius=.073)
    tail = [(0, .035, .87), (.17, .025, .66), (.31, .015, .42),
            (.30, -.015, .255), (.13, -.035, .165),
            (-.075, -.055, .20), (-.17, -.07, .345),
            (-.10, -.08, .465), (.045, -.085, .465), (.105, -.085, .37)]
    chain = b.chain("SeahorseCurlTail", tail)
    b.tube("SeahorseCurlTail", tail,
           [.165, .15, .13, .115, .087, .074, .06, .048, .037, .018],
           p["skin"], chain=chain, bone="DEF_Body", sides=14)
    # 꼬리 마디: 체인 뼈를 직접 따라가며 말린 끝의 빈 공간을 가리지 않는다.
    for i, point in enumerate(tail[1:-2], 1):
        radii = (.135, .117, .101, .076, .061, .050, .041)
        b.ell("TailBellySegment" + str(i),
              (point[0], point[1] - radii[i - 1] * .84, point[2]),
              (radii[i - 1] * .70, .024, .04), p["pale"],
              bone=chain[min(i - 1, len(chain) - 1)], segments=16, rings=10)
    dorsal = b.extra("SeahorseDorsalFin", (.24, .18, 1.29),
                     (.52, .26, 1.43), parent="DEF_Body")
    fin_vertices = [(.245, .14, 1.09), (.27, .16, 1.53),
                    (.51, .19, 1.63), (.63, .21, 1.50),
                    (.60, .20, 1.31), (.48, .18, 1.15),
                    (.39, .19, 1.36)]
    # 얇은 입체 막으로 만들어 Unity의 뒷면 제거에서도 양쪽 면을 유지한다.
    triangles = [(6, 0, 1), (6, 1, 2), (6, 2, 3), (6, 3, 4),
                 (6, 4, 5), (6, 5, 0)]
    fin_front = [(x, y - .018, z) for x, y, z in fin_vertices]
    fin_back = [(x, y + .018, z) for x, y, z in fin_vertices]
    fin_faces = [tuple(reversed(face)) for face in triangles]
    fin_faces.extend(tuple(index + 7 for index in face) for face in triangles)
    fin_faces.extend((i, (i + 1) % 6, (i + 1) % 6 + 7, i + 7)
                     for i in range(6))
    b.mesh("SeahorseDorsalFan", fin_front + fin_back, fin_faces,
           p["shell"], bone=dorsal)
    for i in (2, 3, 4, 5):
        b.tube("DorsalFinRay" + str(i), [fin_vertices[0], fin_vertices[i]],
               .014, p["pale"], bone=dorsal, sides=8)
    for i, (x, z, height) in enumerate(((-.39, 2.20, .12),
                                      (-.29, 2.33, .15),
                                      (-.14, 2.385, .15),
                                      (.015, 2.34, .12))):
        crown = b.extra("SeahorseCoronet" + str(i), (x, .065, z),
                        (x, .10, z + height), parent="DEF_Head")
        b.cone("SeahorseCoronet" + str(i), (x, .065, z),
               (x, .10, z + height), .062, p["shell"],
               bone=crown, radius_end=.025)
        b.ell("CoronetRoundTip" + str(i), (x, .10, z + height),
              (.032, .032, .032), p["shell"], bone=crown,
              segments=16, rings=10)
    _vest(b, p, width=.33, y=-.267, z=1.22, height=.42)
    b.face(center=(-.15, -.335, 2.075), spread=.165, scale=.78)
    _whistle(b, p, x=.16, y=-.42, z=1.24)


BUILDERS = {
    "OctoOctopus": _octopus,
    "TutuTurtle": _turtle,
    "BobaPuffer": _puffer,
    "KikiHermit": _hermit,
    "HaniSeahorse": _seahorse,
}


def build(b, key):
    """선택한 구조대 캐릭터 한 명을 공통 Builder에 생성한다."""
    try:
        builder = BUILDERS[key]
    except KeyError:
        raise ValueError("Unknown sea character: " + str(key)) from None
    builder(b)
